#!/usr/bin/python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import unicodedata
import emoji

class EmojiPickerDialog:
    def __init__(self, parent_window, text_buffer):
        self.parent_window = parent_window
        self.text_buffer = text_buffer
        self.all_emojis = self._get_all_emojis()
        self.dialog = None
        
    def _get_all_emojis(self):
        """Get all emojis from the emoji package"""
        try:
            # Get all emojis from the emoji package
            all_emojis = list(emoji.EMOJI_DATA.keys())
            # Filter out skin tone variants and other modifiers to keep the list manageable
            filtered_emojis = []
            for emoji_char in all_emojis:
                # Skip skin tone modifiers and some complex sequences
                if len(emoji_char) <= 2 and '\U0001F3FB' not in emoji_char:
                    filtered_emojis.append(emoji_char)
            return sorted(filtered_emojis)[:500]  # Limit to first 500 for performance
        except Exception as e:
            print(f"Error loading emojis: {e}")
            # Fallback to a basic set if emoji package fails
            return ["😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😊", "😇",
                   "🙂", "🙃", "😉", "😌", "😍", "🥰", "😘", "😗", "😙", "😚"]
    
    def show(self):
        """Show the emoji picker dialog"""
        if self.dialog:
            self.dialog.present()
            return
            
        self.dialog = Gtk.Dialog(
            title="Emoji Picker",
            parent=self.parent_window,
            flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            buttons=(
                Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE
            )
        )
        
        self.dialog.set_default_size(500, 400)
        self.dialog.set_resizable(True)
        
        # Create main container
        main_box = Gtk.VBox(spacing=6)
        main_box.set_border_width(12)
        
        # Create search entry
        search_box = Gtk.HBox(spacing=50)
        search_label = Gtk.Label("Search:")
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Type to search emojis...")
        self.search_entry.connect("changed", self._on_search_changed)
        search_box.pack_start(search_label, False, False, 0)
        search_box.pack_start(self.search_entry, True, True, 0)
        
        # Create emoji grid
        self.emoji_container = self._create_emoji_grid(self.all_emojis)
        
        # Pack everything
        main_box.pack_start(search_box, False, False, 0)
        main_box.pack_start(self.emoji_container, True, True, 0)
        
        # Add to dialog content area
        content_area = self.dialog.get_content_area()
        content_area.add(main_box)
        
        # Connect signals
        self.dialog.connect("response", self._on_dialog_response)
        self.dialog.connect("key-press-event", self._on_key_press)
        
        # Show all widgets
        self.dialog.show_all()
        
        # Focus search entry
        self.search_entry.grab_focus()
    
    def _create_emoji_grid(self, emojis):
        """Create a grid of all emojis"""
        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(400)
        
        # Create flow box for emojis
        flowbox = Gtk.FlowBox()
        flowbox.set_valign(Gtk.Align.START)
        flowbox.set_max_children_per_line(12)
        flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        flowbox.set_homogeneous(True)
        flowbox.set_row_spacing(6)
        flowbox.set_column_spacing(6)
        
        # Add emojis to flowbox
        for emoji in emojis:
            button = Gtk.Button(emoji)
            button.set_size_request(40, 40)
            button.connect("clicked", self._on_emoji_clicked, emoji)
            # Set tooltip with emoji name
            try:
                emoji_name = emoji.demojize(emoji).replace(':', '').replace('_', ' ').title()
                if emoji_name == emoji:
                    emoji_name = unicodedata.name(emoji[0], "Unknown")
                button.set_tooltip_text(emoji_name)
            except:
                button.set_tooltip_text(emoji)
            flowbox.add(button)
        
        scrolled.add(flowbox)
        return scrolled
    
    def _on_emoji_clicked(self, button, emoji):
        """Handle emoji button click"""
        # Insert emoji at cursor position
        self.text_buffer.insert_at_cursor(emoji)
        # Close dialog
        self.dialog.response(Gtk.ResponseType.CLOSE)
    
    def _on_search_changed(self, entry):
        """Handle search entry changes"""
        search_text = entry.get_text().lower()
        
        if not search_text:
            # Show all emojis
            self._update_emoji_display(self.all_emojis)
            return
        
        # Filter emojis based on search
        matching_emojis = []
        for emoji_char in self.all_emojis:
            try:
                # Use emoji package for better name matching
                emoji_name = emoji.demojize(emoji_char).replace(':', '').replace('_', ' ').lower()
                unicode_name = unicodedata.name(emoji_char[0], "").lower()

                if (search_text in emoji_name or
                    search_text in unicode_name or
                    search_text in emoji_char):
                    matching_emojis.append(emoji_char)
            except:
                if search_text in emoji_char:
                    matching_emojis.append(emoji_char)
        
        # Update display with filtered emojis
        self._update_emoji_display(matching_emojis)
    
    def _update_emoji_display(self, emojis):
        """Update the emoji display with filtered emojis"""
        # Get the parent container
        content_area = self.dialog.get_content_area()
        main_box = content_area.get_children()[0]
        
        # Remove old emoji container
        main_box.remove(self.emoji_container)
        
        # Create new emoji container with filtered emojis
        self.emoji_container = self._create_emoji_grid(emojis)
        
        # Add new container
        main_box.pack_start(self.emoji_container, True, True, 0)
        self.emoji_container.show_all()
    
    def _on_key_press(self, widget, event):
        """Handle key press events"""
        if event.keyval == Gdk.KEY_Escape:
            self.dialog.response(Gtk.ResponseType.CLOSE)
            return True
        return False
    
    def _on_dialog_response(self, dialog, response_id):
        """Handle dialog response"""
        dialog.destroy()
        self.dialog = None
