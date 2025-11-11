#!/usr/bin/python3

import gi

gi.require_version('Gtk', '3.0')
import logging
import os
import re

import markdown
from bs4 import BeautifulSoup
from gi.repository import Gtk

import pdfkit_local as pdfkit

logger = logging.getLogger('reremarkable')

class ExportManager:
    """
    Manages export functionality for HTML and PDF formats including:
    - HTML export (styled and plain)
    - PDF export (styled and plain)
    - File chooser dialogs with appropriate filters
    - Markdown to HTML conversion with fallback extensions
    - Error handling and user feedback
    """

    def __init__(self, style_manager, file_manager, media_path):
        """
        Initialize the ExportManager

        Args:
            style_manager: StyleManager instance for getting HTML styles
            file_manager: FileManager instance for file path operations
            media_path: Path to media files for HTML footer
        """
        self.style_manager = style_manager
        self.file_manager = file_manager
        self.media_path = media_path

        # Markdown extensions configuration
        self.default_extensions = [
            'markdown.extensions.extra',
            'markdown.extensions.toc',
            'markdown.extensions.smarty',
            'markdown_extensions.extensions.urlize',
            'markdown_extensions.extensions.Highlighting',
            'markdown_extensions.extensions.Strikethrough',
            'markdown_extensions.extensions.markdown_checklist',
            'markdown_extensions.extensions.superscript',
            'markdown_extensions.extensions.subscript',
            'markdown_extensions.extensions.mathjax'
        ]
        self.safe_extensions = ['markdown.extensions.extra']

        # HTML footer with scripts for syntax highlighting and MathJax
        self.default_html_end = (
            '<script src="' + self.media_path + 'highlight.min.js"></script>'
            '<script>hljs.initHighlightingOnLoad();</script>'
            '<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.2/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>'
            '<script type="text/javascript">MathJax.Hub.Config({"showProcessingMessages" : false,"messageStyle" : "none","tex2jax": { inlineMath: [ [ "$", "$" ] ] }});</script>'
            '</body></html>'
        )

        # Track PDF export errors to avoid multiple warnings
        self.pdf_error_warning = False

        # Callback for setting window sensitivity during exports
        self.window_sensitivity_callback = None

    def set_window_sensitivity_callback(self, callback):
        """
        Set callback to control window sensitivity during export operations

        Args:
            callback: Function to call with True/False to set window sensitivity
        """
        self.window_sensitivity_callback = callback

    def _set_window_sensitive(self, sensitive):
        """Set window sensitivity using callback if available"""
        if self.window_sensitivity_callback:
            self.window_sensitivity_callback(sensitive)

    def _convert_markdown_to_html(self, text):
        """
        Convert markdown text to HTML with fallback extension handling

        Args:
            text (str): Markdown text to convert

        Returns:
            str: Converted HTML
        """
        try:
            return markdown.markdown(text, self.default_extensions)
        except:
            try:
                return markdown.markdown(text, extensions=self.safe_extensions)
            except:
                return markdown.markdown(text)

    def _process_image_paths_for_pdf(self, text, current_file_path):
        """
        Process relative image paths for PDF export by making them absolute

        Args:
            text (str): Markdown text containing image references
            current_file_path (str): Current file path for resolving relative paths

        Returns:
            str: Text with processed image paths
        """
        if current_file_path == "Untitled":
            return text

        dirname = os.path.dirname(current_file_path)
        return re.sub(
            r'(\!\[.*?\]\()([^/][^:]*?\))',
            lambda m, dirname=dirname: m.group(1) + os.path.join(dirname, m.group(2)),
            text
        )

    def export_html_styled(self, text_buffer, parent_window=None):
        """
        Export markdown content as styled HTML

        Args:
            text_buffer: GTK text buffer containing markdown content
            parent_window: Parent window for dialog (optional)
        """
        self._set_window_sensitive(False)

        try:
            # Get text from buffer
            start, end = text_buffer.get_bounds()
            text = text_buffer.get_text(start, end, False)

            # Convert to HTML
            html_middle = self._convert_markdown_to_html(text)
            html = self.style_manager.get_html_head_style() + html_middle + self.default_html_end

            # Save HTML
            self._save_html_file(html, parent_window)
        finally:
            self._set_window_sensitive(True)

    def export_html_plain(self, text_buffer, parent_window=None):
        """
        Export markdown content as plain HTML (no styling)

        Args:
            text_buffer: GTK text buffer containing markdown content
            parent_window: Parent window for dialog (optional)
        """
        self._set_window_sensitive(False)

        try:
            # Get text from buffer
            start, end = text_buffer.get_bounds()
            text = text_buffer.get_text(start, end, False)

            # Convert to HTML (plain, no styling)
            html = self._convert_markdown_to_html(text)

            # Save HTML
            self._save_html_file(html, parent_window)
        finally:
            self._set_window_sensitive(True)

    def export_pdf_styled(self, text_buffer, parent_window=None):
        """
        Export markdown content as styled PDF

        Args:
            text_buffer: GTK text buffer containing markdown content
            parent_window: Parent window for dialog (optional)
        """
        self._set_window_sensitive(False)

        try:
            # Get text from buffer
            start, end = text_buffer.get_bounds()
            text = text_buffer.get_text(start, end, False)

            # Process image paths for PDF
            current_file_path = self.file_manager.get_current_file_path()
            text = self._process_image_paths_for_pdf(text, current_file_path)

            # Convert to HTML
            html_middle = self._convert_markdown_to_html(text)
            html = self.style_manager.get_html_head_style() + html_middle + self.default_html_end

            # Save PDF
            self._save_pdf_file(html, parent_window)
        finally:
            self._set_window_sensitive(True)

    def export_pdf_plain(self, text_buffer, parent_window=None):
        """
        Export markdown content as plain PDF (no styling)

        Args:
            text_buffer: GTK text buffer containing markdown content
            parent_window: Parent window for dialog (optional)
        """
        self._set_window_sensitive(False)

        try:
            # Get text from buffer
            start, end = text_buffer.get_bounds()
            text = text_buffer.get_text(start, end, False)

            # Convert to HTML (plain, no styling)
            html = self._convert_markdown_to_html(text)

            # Save PDF
            self._save_pdf_file(html, parent_window)
        finally:
            self._set_window_sensitive(True)

    def _save_html_file(self, html_content, parent_window=None):
        """
        Show file chooser dialog and save HTML content to file

        Args:
            html_content (str): HTML content to save
            parent_window: Parent window for dialog (optional)
        """
        chooser = Gtk.FileChooserDialog(
            "Export HTML", parent_window, Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK)
        )

        # Set default path if current file exists
        self.file_manager.set_file_chooser_path(chooser)

        # Configure file filter
        html_filter = Gtk.FileFilter()
        html_filter.set_name("HTML Files")
        html_filter.add_pattern("*.html")
        html_filter.add_pattern("*.htm")
        chooser.set_do_overwrite_confirmation(True)
        chooser.add_filter(html_filter)

        try:
            response = chooser.run()
            if response == Gtk.ResponseType.OK:
                file_name = chooser.get_filename()
                if not file_name.endswith(".html"):
                    file_name += ".html"

                # Use BeautifulSoup to prettify HTML
                soup = BeautifulSoup(html_content, "lxml")

                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(soup.prettify())
        finally:
            chooser.destroy()

    def _save_pdf_file(self, html_content, parent_window=None):
        """
        Show file chooser dialog and save HTML content as PDF

        Args:
            html_content (str): HTML content to convert to PDF
            parent_window: Parent window for dialog (optional)
        """
        chooser = Gtk.FileChooserDialog(
            "Export PDF", parent_window, Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK)
        )

        # Set default path if current file exists
        self.file_manager.set_file_chooser_path(chooser)

        # Configure file filter
        pdf_filter = Gtk.FileFilter()
        pdf_filter.add_pattern("*.pdf")
        pdf_filter.set_name("PDF Files")
        chooser.add_filter(pdf_filter)
        chooser.set_do_overwrite_confirmation(True)

        try:
            response = chooser.run()
            if response == Gtk.ResponseType.OK:
                file_name = chooser.get_filename()
                if not file_name.endswith(".pdf"):
                    file_name += ".pdf"

                self._generate_pdf(html_content, file_name, parent_window)
        finally:
            chooser.destroy()

    def _generate_pdf(self, html_content, file_path, parent_window=None):
        """
        Generate PDF from HTML content with error handling

        Args:
            html_content (str): HTML content to convert
            file_path (str): Output PDF file path
            parent_window: Parent window for error dialog (optional)
        """
        try:
            # Try with full options first
            pdfkit.from_string(html_content, file_path, options={
                'quiet': '',
                'page-size': 'Letter',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'javascript-delay': '550',
                'no-outline': None
            })
        except:
            try:
                # Failed, try with no options
                pdfkit.from_string(html_content, file_path)
            except:
                # PDF Export failed completely
                self._show_pdf_error_dialog(parent_window)

    def _show_pdf_error_dialog(self, parent_window=None):
        """
        Show error dialog when PDF export fails

        Args:
            parent_window: Parent window for dialog (optional)
        """
        # Show warning message only once per session
        if not self.pdf_error_warning:
            self.pdf_error_warning = True
            logger.error("PDF Export Failed!")
            print("\nreRemarkable Error:\tPDF Export Failed!!")

        # Show error dialog to user
        dialog = Gtk.MessageDialog(
            parent_window, 0, Gtk.MessageType.ERROR,
            Gtk.ButtonsType.CANCEL, "PDF EXPORT FAILED"
        )
        dialog.format_secondary_text("File export to PDF was unsuccessful.")
        dialog.run()
        dialog.destroy()

    def get_supported_export_formats(self):
        """
        Get list of supported export formats

        Returns:
            dict: Dictionary of format names and descriptions
        """
        return {
            'html_styled': 'HTML with styling',
            'html_plain': 'HTML without styling',
            'pdf_styled': 'PDF with styling',
            'pdf_plain': 'PDF without styling'
        }
