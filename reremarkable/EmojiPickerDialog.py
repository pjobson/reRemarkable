#!/usr/bin/python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import unicodedata

class EmojiPickerDialog:
    def __init__(self, parent_window, text_buffer):
        self.parent_window = parent_window
        self.text_buffer = text_buffer
        self.emoji_categories = self._get_emoji_categories()
        self.dialog = None
        
    def _get_emoji_categories(self):
        """Define emoji categories with common emojis"""
        return {
            "Smileys & People": [
                "😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😊", "😇",
                "🙂", "🙃", "😉", "😌", "😍", "🥰", "😘", "😗", "😙", "😚",
                "😋", "😛", "😝", "😜", "🤪", "🤨", "🧐", "🤓", "😎", "🤩",
                "🥳", "😏", "😒", "😞", "😔", "😟", "😕", "🙁", "☹️", "😣",
                "😖", "😫", "😩", "🥺", "😢", "😭", "😤", "😠", "😡", "🤬",
                "🤯", "😳", "🥵", "🥶", "😱", "😨", "😰", "😥", "😓", "🤗",
                "🤔", "🤭", "🤫", "🤥", "😶", "😐", "😑", "😬", "🙄", "😯",
                "😦", "😧", "😮", "😲", "🥱", "😴", "🤤", "😪", "😵", "🤐",
                "🥴", "🤢", "🤮", "🤧", "😷", "🤒", "🤕", "🤑", "🤠", "😈",
                "👿", "👹", "👺", "🤡", "💩", "👻", "💀", "☠️", "👽", "👾"
            ],
            "Animals & Nature": [
                "🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐨", "🐯",
                "🦁", "🐮", "🐷", "🐽", "🐸", "🐵", "🙈", "🙉", "🙊", "🐒",
                "🐔", "🐧", "🐦", "🐤", "🐣", "🐥", "🦆", "🦅", "🦉", "🦇",
                "🐺", "🐗", "🐴", "🦄", "🐝", "🐛", "🦋", "🐌", "🐞", "🐜",
                "🦟", "🦗", "🕷️", "🕸️", "🦂", "🐢", "🐍", "🦎", "🦖", "🦕",
                "🐙", "🦑", "🦐", "🦞", "🦀", "🐡", "🐠", "🐟", "🐬", "🐳",
                "🐋", "🦈", "🐊", "🐅", "🐆", "🦓", "🦍", "🦧", "🐘", "🦛",
                "🦏", "🐪", "🐫", "🦒", "🦘", "🐃", "🐂", "🐄", "🐎", "🐖"
            ],
            "Food & Drink": [
                "🍎", "🍐", "🍊", "🍋", "🍌", "🍉", "🍇", "🍓", "🫐", "🍈",
                "🍒", "🍑", "🥭", "🍍", "🥥", "🥝", "🍅", "🍆", "🥑", "🥦",
                "🥬", "🥒", "🌶️", "🫑", "🌽", "🥕", "🫒", "🧄", "🧅", "🥔",
                "🍠", "🥐", "🍞", "🥖", "🥨", "🧀", "🥚", "🍳", "🧈", "🥞",
                "🧇", "🥓", "🥩", "🍗", "🍖", "🦴", "🌭", "🍔", "🍟", "🍕",
                "🥪", "🥙", "🧆", "🌮", "🌯", "🫔", "🥗", "🥘", "🫕", "🍝",
                "🍜", "🍲", "🍛", "🍣", "🍱", "🥟", "🦪", "🍤", "🍙", "🍚",
                "🍘", "🍥", "🥠", "🥮", "🍢", "🍡", "🍧", "🍨", "🍦", "🥧"
            ],
            "Activities": [
                "⚽", "🏀", "🏈", "⚾", "🥎", "🎾", "🏐", "🏉", "🥏", "🎱",
                "🪀", "🏓", "🏸", "🏒", "🏑", "🥍", "🏏", "🪃", "🥅", "⛳",
                "🪁", "🏹", "🎣", "🤿", "🥊", "🥋", "🎽", "🛹", "🛼", "🛷",
                "⛸️", "🥌", "🎿", "⛷️", "🏂", "🪂", "🏋️", "🤼", "🤸", "⛹️",
                "🤺", "🏇", "🧘", "🏄", "🏊", "🤽", "🚣", "🧗", "🚵", "🚴",
                "🏆", "🥇", "🥈", "🥉", "🏅", "🎖️", "🏵️", "🎗️", "🎫", "🎟️",
                "🎪", "🤹", "🎭", "🩰", "🎨", "🎬", "🎤", "🎧", "🎼", "🎵",
                "🎶", "🥁", "🪘", "🎹", "🎸", "🪕", "🎺", "🎷", "🪗", "🎻"
            ],
            "Travel & Places": [
                "🚗", "🚕", "🚙", "🚌", "🚎", "🏎️", "🚓", "🚑", "🚒", "🚐",
                "🛻", "🚚", "🚛", "🚜", "🏍️", "🛵", "🚲", "🛴", "🛹", "🛼",
                "🚁", "🛸", "✈️", "🛩️", "🛫", "🛬", "🪂", "💺", "🚀", "🛰️",
                "🚢", "⛵", "🚤", "🛥️", "🛳️", "⛴️", "🚨", "🚥", "🚦", "🛑",
                "🚏", "⚓", "⛽", "🚧", "🚇", "🚈", "🚝", "🚞", "🚋", "🚃",
                "🚟", "🚠", "🚡", "🎢", "🎡", "🎠", "🏗️", "🌉", "🏰", "🏯",
                "🏟️", "🎪", "🏭", "🏠", "🏡", "🏘️", "🏚️", "🏗️", "🏢", "🏬",
                "🏣", "🏤", "🏥", "🏦", "🏨", "🏪", "🏫", "🏩", "💒", "🏛️"
            ],
            "Objects": [
                "⌚", "📱", "📲", "💻", "⌨️", "🖥️", "🖨️", "🖱️", "🖲️", "🕹️",
                "🗜️", "💽", "💾", "💿", "📀", "📼", "📷", "📸", "📹", "🎥",
                "📽️", "🎞️", "📞", "☎️", "📟", "📠", "📺", "📻", "🎙️", "🎚️",
                "🎛️", "🧭", "⏱️", "⏲️", "⏰", "🕰️", "⌛", "⏳", "📡", "🔋",
                "🔌", "💡", "🔦", "🕯️", "🪔", "🧯", "🛢️", "💸", "💵", "💴",
                "💶", "💷", "🪙", "💰", "💳", "💎", "⚖️", "🪜", "🧰", "🔧",
                "🔨", "⚒️", "🛠️", "⛏️", "🪓", "🪚", "🔩", "⚙️", "🪤", "🧲",
                "🔫", "💣", "🧨", "🪓", "🔪", "🗡️", "⚔️", "🛡️", "🚬", "⚰️"
            ],
            "Symbols": [
                "❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💔",
                "❣️", "💕", "💞", "💓", "💗", "💖", "💘", "💝", "💟", "☮️",
                "✝️", "☪️", "🕉️", "☸️", "✡️", "🔯", "🕎", "☯️", "☦️", "🛐",
                "⛎", "♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐",
                "♑", "♒", "♓", "🆔", "⚛️", "🉑", "☢️", "☣️", "📴", "📳",
                "🈶", "🈚", "🈸", "🈺", "🈷️", "✴️", "🆚", "💮", "🉐", "㊙️",
                "㊗️", "🈴", "🈵", "🈹", "🈲", "🅰️", "🅱️", "🆎", "🆑", "🅾️",
                "🆘", "❌", "⭕", "🛑", "⛔", "📛", "🚫", "💯", "💢", "♨️"
            ]
        }
    
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
        search_box = Gtk.HBox(spacing=6)
        search_label = Gtk.Label("Search:")
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Type to search emojis...")
        self.search_entry.connect("changed", self._on_search_changed)
        search_box.pack_start(search_label, False, False, 0)
        search_box.pack_start(self.search_entry, True, True, 0)
        
        # Create category notebook
        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        
        # Add categories
        for category_name, emojis in self.emoji_categories.items():
            self._create_category_page(category_name, emojis)
        
        # Pack everything
        main_box.pack_start(search_box, False, False, 0)
        main_box.pack_start(self.notebook, True, True, 0)
        
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
    
    def _create_category_page(self, category_name, emojis):
        """Create a page for an emoji category"""
        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        # Create flow box for emojis
        flowbox = Gtk.FlowBox()
        flowbox.set_valign(Gtk.Align.START)
        flowbox.set_max_children_per_line(10)
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
                emoji_name = unicodedata.name(emoji[0], "Unknown")
                button.set_tooltip_text(emoji_name.title())
            except:
                button.set_tooltip_text(emoji)
            flowbox.add(button)
        
        scrolled.add(flowbox)
        
        # Create tab label
        tab_label = Gtk.Label(category_name)
        
        # Add page to notebook
        self.notebook.append_page(scrolled, tab_label)
    
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
            # Show all categories
            for i in range(self.notebook.get_n_pages()):
                page = self.notebook.get_nth_page(i)
                page.show()
            return
        
        # Filter emojis based on search
        matching_emojis = []
        for category_name, emojis in self.emoji_categories.items():
            for emoji in emojis:
                try:
                    emoji_name = unicodedata.name(emoji[0], "").lower()
                    if search_text in emoji_name or search_text in emoji:
                        matching_emojis.append(emoji)
                except:
                    if search_text in emoji:
                        matching_emojis.append(emoji)
        
        # Create or update search results page
        self._show_search_results(matching_emojis)
    
    def _show_search_results(self, emojis):
        """Show search results in a special page"""
        # Remove existing search page if it exists
        for i in range(self.notebook.get_n_pages()):
            page = self.notebook.get_nth_page(i)
            tab_label = self.notebook.get_tab_label(page)
            if hasattr(tab_label, 'get_text') and tab_label.get_text() == "Search Results":
                self.notebook.remove_page(i)
                break
        
        if not emojis:
            return
        
        # Create search results page
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        flowbox = Gtk.FlowBox()
        flowbox.set_valign(Gtk.Align.START)
        flowbox.set_max_children_per_line(10)
        flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        flowbox.set_homogeneous(True)
        flowbox.set_row_spacing(6)
        flowbox.set_column_spacing(6)
        
        for emoji in emojis:
            button = Gtk.Button(emoji)
            button.set_size_request(40, 40)
            button.connect("clicked", self._on_emoji_clicked, emoji)
            try:
                emoji_name = unicodedata.name(emoji[0], "Unknown")
                button.set_tooltip_text(emoji_name.title())
            except:
                button.set_tooltip_text(emoji)
            flowbox.add(button)
        
        scrolled.add(flowbox)
        
        # Add as first page and switch to it
        tab_label = Gtk.Label("Search Results")
        self.notebook.insert_page(scrolled, tab_label, 0)
        self.notebook.set_current_page(0)
        scrolled.show_all()
    
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