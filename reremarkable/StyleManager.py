# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

import styles
from gi.repository import Gtk
import logging

logger = logging.getLogger('reremarkable')

class StyleManager:
    """Handles style management for the markdown editor"""
    
    # Available style mappings
    STYLE_MAPPINGS = {
        'dark': lambda: styles.dark,
        'foghorn': lambda: styles.foghorn,
        'github': lambda: styles.github,
        'github_dark': lambda: styles.github_dark,
        'github_light': lambda: styles.github_light,
        'handwriting': lambda: styles.handwriting,
        'markdown': lambda: styles.markdown,
        'metro_vibes': lambda: styles.metro_vibes,
        'metro_vibes_dark': lambda: styles.metro_vibes_dark,
        'modern': lambda: styles.modern,
        'screen': lambda: styles.screen,
        'solarized_dark': lambda: styles.solarized_dark,
        'solarized_light': lambda: styles.solarized_light
    }
    
    def __init__(self, settings_manager, media_path):
        self.settings_manager = settings_manager
        self.media_path = media_path
        self.current_style = "github"  # Default style
        self.style_change_callbacks = []
        self.menu_items = {}  # Dictionary to store menu item references
        self.menu_labels = {}  # Dictionary to store original menu item labels

        # Load current style from settings
        self.load_current_style()
    
    def add_style_change_callback(self, callback):
        """Add a callback to be called when style changes"""
        self.style_change_callbacks.append(callback)
    
    def _notify_style_change(self):
        """Notify all callbacks of style change"""
        for callback in self.style_change_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in style change callback: {e}")
    
    def load_current_style(self):
        """Load the current style from settings"""
        self.current_style = self.settings_manager.get_style()
        self.apply_current_style()
    
    def apply_current_style(self):
        """Apply the currently selected style"""
        if self.current_style in self.STYLE_MAPPINGS:
            styles.set(self.STYLE_MAPPINGS[self.current_style]())
        else:
            logger.warning(f"Unknown style: {self.current_style}")
            # Fallback to github style
            styles.set(styles.github)
            self.current_style = "github"
    
    def set_style(self, style_name):
        """
        Set a predefined style

        Args:
            style_name: Name of the style to apply
        """
        if style_name not in self.STYLE_MAPPINGS:
            logger.error(f"Unknown style: {style_name}")
            return False

        self.current_style = style_name
        styles.set(self.STYLE_MAPPINGS[style_name]())
        self.settings_manager.set_setting('style', style_name)
        self.update_visual_markers()  # Update visual markers when style changes
        self._notify_style_change()
        return True
    
    def get_current_style(self):
        """Get the current style name"""
        return self.current_style
    
    def get_html_head_style(self):
        """Get the HTML head style section for preview"""
        html_start = (
            '<!doctype HTML><html><head><meta charset="utf-8">'
            '<title>Made with reRemarkable!</title>'
            f'<link rel="stylesheet" href="{self.media_path}highlightjs.default.min.css">'
            f"<style type='text/css'>{styles.get()}</style>"
            '</head><body>'
        )
        return html_start
    
    def get_available_styles(self):
        """Get list of available predefined styles"""
        return list(self.STYLE_MAPPINGS.keys())

    def set_menu_items(self, builder):
        """
        Store references to style menu items for visual marker management

        Args:
            builder: GTK builder object with menu items
        """
        # Map menu item IDs to their style names and labels
        menu_item_map = {
            'menuitem_dark': ('dark', 'Dark'),
            'menuitem_foghorn': ('foghorn', 'Foghorn'),
            'menuitem_github': ('github', 'Github (Default)'),
            'menuitem_github_dark': ('github_dark', 'GitHub Dark'),
            'menuitem_github_light': ('github_light', 'GitHub Light'),
            'menuitem_handwritten': ('handwriting', 'Handwritten'),
            'menuitem_markdown': ('markdown', 'Markdown'),
            'menuitem_metro_vibes': ('metro_vibes', 'Metro Vibes'),
            'menuitem_metro_vibes_dark': ('metro_vibes_dark', 'Metro Vibes Dark'),
            'menuitem_modern': ('modern', 'Modern'),
            'menuitem_screen': ('screen', 'Screen'),
            'menuitem_solarized_dark': ('solarized_dark', 'Solarized Dark'),
            'menuitem_solarized_light': ('solarized_light', 'Solarized Light')
        }

        # Get and store all menu item references and original labels
        for menu_id, (style_name, label) in menu_item_map.items():
            menu_item = builder.get_object(menu_id)
            if menu_item:
                self.menu_items[style_name] = menu_item
                self.menu_labels[style_name] = label

        # Update visual markers to match current style
        self.update_visual_markers()

    def update_visual_markers(self):
        """Update visual ✓ markers on menu items to reflect current style"""
        for style_name, menu_item in self.menu_items.items():
            original_label = self.menu_labels.get(style_name, '')
            if style_name == self.current_style:
                # Add ✓ marker to the current style
                menu_item.set_label(f"✓ {original_label}")
            else:
                # Remove marker from other styles
                menu_item.set_label(original_label)
    
    # Convenience methods for specific styles
    def apply_dark_style(self):
        """Apply dark style"""
        return self.set_style('dark')
    
    def apply_foghorn_style(self):
        """Apply foghorn style"""
        return self.set_style('foghorn')
    
    def apply_github_style(self):
        """Apply github style"""
        return self.set_style('github')

    def apply_github_dark_style(self):
        """Apply GitHub Dark style"""
        return self.set_style('github_dark')

    def apply_github_light_style(self):
        """Apply GitHub Light style"""
        return self.set_style('github_light')

    def apply_handwriting_style(self):
        """Apply handwriting style"""
        return self.set_style('handwriting')
    
    def apply_markdown_style(self):
        """Apply markdown style"""
        return self.set_style('markdown')
    
    def apply_metro_vibes_style(self):
        """Apply metro vibes style"""
        return self.set_style('metro_vibes')
    
    def apply_metro_vibes_dark_style(self):
        """Apply metro vibes dark style"""
        return self.set_style('metro_vibes_dark')
    
    def apply_modern_style(self):
        """Apply modern style"""
        return self.set_style('modern')
    
    def apply_screen_style(self):
        """Apply screen style"""
        return self.set_style('screen')
    
    def apply_solarized_dark_style(self):
        """Apply solarized dark style"""
        return self.set_style('solarized_dark')
    
    def apply_solarized_light_style(self):
        """Apply solarized light style"""
        return self.set_style('solarized_light')