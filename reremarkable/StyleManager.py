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
        'handwriting_css': lambda: styles.handwriting,
        'markdown': lambda: styles.markdown,
        'metro_vibes': lambda: styles.metro_vibes,
        'metro_vibes_dark': lambda: styles.metro_vibes_dark,
        'modern_css': lambda: styles.modern,
        'screen': lambda: styles.screen,
        'solarized_dark': lambda: styles.solarized_dark,
        'solarized_light': lambda: styles.solarized_light
    }
    
    def __init__(self, settings_manager, media_path):
        self.settings_manager = settings_manager
        self.media_path = media_path
        self.current_style = "github"  # Default style
        self.style_change_callbacks = []

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
    
    def apply_handwriting_style(self):
        """Apply handwriting style"""
        return self.set_style('handwriting_css')
    
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
        return self.set_style('modern_css')
    
    def apply_screen_style(self):
        """Apply screen style"""
        return self.set_style('screen')
    
    def apply_solarized_dark_style(self):
        """Apply solarized dark style"""
        return self.set_style('solarized_dark')
    
    def apply_solarized_light_style(self):
        """Apply solarized light style"""
        return self.set_style('solarized_light')