#!/usr/bin/python3

import gi

gi.require_version('Gtk', '3.0')
import logging
import os

from gi.repository import Gdk, Gtk

logger = logging.getLogger('reremarkable')

class RecentFilesManager:
    """
    Manages the recent files functionality including:
    - Loading and saving recent files from/to config file
    - Managing the recent files list
    - Creating and updating the recent files menu
    - Handling recent file selection and accelerator keys
    """

    def __init__(self, max_recent_files=10):
        """
        Initialize the RecentFilesManager

        Args:
            max_recent_files (int): Maximum number of recent files to track
        """
        self.recent_files = []
        self.max_recent_files = max_recent_files
        self.recent_files_file = os.path.expanduser("~/.config/reremarkable/recent_files.txt")
        self.recent_files_menu = None
        self.accel_group = None
        self.file_open_callback = None

        # Load recent files on initialization
        self.load_recent_files()

    def set_menu_and_accel_group(self, recent_files_menu, accel_group):
        """
        Set the GTK menu object and accelerator group for recent files

        Args:
            recent_files_menu: The GTK menu object for recent files
            accel_group: The accelerator group for keyboard shortcuts
        """
        self.recent_files_menu = recent_files_menu
        self.accel_group = accel_group
        self.update_recent_files_menu()

    def set_file_open_callback(self, callback):
        """
        Set the callback function to open a file

        Args:
            callback: Function to call when opening a file, should accept file_path
        """
        self.file_open_callback = callback

    def load_recent_files(self):
        """Load recent files from config file"""
        try:
            # Create config directory if it doesn't exist
            config_dir = os.path.dirname(self.recent_files_file)
            os.makedirs(config_dir, exist_ok=True)

            if os.path.exists(self.recent_files_file):
                with open(self.recent_files_file) as f:
                    self.recent_files = [line.strip() for line in f.readlines() if line.strip()]
                # Remove files that no longer exist
                self.recent_files = [f for f in self.recent_files if os.path.exists(f)]
        except Exception as e:
            logger.warning(f"Could not load recent files: {e}")
            self.recent_files = []

    def save_recent_files(self):
        """Save recent files to config file"""
        try:
            config_dir = os.path.dirname(self.recent_files_file)
            os.makedirs(config_dir, exist_ok=True)

            with open(self.recent_files_file, 'w') as f:
                for file_path in self.recent_files:
                    f.write(file_path + '\n')
        except Exception as e:
            logger.warning(f"Could not save recent files: {e}")

    def add_recent_file(self, file_path):
        """
        Add a file to the recent files list

        Args:
            file_path (str): The path of the file to add
        """
        # Convert to absolute path
        file_path = os.path.abspath(file_path)

        # Remove if already in list
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)

        # Add to beginning of list
        self.recent_files.insert(0, file_path)

        # Limit list size
        if len(self.recent_files) > self.max_recent_files:
            self.recent_files = self.recent_files[:self.max_recent_files]

        # Save to file
        self.save_recent_files()

        # Update menu if available
        if self.recent_files_menu:
            self.update_recent_files_menu()

    def clear_recent_files(self):
        """Clear all recent files"""
        self.recent_files = []
        self.save_recent_files()
        if self.recent_files_menu:
            self.update_recent_files_menu()

    def open_recent_file(self, menuitem, file_path):
        """
        Open a recent file

        Args:
            menuitem: The menu item that was clicked
            file_path (str): The path of the file to open
        """
        if os.path.exists(file_path):
            if self.file_open_callback:
                self.file_open_callback(file_path)
        else:
            # File no longer exists, remove from recent files
            if file_path in self.recent_files:
                self.recent_files.remove(file_path)
                self.save_recent_files()
                if self.recent_files_menu:
                    self.update_recent_files_menu()

    def update_recent_files_menu(self):
        """Update the recent files submenu"""
        if not self.recent_files_menu:
            return

        # Clear existing menu items
        for child in self.recent_files_menu.get_children():
            self.recent_files_menu.remove(child)

        if not self.recent_files:
            # Add "No recent files" item
            no_files_item = Gtk.MenuItem.new_with_label("No recent files")
            no_files_item.set_sensitive(False)
            no_files_item.show()
            self.recent_files_menu.append(no_files_item)
        else:
            # Add recent files
            for i, file_path in enumerate(self.recent_files):
                # Create menu item with filename and path
                filename = os.path.basename(file_path)
                directory = os.path.dirname(file_path)

                # Truncate long paths
                if len(directory) > 50:
                    directory = "..." + directory[-47:]

                label = f"{i+1}. {filename}"
                menu_item = Gtk.MenuItem.new_with_label(label)
                menu_item.set_tooltip_text(file_path)
                menu_item.connect("activate", self.open_recent_file, file_path)
                menu_item.show()
                self.recent_files_menu.append(menu_item)

                # Add accelerator for first 9 files (Ctrl+Alt+1-9)
                if i < 9 and self.accel_group:
                    menu_item.add_accelerator("activate", self.accel_group,
                                            ord('1') + i, Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.MOD1_MASK,
                                            Gtk.AccelFlags.VISIBLE)

            # Add separator and clear option
            separator = Gtk.SeparatorMenuItem()
            separator.show()
            self.recent_files_menu.append(separator)

            clear_item = Gtk.MenuItem.new_with_label("Clear Recent Files")
            clear_item.connect("activate", lambda x: self.clear_recent_files())
            clear_item.show()
            self.recent_files_menu.append(clear_item)

    def get_recent_files(self):
        """
        Get the list of recent files

        Returns:
            list: List of recent file paths
        """
        return self.recent_files.copy()

    def has_recent_files(self):
        """
        Check if there are any recent files

        Returns:
            bool: True if there are recent files, False otherwise
        """
        return len(self.recent_files) > 0
