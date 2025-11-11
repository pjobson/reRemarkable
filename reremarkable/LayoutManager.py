
import json
import logging
import os

from gi.repository import GLib, Gtk

logger = logging.getLogger('reremarkable')

class LayoutManager:
    """Handles window layout and UI management for the markdown editor"""

    def __init__(self, window, settings_manager):
        self.window = window
        self.settings_manager = settings_manager
        self.paned = None
        self.live_preview = None
        self.scrolledwindow_text_view = None
        self.scrolledwindow_live_preview = None
        self.text_view = None
        self.toolbar = None
        self.statusbar = None
        self.builder = None

        # Layout state
        self.is_fullscreen = False
        self.editor_position = 0  # 0 = editor left/top, 1 = editor right/bottom
        self.zoom_steps = 0.1

        # Config file path
        self.config_dir = os.path.expanduser('~/.config/reremarkable')
        self.layout_file = os.path.join(self.config_dir, 'layout.json')

    def set_ui_components(self, paned, live_preview, scrolledwindow_text_view,
                         scrolledwindow_live_preview, text_view, toolbar, statusbar, builder):
        """Set references to UI components"""
        self.paned = paned
        self.live_preview = live_preview
        self.scrolledwindow_text_view = scrolledwindow_text_view
        self.scrolledwindow_live_preview = scrolledwindow_live_preview
        self.text_view = text_view
        self.toolbar = toolbar
        self.statusbar = statusbar
        self.builder = builder

    def toggle_vertical_layout(self):
        """Toggle between horizontal and vertical layout"""
        if self.settings_manager.is_vertical_layout():
            # Switch to vertical layout and reset position
            self.paned.set_orientation(Gtk.Orientation.VERTICAL)
            self.paned.set_orientation(Gtk.Orientation.HORIZONTAL)
            self.paned.set_orientation(Gtk.Orientation.VERTICAL)
            self.paned.set_position(self.paned.get_allocation().height/2)
            self.settings_manager.set_setting('vertical', True)
        else:
            self.paned.set_orientation(Gtk.Orientation.HORIZONTAL)
            self.paned.set_position(self.paned.get_allocation().width/2)
            self.settings_manager.set_setting('vertical', False)

    def apply_vertical_layout_setting(self):
        """Apply the vertical layout setting from config"""
        if self.settings_manager.is_vertical_layout():
            self.paned.set_orientation(Gtk.Orientation.VERTICAL)
            if self.builder:
                self.builder.get_object("menuitem_vertical_layout").set_active(True)
        else:
            self.paned.set_orientation(Gtk.Orientation.HORIZONTAL)

    def toggle_word_wrap(self):
        """Toggle word wrap on the text view"""
        if self.settings_manager.is_word_wrap_enabled():
            self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        else:
            self.text_view.set_wrap_mode(Gtk.WrapMode.NONE)

    def toggle_line_numbers(self):
        """Toggle line numbers on the text view"""
        if self.settings_manager.is_line_numbers_enabled():
            self.text_view.set_show_line_numbers(True)
        else:
            self.text_view.set_show_line_numbers(False)

    def toggle_live_preview(self, update_callback=None):
        """
        Toggle the visibility of the live preview pane

        Args:
            update_callback: Optional callback to update live preview content
        """
        if self.live_preview.get_visible():
            # Hide the live preview
            self.paned.remove(self.scrolledwindow_live_preview)
            self.live_preview.set_visible(False)
            self.settings_manager.set_setting('live-preview', False)
            if self.builder:
                self.builder.get_object("menuitem_swap").set_sensitive(False)
                self.builder.get_object("menuitem_swap").set_tooltip_text("Enable Live Preview First")
                self.builder.get_object("toolbar1").set_visible(False)
        else:
            # Show the live preview
            self.paned.add(self.scrolledwindow_live_preview)
            if self.editor_position == 0:
                self.paned.remove(self.scrolledwindow_text_view)
                self.paned.add(self.scrolledwindow_text_view)
            self.live_preview.set_visible(True)
            self.settings_manager.set_setting('live-preview', True)
            if self.builder:
                self.builder.get_object("menuitem_swap").set_sensitive(True)
                self.builder.get_object("menuitem_swap").set_tooltip_text("")
                self.builder.get_object("toolbar1").set_visible(True)
            if update_callback:
                update_callback()

    def swap_panes(self):
        """Swap the position of editor and preview panes"""
        if self.live_preview.get_visible():
            self.paned.remove(self.scrolledwindow_live_preview)
            self.paned.remove(self.scrolledwindow_text_view)
            if self.editor_position == 0:
                self.paned.add(self.scrolledwindow_live_preview)
                self.paned.add(self.scrolledwindow_text_view)
                self.editor_position = 1
            else:
                self.paned.add(self.scrolledwindow_text_view)
                self.paned.add(self.scrolledwindow_live_preview)
                self.editor_position = 0

    def zoom_in(self, scroll_callback=None):
        """
        Zoom in the live preview

        Args:
            scroll_callback: Optional callback to fix scrolling after zoom
        """
        current_zoom = self.live_preview.get_zoom_level()
        new_zoom = (1 + self.zoom_steps) * current_zoom
        self.live_preview.set_zoom_level(new_zoom)
        self.settings_manager.set_setting('zoom-level', new_zoom)
        if scroll_callback:
            scroll_callback()

    def zoom_out(self, scroll_callback=None):
        """
        Zoom out the live preview

        Args:
            scroll_callback: Optional callback to fix scrolling after zoom
        """
        current_zoom = self.live_preview.get_zoom_level()
        new_zoom = (1 - self.zoom_steps) * current_zoom
        self.live_preview.set_zoom_level(new_zoom)
        self.settings_manager.set_setting('zoom-level', new_zoom)
        if scroll_callback:
            scroll_callback()

    def apply_zoom_setting(self):
        """Apply the zoom level setting from config"""
        zoom_level = self.settings_manager.get_zoom_level()
        self.live_preview.set_zoom_level(zoom_level)

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.is_fullscreen:
            self.window.unfullscreen()
            self.is_fullscreen = False
            if self.builder:
                self.builder.get_object("menuitem_fullscreen").set_label("Fullscreen")
        else:
            self.window.fullscreen()
            self.is_fullscreen = True
            if self.builder:
                self.builder.get_object("menuitem_fullscreen").set_label("Exit fullscreen")

    def toggle_toolbar(self):
        """Toggle the visibility of the toolbar"""
        if self.toolbar.get_visible():
            self.toolbar.set_visible(False)
            self.settings_manager.set_setting('toolbar', False)
            if self.builder:
                self.builder.get_object("menuitem_toolbar").set_label("Show Toolbar")
                self.builder.get_object("toolbar1").set_visible(False)
        else:
            self.toolbar.set_visible(True)
            self.settings_manager.set_setting('toolbar', True)
            if self.builder:
                self.builder.get_object("menuitem_toolbar").set_label("Hide Toolbar")
                self.builder.get_object("toolbar1").set_visible(True)

    def toggle_statusbar(self, status_update_callback=None):
        """
        Toggle the visibility of the statusbar

        Args:
            status_update_callback: Optional callback to update status content
        """
        if self.statusbar.get_visible():
            self.statusbar.set_visible(False)
            self.settings_manager.set_setting('statusbar', False)
            if self.builder:
                self.builder.get_object("menuitem_statusbar").set_label("Show Statusbar")
        else:
            self.statusbar.set_visible(True)
            self.settings_manager.set_setting('statusbar', True)
            if self.builder:
                self.builder.get_object("menuitem_statusbar").set_label("Hide Statusbar")
            if status_update_callback:
                status_update_callback()

    def apply_toolbar_setting(self):
        """Apply the toolbar visibility setting from config"""
        if not self.settings_manager.is_toolbar_visible():
            self.toggle_toolbar()

    def apply_statusbar_setting(self, status_update_callback=None):
        """Apply the statusbar visibility setting from config"""
        if not self.settings_manager.is_statusbar_visible():
            self.toggle_statusbar(status_update_callback)

    def apply_live_preview_setting(self, update_callback=None):
        """Apply the live preview visibility setting from config"""
        if not self.settings_manager.is_live_preview_enabled():
            self.toggle_live_preview(update_callback)

    def save_window_layout(self):
        """Save window layout to config file"""
        try:
            # Get window position and size
            x, y = self.window.get_position()
            width, height = self.window.get_size()
            maximized = self.window.is_maximized()

            # Get paned position
            paned_position = self.paned.get_position()

            # Get editor position and live preview visibility
            live_preview_visible = self.live_preview.get_visible()

            layout_data = {
                'window_width': width,
                'window_height': height,
                'window_x': x,
                'window_y': y,
                'window_maximized': maximized,
                'paned_position': paned_position,
                'editor_position': self.editor_position,
                'live_preview_visible': live_preview_visible
            }

            # Create config directory if it doesn't exist
            os.makedirs(self.config_dir, exist_ok=True)

            # Save layout to file
            with open(self.layout_file, 'w') as f:
                json.dump(layout_data, f, indent=2)

        except Exception as e:
            logger.error(f"Could not save window layout: {e}")

    def load_window_layout(self):
        """Load window layout from config file"""
        try:
            if not os.path.exists(self.layout_file):
                return

            with open(self.layout_file) as f:
                layout_data = json.load(f)

            # Restore window size and position
            if 'window_width' in layout_data and 'window_height' in layout_data:
                width = layout_data['window_width']
                height = layout_data['window_height']
                self.window.resize(width, height)

            if 'window_x' in layout_data and 'window_y' in layout_data:
                x = layout_data['window_x']
                y = layout_data['window_y']
                self.window.move(x, y)

            # Restore maximized state
            if layout_data.get('window_maximized', False):
                self.window.maximize()

            # Restore paned position (defer until window is realized)
            if 'paned_position' in layout_data:
                position = layout_data['paned_position']
                GLib.idle_add(self._restore_paned_position, position)

            # Restore editor position
            if 'editor_position' in layout_data:
                self.editor_position = layout_data['editor_position']

            # Restore live preview visibility
            if 'live_preview_visible' in layout_data:
                if not layout_data['live_preview_visible'] and self.live_preview.get_visible():
                    # Live preview should be hidden
                    GLib.idle_add(self.toggle_live_preview)

        except Exception as e:
            logger.error(f"Could not load window layout: {e}")

    def _restore_paned_position(self, position):
        """Helper function to restore paned position after window is realized"""
        try:
            self.paned.set_position(position)
            return False  # Don't repeat this idle callback
        except Exception as e:
            logger.error(f"Could not restore paned position: {e}")
            return False

    def get_editor_position(self):
        """Get the current editor position (0 = left/top, 1 = right/bottom)"""
        return self.editor_position

    def is_live_preview_visible(self):
        """Check if live preview is currently visible"""
        return self.live_preview.get_visible() if self.live_preview else False

    def get_current_zoom_level(self):
        """Get the current zoom level"""
        return self.live_preview.get_zoom_level() if self.live_preview else 1.0
