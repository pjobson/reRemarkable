#!usr/bin/python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
gi.require_version('WebKit2', '4.1')

from bs4 import BeautifulSoup
from gi.repository import Gdk, GLib, Gtk, GtkSource, Pango, WebKit2
from locale import gettext as _
from urllib.request import urlopen
import markdown
import os
import sys
import pdfkit_local as pdfkit
import re, subprocess, datetime, os, webbrowser, _thread, sys, locale
import tempfile
import traceback
import styles
import unicodedata
import warnings
from findBar import FindBar
from SettingsManager import SettingsManager
from MarkdownFormatter import MarkdownFormatter
from FileManager import FileManager
from StyleManager import StyleManager
from LayoutManager import LayoutManager
from RecentFilesManager import RecentFilesManager
from ExportManager import ExportManager


import logging
logger = logging.getLogger('reremarkable')

# Ignore warnings re. scroll handler (temp. fix) && starting GTK warning
warnings.filterwarnings("ignore", ".*has no handler with id.*")

from reremarkable_lib import Window, reremarkableconfig
from AboutReRemarkableDialog import AboutReRemarkableDialog
from EmojiPickerDialog import EmojiPickerDialog

# Import version from centralized version file
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from version import __version__ as app_version

class RemarkableWindow(Window):
    __gtype_name__ = "RemarkableWindow"
    
    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(RemarkableWindow, self).finish_initializing(builder)

        self.AboutDialog = AboutReRemarkableDialog
        self.emoji_picker = None

        self.settings = Gtk.Settings.get_default()

        self.homeDir = os.environ['HOME']
        self.media_path = reremarkableconfig.get_data_path() + os.path.sep + "media" + os.path.sep

        # Initialize settings manager
        self.settings_manager = SettingsManager(self.homeDir)
        self.settings_manager.check_settings()
        
        # Initialize markdown formatter (will be set after text_buffer is created)
        self.markdown_formatter = None
        # Initialize file manager (will be set after text_buffer is created)
        self.file_manager = None
        # Initialize style manager
        self.style_manager = None
        # Initialize layout manager
        self.layout_manager = None

        # HTML footer with scripts for live preview
        self.default_html_end = '<script src="' + self.media_path + 'highlight.min.js"></script><script>hljs.initHighlightingOnLoad();</script><script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.2/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script><script type="text/javascript">MathJax.Hub.Config({"showProcessingMessages" : false,"messageStyle" : "none","tex2jax": { inlineMath: [ [ "$", "$" ] ] }});</script></body></html>'
        
        # Markdown extensions (used by live preview and other features)
        self.default_extensions = ['markdown.extensions.extra','markdown.extensions.toc', 'markdown.extensions.smarty', 'markdown_extensions.extensions.urlize', 'markdown_extensions.extensions.Highlighting', 'markdown_extensions.extensions.Strikethrough', 'markdown_extensions.extensions.markdown_checklist', 'markdown_extensions.extensions.superscript', 'markdown_extensions.extensions.subscript', 'markdown_extensions.extensions.mathjax']
        self.safe_extensions = ['markdown.extensions.extra']
        self.pdf_error_warning = False
        
        # Initialize recent files manager
        self.recent_files_manager = RecentFilesManager(max_recent_files=10)

        self.window = self.builder.get_object("reremarkable_window")
        self.window.connect("delete-event", self.window_delete_event)
        self.window.connect("destroy", self.quit_requested)

        self.text_buffer = GtkSource.Buffer()
        self.text_view = GtkSource.View.new_with_buffer(self.text_buffer)
        self.text_view.set_show_line_numbers(True)
        self.text_view.set_auto_indent(True)
        
        # Force the SourceView to use a SourceBuffer and not a TextBuffer
        self.lang_manager = GtkSource.LanguageManager()
        self.text_buffer.set_language(self.lang_manager.get_language('markdown'))
        self.text_buffer.set_highlight_matching_brackets(True)
        
        self.undo_manager = self.text_buffer.get_undo_manager()
        self.undo_manager.connect("can-undo-changed", self.can_undo_changed)
        self.undo_manager.connect("can-redo-changed", self.can_redo_changed)

        self.text_buffer.connect("changed", self.on_text_view_changed)
        self.text_view.set_buffer(self.text_buffer)
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.text_view.connect('key-press-event', self.cursor_ctrl_arrow_rtl_fix)
        
        # Initialize markdown formatter with the text buffer
        self.markdown_formatter = MarkdownFormatter(self.text_buffer)
        
        # Initialize file manager with window and text buffer
        self.file_manager = FileManager(self.window, self.text_buffer)
        self.file_manager.set_recent_files_callback(self.recent_files_manager.add_recent_file)
        
        # Initialize export manager
        self.export_manager = ExportManager(self.style_manager, self.file_manager, self.media_path)
        self.export_manager.set_window_sensitivity_callback(self.window.set_sensitive)
        
        # Initialize style manager
        self.style_manager = StyleManager(self.settings_manager, self.media_path)
        self.style_manager.add_style_change_callback(self.on_style_changed)
        
        # Initialize export manager (will be set up after file_manager is available)
        self.export_manager = None
        
        # Initialize layout manager (will be set up after UI components are created)
        self.layout_manager = None

        self.live_preview = WebKit2.WebView()

        self.scrolledwindow_text_view = Gtk.ScrolledWindow()
        self.scrolledwindow_text_view.add(self.text_view)
        self.scrolledwindow_live_preview = Gtk.ScrolledWindow()
        self.scrolledwindow_live_preview.add(self.live_preview)

        self.paned = self.builder.get_object("paned")
        self.paned.set_position(self.window.get_size()[0]/2)
        self.paned.pack1(self.scrolledwindow_text_view)
        self.paned.pack2(self.scrolledwindow_live_preview)

        self.toolbar = self.builder.get_object("toolbar")
        self.toolbutton_undo = self.builder.get_object("toolbutton_undo")
        self.toolbutton_undo.set_sensitive(False)
        self.toolbutton_redo = self.builder.get_object("toolbutton_redo")
        self.toolbutton_redo.set_sensitive(False)

        self.statusbar = self.builder.get_object("statusbar")
        self.context_id = self.statusbar.get_context_id("main status bar")

        # Initialize layout manager now that UI components are available
        self.layout_manager = LayoutManager(self.window, self.settings_manager)
        self.layout_manager.set_ui_components(
            self.paned, self.live_preview, self.scrolledwindow_text_view,
            self.scrolledwindow_live_preview, self.text_view, self.toolbar,
            self.statusbar, self.builder
        )

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.update_status_bar(self)
        self.update_live_preview(self)

        text = ""

        self.wrap_box = self.builder.get_object("wrap_box")
        self.find_entry = self.builder.get_object("find_entry")
        self.replace_entry = self.builder.get_object("replace_entry")
        match_case = self.builder.get_object("match_case")
        whole_word = self.builder.get_object("whole_word")
        regex = self.builder.get_object("regex")
        findbar = self.builder.get_object('findbar')
        self.findbar = FindBar(findbar, self.wrap_box, self.find_entry, self.replace_entry,
                               match_case, whole_word, regex)
        self.findbar.set_text_view(self.text_view)

        # Check if filename has been specified in terminal command
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            if not self.file_manager.load_file(file_path, self.window.set_title):
                print(f"{file_path} does not exist, creating it")
                self.file_manager.set_current_file_path(file_path)

        self.update_status_bar(self)
        self.update_live_preview(self)

        # Check if an updated version of application exists [removed this functionality]
        # _thread.start_new_thread(self.check_for_updates, ())

        # Load settings after UI initialization
        self.load_settings()

        self.text_view.grab_focus()
        
        # Initialize recent files menu
        recent_files_menu = self.builder.get_object("recent_files_menu")
        if hasattr(self, 'accel_group'):
            pass  # accel_group will be set up if needed
        else:
            self.accel_group = Gtk.AccelGroup()
            self.window.add_accel_group(self.accel_group)
        
        # Set up recent files manager with menu and callback
        self.recent_files_manager.set_menu_and_accel_group(recent_files_menu, self.accel_group)
        self.recent_files_manager.set_file_open_callback(lambda file_path: self.file_manager.load_file(file_path, self.window.set_title))
        
        # Load window layout
        self.layout_manager.load_window_layout()

        self.tv_scrolled = self.scrolledwindow_text_view.get_vadjustment().connect("value-changed", self.scrollPreviewTo)
        self.lp_scrolled_fix = self.scrolledwindow_live_preview.get_vadjustment().connect("value-changed", self.scrollPreviewToFix)
        self.scrolledwindow_live_preview.get_vadjustment().set_lower(1)

        self.temp_file_list = []

    def on_find_next_button_clicked(self, widget):
        self.findbar.on_find_next_button_clicked(widget)

    def on_find_previous_button_clicked(self, widget):
        self.findbar.on_find_previous_button_clicked(widget)

    def on_find_entry_changed(self, entry):
        self.findbar.on_find_entry_changed(entry)

    def on_replace_button_clicked(self, widget):
        self.findbar.on_replace_button_clicked(widget)

    def on_replace_all_button_clicked(self, widget):
        self.findbar.on_replace_all_button_clicked(widget)

    def on_hide_panel_button_clicked(self, widget):
        self.findbar.on_hide_panel_button_clicked(widget)

    def can_redo_changed(self, widget):
        if self.text_buffer.can_redo():
            self.builder.get_object("menuitem_redo").set_sensitive(True)
            self.builder.get_object("toolbutton_redo").set_sensitive(True)
        else:
            self.builder.get_object("menuitem_redo").set_sensitive(False)
            self.builder.get_object("toolbutton_redo").set_sensitive(False)

    def can_undo_changed(self, widget):
        if self.text_buffer.can_undo():
            self.builder.get_object("menuitem_undo").set_sensitive(True)
            self.builder.get_object("toolbutton_undo").set_sensitive(True)

        else:
            self.builder.get_object("menuitem_undo").set_sensitive(False)
            self.builder.get_object("toolbutton_undo").set_sensitive(False)


    def load_settings(self):
        if self.settings_manager.is_nightmode_enabled():
            # Enable night/dark mode on startup
            self.builder.get_object("menuitem_night_mode").set_active(True)
            self.on_menuitem_night_mode_activate(self)

        if not self.settings_manager.is_word_wrap_enabled():
            # Disable word wrap on startup
            self.builder.get_object("menuitem_word_wrap").set_active(False)
            self.layout_manager.toggle_word_wrap()

        if not self.settings_manager.is_live_preview_enabled():
            # Disable Live Preview on startup
            self.builder.get_object("menuitem_live_preview").set_active(False)
            self.layout_manager.apply_live_preview_setting(lambda: self.update_live_preview(self))

        # Apply toolbar setting
        self.layout_manager.apply_toolbar_setting()

        # Apply statusbar setting
        self.layout_manager.apply_statusbar_setting(lambda: self.update_status_bar(self))
                
        if not self.settings_manager.is_line_numbers_enabled():
            # Hide line numbers on startup
            self.builder.get_object("menuitem_line_numbers").set_active(False)
            self.layout_manager.toggle_line_numbers()
            
        # Apply vertical layout setting
        self.layout_manager.apply_vertical_layout_setting()

        self.layout_manager.apply_zoom_setting()

        if self.settings_manager.is_rtl_enabled():
            self.builder.get_object("menuitem_rtl").set_active(True)

        # Try to load the previously chosen font, may fail as font may not exist, ect.
        try:
            self.font = self.settings_manager.get_font()
            self.text_view.override_font(Pango.FontDescription(self.font))
        except:
            pass # Loading font failed --> leave at default font
            
        # Load the previously chosen style through StyleManager
        # This is handled automatically by StyleManager initialization

        self.wrap_box.set_visible(False)
    
    def on_style_changed(self):
        """Callback when style changes - update live preview"""
        self.update_live_preview(self)

    def scrollPreviewToFix(self, widget):
        self.scrolledwindow_live_preview.get_vadjustment().disconnect(self.lp_scrolled_fix)
        value = self.scrolledwindow_live_preview.get_vadjustment().get_value()
        if value == 0: # Fix
            self.scrollPreviewTo(self)
        else:
            pass # Something better?

    def scrollPreviewTo(self, widget):
        self.scrolledwindow_live_preview.get_vadjustment().disconnect(self.lp_scrolled_fix)
        value = self.scrolledwindow_text_view.get_vadjustment().get_value()
        upper_edit = self.scrolledwindow_text_view.get_vadjustment().get_upper()
        preview_upper = self.scrolledwindow_live_preview.get_vadjustment().get_upper()
        if value >= upper_edit - self.scrolledwindow_text_view.get_vadjustment().get_page_size():
            self.scrolledwindow_live_preview.get_vadjustment().set_value(preview_upper - self.scrolledwindow_live_preview.get_vadjustment().get_page_size())
        else:
            self.scrolledwindow_live_preview.get_vadjustment().set_value(value / upper_edit * preview_upper)
        self.lp_scrolled_fix = self.scrolledwindow_live_preview.get_vadjustment().connect("value-changed", self.scrollPreviewToFix)

    def on_menuitem_numbered_list_activate(self, widget):
        self.markdown_formatter.apply_numbered_list()

    def on_menuitem_new_activate(self, widget):
        self.file_manager.new_file()

    def on_toolbutton_new_clicked(self, widget):
        self.file_manager.new_file()

    def on_menuitem_open_activate(self, widget):
        self.file_manager.open_file_dialog(self.window.set_title)

    def on_toolbutton_open_clicked(self, widget):
        self.file_manager.open_file_dialog(self.window.set_title)
    


    def on_menuitem_save_activate(self, widget):
        self.file_manager.save_file(self.window.set_title)

    def on_toolbutton_save_clicked(self, widget):
        self.file_manager.save_file(self.window.set_title)

    def on_menuitem_save_as_activate(self, widget, crap=""):
        self.file_manager.save_file_as(self.window.set_title)

    def on_menuitem_rtl_toggled(self, widget):
        self.rtl(widget.get_active())
        self.settings_manager.set_setting('rtl', widget.get_active())

    def rtl(self, enabled):
        # whatever the swap choice was, it needs to be flipped now
        self.on_menuitem_swap_activate(None)

        styles.rtl(enabled)
        self.update_live_preview(self)

    def on_menuitem_export_html_activate(self, widget):
        self.export_manager.export_html_styled(self.text_buffer, self.window)

    def on_menuitem_export_html_plain_activate(self, widget):
        self.export_manager.export_html_plain(self.text_buffer, self.window)


    def on_menuitem_export_pdf_activate(self, widget):
        self.export_manager.export_pdf_styled(self.text_buffer, self.window)

    def on_menuitem_export_pdf_plain_activate(self, widget):
        self.export_manager.export_pdf_plain(self.text_buffer, self.window)

    def on_menuitem_print_preview_activate(self, widget):
        """Print the content of the preview pane using WebKit2's built-in print functionality"""
        if self.live_preview.get_visible():
            try:
                # Use WebKit2's native print functionality which handles web content properly
                print_operation = WebKit2.PrintOperation.new(self.live_preview)
                print_operation.run_dialog(self.window)
            except Exception as e:
                logger.error(f"WebKit2 print operation error: {e}")
                # Fallback to standard GTK print operation
                self._fallback_print_preview()
        else:
            dialog = Gtk.MessageDialog(
                self.window, 0, Gtk.MessageType.WARNING,
                Gtk.ButtonsType.OK, "Preview Not Visible"
            )
            dialog.format_secondary_text("Please enable live preview first to print.")
            dialog.run()
            dialog.destroy()
    
    def _fallback_print_preview(self):
        """Fallback print method using standard GTK PrintOperation"""
        print_operation = Gtk.PrintOperation()
        print_operation.set_embed_page_setup(True)
        
        # Set up print operation callbacks
        print_operation.connect("begin-print", self._on_print_begin)
        print_operation.connect("draw-page", self._on_print_draw_page)
        
        try:
            result = print_operation.run(Gtk.PrintOperationAction.PRINT_DIALOG, self.window)
            if result == Gtk.PrintOperationResult.ERROR:
                logger.error("Print operation failed")
        except Exception as e:
            logger.error(f"Print operation error: {e}")
            dialog = Gtk.MessageDialog(
                self.window, 0, Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK, "Print Error"
            )
            dialog.format_secondary_text("Failed to print preview content.")
            dialog.run()
            dialog.destroy()
    
    def _on_print_begin(self, operation, context):
        """Called when print operation begins"""
        operation.set_n_pages(1)
    
    def _on_print_draw_page(self, operation, context, page_num):
        """Called to draw each page during printing"""
        cairo_context = context.get_cairo_context()
        
        # Get the WebView's content and render it for printing
        width = context.get_width()
        height = context.get_height()
        
        # Get WebView dimensions
        webview_width = self.live_preview.get_allocated_width()
        webview_height = self.live_preview.get_allocated_height()
        
        if webview_width > 0 and webview_height > 0:
            # Scale the WebView content to fit the page while maintaining aspect ratio
            scale_x = width / webview_width
            scale_y = height / webview_height
            scale = min(scale_x, scale_y)
            
            cairo_context.scale(scale, scale)
            
            # Draw the WebView content
            self.live_preview.draw(cairo_context)
        

    def on_menuitem_quit_activate(self, widget):
        self.clean_up()
        self.window_delete_event(self)

    def window_delete_event(self, widget, callback=None):
        safe_to_quit = self.file_manager.can_close_safely(self.window.set_title)
        
        if safe_to_quit:
            # Save window layout before quitting
            self.layout_manager.save_window_layout()
            self.quit_requested(None)
        else:
            return True # Cancel the quit operation as user didn't want to save the changes

    def quit_requested(self, widget, callback_data=None):
        self.clean_up() # Second time, just to be safe
        Gtk.main_quit()

    def on_menuitem_undo_activate(self, widget):
        self.undo(self)

    def on_toolbutton_undo_clicked(self, widget):
        self.undo(self)

    def undo(self, widget):
        if self.text_buffer.can_undo():
            self.text_buffer.undo()

    def on_menuitem_redo_activate(self, widget):
        self.redo(self)

    def on_toolbutton_redo_clicked(self, widget):
        self.redo(self)

    def zoom_in(self):
        self.layout_manager.zoom_in(lambda: self.scrollPreviewToFix(self))

    def zoom_out(self):
        self.layout_manager.zoom_out(lambda: self.scrollPreviewToFix(self))

    def on_toolbutton_zoom_in_clicked(self, widget):
        self.zoom_in()

    def on_toolbutton_zoom_out_clicked(self, widget):
        self.zoom_out()

    def redo(self, widget):
        if self.text_buffer.can_redo():
            self.text_buffer.redo()

    def on_menuitem_find_activate(self, widget):
        self.findbar.show()

    def on_menuitem_cut_activate(self, widget):
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()
            text = self.text_buffer.get_text(start, end, True)
            self.clipboard.set_text(text, -1)
            self.text_buffer.delete(start, end)

    def on_menuitem_copy_activate(self, widget):
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()
            text = self.text_buffer.get_text(start, end, True)
            self.clipboard.set_text(text, -1)
        else:
            self.live_preview.can_execute_editing_command(WebKit2.EDITING_COMMAND_COPY, None, self.execute_copy_command, None)

    def execute_copy_command(self, source, result, user_data):
        if self.live_preview.can_execute_editing_command_finish(result):
            self.live_preview.execute_editing_command(WebKit2.EDITING_COMMAND_COPY)

    def on_menuitem_paste_activate(self, widget):
        text = self.clipboard.wait_for_text()
        image = self.clipboard.wait_for_image()
        if text != None:
            if self.text_buffer.get_has_selection():
                start, end = self.text_buffer.get_selection_bounds()
                self.text_buffer.delete(start, end)
            self.text_buffer.insert_at_cursor(text)
        elif image != None:
            image_rel_path = 'imgs'
            if self.file_manager.get_current_file_path() == 'Untitled':
                # File not yet saved (i.e. we do not have path for the file)
                self.file_manager.save_file(self.window.set_title)
                assert self.file_manager.get_current_file_path() != 'Untitled'

            image_dir = os.path.join(os.path.dirname(self.file_manager.get_current_file_path()), image_rel_path)
            image_fname = datetime.datetime.now().strftime('%Y%m%d-%H%M%S.png')
            image_path = os.path.join(image_dir, image_fname)
            text = '![](%s/%s)' % (image_rel_path, image_fname)

            if not os.path.exists(image_dir):
                os.makedirs(image_dir)
            image.savev(image_path, 'png', [], [])

            if self.text_buffer.get_has_selection():
                start, end = self.text_buffer.get_selection_bounds()
                self.text_buffer.delete(start, end)

            self.text_buffer.insert_at_cursor(text)

    def on_menuitem_lower_activate(self, widget):
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()
            text = self.text_buffer.get_text(start, end, True)
            text = text.lower()
            self.text_buffer.delete(start, end)
            self.text_buffer.insert_at_cursor(text)

    def on_menuitem_title_activate(self, widget):
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()
            text = self.text_buffer.get_text(start, end, True)
            text = text.title()
            self.text_buffer.delete(start, end)
            self.text_buffer.insert_at_cursor(text)

    def on_menuitem_upper_activate(self, widget):
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()
            text = self.text_buffer.get_text(start, end, True)
            text = text.upper()
            self.text_buffer.delete(start, end)
            self.text_buffer.insert_at_cursor(text)
            
    def on_menuitem_join_lines_activate(self, widget):
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()
            self.text_buffer.join_lines(start, end)
        
    def on_menuitem_sort_lines_activate(self, widget):
        if self.text_buffer.get_has_selection():
            # Sort the selected lines
            start, end = self.text_buffer.get_selection_bounds()
            self.text_buffer.sort_lines(start, end, GtkSource.SortFlags.CASE_SENSITIVE, 0)
        else:
            # No selection active, sort all lines
            start, end = self.text_buffer.get_bounds()
            self.text_buffer.sort_lines(start, end, GtkSource.SortFlags.CASE_SENSITIVE, 0)

    def on_menuitem_sort_lines_reverse_activate(self, widget):
        if self.text_buffer.get_has_selection():
            # Sort the selected lines in reverse
            start, end = self.text_buffer.get_selection_bounds()
            self.text_buffer.sort_lines(start, end, GtkSource.SortFlags.REVERSE_ORDER, 0)
        else:
            # No selection active, sort all lines in reverse
            start, end = self.text_buffer.get_bounds()
            self.text_buffer.sort_lines(start, end, GtkSource.SortFlags.REVERSE_ORDER, 0)
    
    # Copy all text from the editor pane and format it as HTML in the clipboard
    def on_menuitem_copy_all_activate(self, widget):
        text = self.text_buffer.get_text(self.text_buffer.get_start_iter(), self.text_buffer.get_end_iter(), False)
        try:
            text = markdown.markdown(text, self.default_extensions)
        except:
            try:
                html_middle = markdown.markdown(text, extensions = self.safe_extensions)
            except:
                html_middle = markdown.markdown(text)
        self.clipboard.set_text(text, -1)

    # Copy selected text from the editor pane and format as HTML in the clipboard
    def on_menuitem_copy_selection_activate(self, widget):
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()
            text = self.text_buffer.get_text(start, end, True)
            try:
                text = markdown.markdown(text, self.default_extensions)
            except:
                try:
                    html_middle = markdown.markdown(text, extensions =self.safe_extensions)
                except:
                    html_middle = markdown.markdown(text)
            self.clipboard.set_text(text, -1)

    def on_menuitem_vertical_layout_activate(self, widget):
        self.layout_manager.toggle_vertical_layout()

    def on_menuitem_word_wrap_activate(self, widget):
        # Update settings based on menu state
        active = self.builder.get_object("menuitem_word_wrap").get_active()
        self.settings_manager.set_setting('word-wrap', active)
        self.layout_manager.toggle_word_wrap()


    def on_menuitem_line_numbers_activate(self, widget):
        # Update settings based on menu state
        active = self.builder.get_object("menuitem_line_numbers").get_active()
        self.settings_manager.set_setting('line-numbers', active)
        self.layout_manager.toggle_line_numbers()
            
    def on_menuitem_live_preview_activate(self, widget):
        self.layout_manager.toggle_live_preview(lambda: self.update_live_preview(self))


    def on_menuitem_swap_activate(self, widget):
        self.layout_manager.swap_panes()

    def on_menuitem_zoom_in_activate(self, widget):
        self.zoom_in()

    def on_menuitem_zoom_out_activate(self, widget):
        self.zoom_out()

    def on_menuitem_editor_font_activate(self, widget):
        self.font_chooser = Gtk.FontSelectionDialog()
        self.font_chooser.set_preview_text("reRemarkable is the best markdown editor for Linux")
        try:
            self.font_chooser.set_font_name(self.font)
        except:
            pass # Font not initialized, do nothing, continue
        self.font_chooser.connect("destroy", self.font_dialog_destroyed)
        self.font_ok_button = self.font_chooser.get_ok_button()
        self.font_ok_button.connect("clicked", self.font_dialog_ok)
        self.font_cancel_button = self.font_chooser.get_cancel_button()
        self.font_cancel_button.connect("clicked", self.font_dialog_cancel)
        self.font_chooser.show()

    def font_dialog_destroyed(self, widget):
        self.font_chooser.destroy()

    def font_dialog_cancel(self, widget):
        self.font_chooser.destroy()

    def font_dialog_ok(self, widget):
        self.font = self.font_chooser.get_font_name()
        self.settings_manager.set_setting('font', self.font)
        self.text_view.override_font(Pango.FontDescription(self.font))

        # Now adjust the size using TextTag
        self.font_dialog_destroyed(self)

    def on_menuitem_statusbar_activate(self, widget):
        self.layout_manager.toggle_statusbar(lambda: self.update_status_bar(self))

    def on_menuitem_toolbar_activate(self, widget):
        self.layout_manager.toggle_toolbar()

    def on_menuitem_preview_browser_activate(self, widget):
        # Create a temporary HTML file
        tf = tempfile.NamedTemporaryFile(delete = False)
        self.temp_file_list.append(tf)
        tf_name = tf.name

        text = self.text_buffer.get_text(self.text_buffer.get_start_iter(), self.text_buffer.get_end_iter(), False)
        dirname = os.path.dirname(self.file_manager.get_current_file_path())
        text = re.sub(r'(\!\[.*?\]\()([^/][^:]*?\))', lambda m, dirname=dirname: m.group(1) + os.path.join(dirname, m.group(2)), text)
        try:
            html_middle = markdown.markdown(text, self.default_extensions)
        except:
            try:
                html_middle = markdown.markdown(text, extensions =self.safe_extensions)
            except:
                html_middle = markdown.markdown(text)
        html = self.style_manager.get_html_head_style() + html_middle + self.default_html_end
        tf.write(html.encode())
        tf.flush()
        
        # Load the temporary HTML file in the user's default browser
        webbrowser.open_new_tab(tf_name)

    def on_menuitem_night_mode_activate(self, widget):
        if self.builder.get_object("menuitem_night_mode").get_active():
            self.settings.set_property("gtk-application-prefer-dark-theme", True)
            self.settings_manager.set_setting('nightmode', True)
        else:
            self.settings.set_property("gtk-application-prefer-dark-theme", False)
            self.settings_manager.set_setting('nightmode', False)

    def on_menuitem_fullscreen_activate(self, widget):
        self.layout_manager.toggle_fullscreen()

    def on_menuitem_bold_activate(self, widget):
        self.markdown_formatter.apply_bold()

    def on_toolbutton_bold_clicked(self, widget):
        self.markdown_formatter.apply_bold()

    def on_menuitem_italic_activate(self, widget):
        self.markdown_formatter.apply_italic()

    def on_toolbutton_italic_clicked(self, widget):
        self.markdown_formatter.apply_italic()

    def on_menuitem_strikethrough_activate(self, widget):
        self.markdown_formatter.apply_strikethrough()

    def on_toolbutton_strikethrough_clicked(self, widget):
        self.markdown_formatter.apply_strikethrough()

    def on_menuitem_highlight_activate(self, widget):
        self.markdown_formatter.apply_highlight()

    def on_menuitem_superscript_activate(self, widget):
        self.markdown_formatter.apply_superscript()

    def on_menuitem_subscript_activate(self, widget):
        self.markdown_formatter.apply_subscript()

    def on_menuitem_block_quote_activate(self, widget):
        self.markdown_formatter.apply_block_quote()

    def on_menuitem_code_activate(self, widget):
        self.markdown_formatter.apply_code_block()

    def on_menuitem_bullet_list_activate(self, widget):
        self.markdown_formatter.apply_bullet_list()

    def on_menuitem_heading_1_activate(self, widget):
        self.markdown_formatter.apply_heading(1)

    def on_menuitem_heading_2_activate(self, widget):
        self.markdown_formatter.apply_heading(2)

    def on_menuitem_heading_3_activate(self, widget):
        self.markdown_formatter.apply_heading(3)

    def on_menuitem_heading_4_activate(self, widget):
        self.markdown_formatter.apply_heading(4)

    def on_menuitem_horizonatal_rule_activate(self, widget):
        self.markdown_formatter.insert_horizontal_rule()

    def on_menuitem_timestamp_activate(self, widget):
        self.markdown_formatter.insert_timestamp()

    def on_toolbutton_timestamp_clicked(self, widget):
        self.markdown_formatter.insert_timestamp()

    def on_toolbutton_emoji_clicked(self, widget):
        self.show_emoji_picker(self)

    def insert_timestamp(self, widget):
        self.markdown_formatter.insert_timestamp()
        self.text_view.grab_focus()

    def on_menuitem_image_activate(self, widget):
        self.insert_image(self)

    def on_toolbutton_image_clicked(self, widget):
        self.insert_image(self)

    def on_menuitem_table_activate(self, widget):
        self.insert_table(self)

    def insert_table(self, widget):
        self.insert_window_table = Gtk.Window()
        self.insert_window_table.set_title("Insert Table")
        self.insert_window_table.set_resizable(True)
        self.insert_window_table.set_border_width(6)
        self.insert_window_table.set_default_size(300, 250)
        self.insert_window_table.set_position(Gtk.WindowPosition.CENTER)
        vbox = Gtk.VBox()
        label_n_rows = Gtk.Label("Number of Rows:")
        self.entry_n_rows = Gtk.Entry()
        label_n_columns = Gtk.Label("Number of Columns")
        self.entry_n_columns = Gtk.Entry()
        vbox.pack_start(label_n_rows, self, False, False)
        vbox.pack_start(self.entry_n_rows, self, False, False)
        vbox.pack_start(label_n_columns, self, False, False)
        vbox.pack_start(self.entry_n_columns, self, False, False)
        button = Gtk.Button("Insert Table")
        vbox.pack_end(button, self, False, False)
        self.insert_window_table.add(vbox)
        self.insert_window_table.show_all()
        button.connect("clicked", self.insert_table_cmd, self.insert_window_table)
    
    def insert_table_cmd(self, widget, window):
        # if self.entry_url_i.get_text():
        n_rows = self.entry_n_rows.get_text()
        n_columns = self.entry_n_columns.get_text()

        if n_rows and n_columns:
            try:
                n_rows = int(n_rows)
            except:
                return
            try:
                n_columns = int(n_columns)
            except:
                return
                
            if n_rows > 0 and n_columns > 0:
                table_str = ""
                line = ("|  "  * n_columns) + "|"
                header_line = ("|--" * n_columns) + "|"

                table_str = line + "\n" + header_line + "\n"
                if n_rows > 1:
                    n_rows -= 1
                    while n_rows > 0:                     
                        table_str += line + "\n"
                        n_rows -= 1

                self.markdown_formatter.create_table(n_rows, n_columns)
        self.insert_window_table.hide()

    def insert_image(self, widget):
        self.insert_window_image = Gtk.Window()
        self.insert_window_image.set_title("Insert Image")
        self.insert_window_image.set_resizable(True)
        self.insert_window_image.set_border_width(6)
        self.insert_window_image.set_default_size(300, 250)
        self.insert_window_image.set_position(Gtk.WindowPosition.CENTER)
        vbox = Gtk.VBox()
        label_alt_text = Gtk.Label("Alt Text:")
        self.entry_alt_text_i = Gtk.Entry()
        label_title = Gtk.Label("Title:")
        self.entry_title_i = Gtk.Entry()
        label_url = Gtk.Label("Path/Url:")
        self.entry_url_i = Gtk.Entry()
        vbox.pack_start(label_alt_text, self, False, False)
        vbox.pack_start(self.entry_alt_text_i, self, False, False)
        vbox.pack_start(label_title, self, False, False)
        vbox.pack_start(self.entry_title_i, self, False, False)
        vbox.pack_start(label_url, self, False, False)
        self.hbox_url = Gtk.HBox()
        self.hbox_url.pack_start(self.entry_url_i, self, True, False)
        self.path_file_button = Gtk.FileChooserButton(title= "Select an image")
        self.path_file_button.connect("file-set", self.file_chooser_button_clicked)
        self.hbox_url.pack_start(self.path_file_button, self, False, False)
        vbox.pack_start(self.hbox_url, self, False, False)
        button = Gtk.Button("Insert Image")
        vbox.pack_end(button, self, False, False)
        self.insert_window_image.add(vbox)
        self.insert_window_image.show_all()
        button.connect("clicked", self.insert_image_cmd, self.insert_window_image)

    def file_chooser_button_clicked(self, widget):
        filePath = widget.get_filename()
        self.entry_url_i.set_text(filePath)

    def insert_image_cmd(self, widget, window):
        if self.entry_url_i.get_text():
            alt_text = self.entry_alt_text_i.get_text() or " "
            url = self.entry_url_i.get_text()
            title = self.entry_title_i.get_text() if self.entry_title_i.get_text() else None
            self.markdown_formatter.insert_image(alt_text, url, title)
        self.insert_window_image.hide()

    def on_menuitem_link_activate(self, widget):
        self.insert_link(self)

    def on_toolbutton_link_clicked(self, widget):
        self.insert_link(self)

    def insert_link(self, widget):
        self.insert_window_link = Gtk.Window()
        self.insert_window_link.set_title("Insert Link")
        self.insert_window_link.set_resizable(True)
        self.insert_window_link.set_border_width(6)
        self.insert_window_link.set_default_size(350, 250)
        self.insert_window_link.set_position(Gtk.WindowPosition.CENTER)
        vbox = Gtk.VBox()
        label_alt_text = Gtk.Label("Alt Text:")
        self.entry_alt_text = Gtk.Entry()
        label_url = Gtk.Label("Url:")
        self.entry_url = Gtk.Entry()
        vbox.pack_start(label_alt_text, self, False, False)
        vbox.pack_start(self.entry_alt_text, self, False, False)
        vbox.pack_start(label_url, self, False, False)
        vbox.pack_start(self.entry_url, self, False, False)
        button = Gtk.Button("Insert Link")
        vbox.pack_end(button, self, False, False)

        # Use highligted text as the default "alt text"
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()
            text = self.text_buffer.get_text(start, end, True)
            self.entry_alt_text.set_text(text)

        self.insert_window_link.add(vbox)
        self.insert_window_link.show_all()
        button.connect("clicked", self.insert_link_cmd, self.insert_window_link)

    def insert_link_cmd(self, widget, window):
        if self.entry_url.get_text():
            alt_text = self.entry_alt_text.get_text()
            url = self.entry_url.get_text()
            self.markdown_formatter.insert_link(alt_text, url)
        self.insert_window_link.hide()

    def on_menuitem_emoji_activate(self, widget):
        self.show_emoji_picker(self)

    def show_emoji_picker(self, widget):
        """Show the emoji picker dialog"""
        if not self.emoji_picker:
            self.emoji_picker = EmojiPickerDialog(self.window, self.text_buffer)
        self.emoji_picker.show()



    def on_menuitem_dark_activate(self, widget):
        self.style_manager.apply_dark_style()

    def on_menuitem_foghorn_activate(self, widget):
        self.style_manager.apply_foghorn_style()

    def on_menuitem_github_activate(self, widget):
        self.style_manager.apply_github_style()

    def on_menuitem_handwritten_activate(self, widget):
        self.style_manager.apply_handwriting_style()

    def on_menuitem_markdown_activate(self, widget):
        self.style_manager.apply_markdown_style()

    def on_menuitem_metro_vibes_activate(self, widget):
        self.style_manager.apply_metro_vibes_style()

    def on_menuitem_metro_vibes_dark_activate(self, widget):
        self.style_manager.apply_metro_vibes_dark_style()


    def on_menuitem_modern_activate(self, widget):
        self.style_manager.apply_modern_style()

    def on_menuitem_screen_activate(self, widget):
        self.style_manager.apply_screen_style()
    
    def on_menuitem_solarized_dark_activate(self, widget):
        self.style_manager.apply_solarized_dark_style()

    def on_menuitem_solarized_light_activate(self, widget):
        self.style_manager.apply_solarized_light_style()

    # Custom CSS
    def on_menuitem_custom_activate(self, widget):
        self.style_manager.apply_custom_style_dialog(self.window)

    def on_menuitem_github_page_activate(self, widget):
        webbrowser.open_new_tab("https://github.com/pjobson/reRemarkable")
    
    def on_menuitem_reportbug_activate(self, widget):
        webbrowser.open_new_tab("https://github.com/pjobson/reRemarkable/issues")

    def on_menuitem_about_activate(self, widget):
        self.AboutDialog.show(self)

    def on_menuitem_markdown_tutorial_activate(self, widget):
        webbrowser.open_new_tab("https://daringfireball.net/projects/markdown/syntax")

    def on_menuitem_license_activate(self, widget):
        # Get the script's base directory
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        license_path = os.path.join(script_dir, 'LICENSE.md')

        # Check if LICENSE.md exists, if not download it
        if not os.path.exists(license_path):
            try:
                license_url = 'https://raw.githubusercontent.com/pjobson/reRemarkable/master/LICENSE.md'
                response = urlopen(license_url)
                license_content = response.read().decode('utf-8')
                with open(license_path, 'w') as f:
                    f.write(license_content)
            except Exception as e:
                logger.error(f"Failed to download LICENSE.md: {e}")
                return

        # Open the LICENSE.md file using the existing file opening mechanism
        self.file_manager.load_file(license_path, self.window.set_title)

    def on_text_view_changed(self, widget):
        start, end = self.text_buffer.get_bounds()
        
        if self.statusbar.get_visible():
            self.update_status_bar(self)
        else:  # statusbar not present, don't need to update/count words, etc.
            pass
        if self.live_preview.get_visible():
            self.update_live_preview(self)
            self.scrollPreviewTo(self)

        else:  # Live preview not enabled, don't need to update the view
            pass

        # Update title to reflect changes
        if self.text_buffer.get_modified():
            title = self.window.get_title()
            if title[0] != "*":
                title = "*" + title
                self.window.set_title(title)

    """
        GtkTextView simply does not seem to handle visual word
        movements correctly in bi-directional move.
        This is a hack for going the opposite of logical order
        in case RTL mode was selected in the editor.
        It's not perfect, but at least for people who are mostly
        working in RTL mode the cursor will behave as expected
        more frequently.

        The inherent bug here, of course, is that if there
        is an English paragraph in an RTL document, the cursor
        will go backwards on that specific paragraph.
        This might be fixed if we look at the current
        paragraph and infer how to act based on its type.
        But I didn't bother for now, as this, admittedly,
        is a double edge case: 1) RTL users; and 2) Having
        English paragraphs and caring about Ctrl+Arrows behavior
        in them to the point where it gets irritating.

        In short, this is a quick, but useful, hack.
    """
    def cursor_ctrl_arrow_rtl_fix(self, widget, event):
        if event.keyval in [Gdk.KEY_Left, Gdk.KEY_Right]:
            if event.state & Gdk.ModifierType.CONTROL_MASK:
                is_rtl = self.settings_manager.is_rtl_enabled()

                dirs = {
                    Gdk.KEY_Left: is_rtl and 1 or -1,
                    Gdk.KEY_Right: is_rtl and -1 or 1,
                }

                widget.emit('move-cursor',
                            Gtk.MovementStep.WORDS,
                            dirs[event.keyval],
                            event.state & Gdk.ModifierType.SHIFT_MASK != 0)

                return True

        return False

    """
        Update the text in the status bar. Displays the number of lines,
        words and characters. This approach is possible inefficient.
    """
    def update_status_bar(self, widget):
        self.statusbar.pop(self.context_id)
        lines = self.text_buffer.get_line_count()
        chars = self.text_buffer.get_char_count()
        words = self.text_buffer.get_text(self.text_buffer.get_start_iter(), self.text_buffer.get_end_iter(), False).split()
        word_count = 0
        word_exceptions = ["#", "##", "###", "####", "#####", "######", "*", "**", "-", "+", "_", "/", "\\", "/", ":",
                           ";", "@", "'", "~", "(", ")", "[", "]", "{", "}", "((", "))", "+-", "-+", "/=", ".", "|",
                           "!", "!!", "!!!", "$", "", "%", "^", "&"]  # Exclude these from word count
        for w in words:
            if w not in word_exceptions:
                if not re.match('^[0-9]{1,3}$', w):
                    word_count += 1
        self.status_message = "Lines: " + str(lines) + ", " + "Words: " + str(word_count) + ", Characters: " + str(chars)
        self.statusbar.push(self.context_id, self.status_message)

    def update_live_preview(self, widet):
        text = self.text_buffer.get_text(
            self.text_buffer.get_start_iter(),
            self.text_buffer.get_end_iter(),
            False
        )
        try:
            html_middle = markdown.markdown(text, self.default_extensions)
            html_middle = markdown.markdown(
                text,
                extensions=self.default_extensions,
                disable_raw_html=False
            )
        except:
            try:
                html_middle = markdown.markdown(
                    text,
                    extensions=self.safe_extensions,
                    disable_raw_html=False
                )
            except:
                html_middle = markdown.markdown(
                    text,
                    disable_raw_html=False
                )
        html = self.style_manager.get_html_head_style() + html_middle + self.default_html_end

        # Update the display, supporting relative paths to local images
        current_path = self.file_manager.get_current_file_path()
        if current_path != "Untitled":
            base_uri = "file://{}".format(os.path.abspath(current_path))
        else:
            base_uri = None
        self.live_preview.load_html(html, base_uri)

    """
        This function suppresses the messages from the WebKit (live preview) console
    """
    def _javascript_console_message(self, view, message, line, sourceid):
        return True


    """
        This function deletes any temporary files that were created during execution
    """
    def clean_up(self):
        i = len(self.temp_file_list) - 1
        while i >= 0:
            os.remove(self.temp_file_list[0].name)
            del self.temp_file_list[0]
            i -= 1



