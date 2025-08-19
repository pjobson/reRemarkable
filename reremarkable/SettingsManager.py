# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

import os
import logging

logger = logging.getLogger('reremarkable')

class SettingsManager:
    def __init__(self, home_dir):
        self.homeDir = home_dir
        self.path = os.path.join(self.homeDir, ".reremarkable/")
        self.settings_path = os.path.join(self.path, "reremarkable.settings")
        self.settings = {}
        self._initialize_defaults()
    
    def _initialize_defaults(self):
        """Initialize default settings"""
        self.default_settings = {
            'css': '',
            'font': "Sans 10",
            'line-numbers': True,
            'live-preview': True,
            'nightmode': False,
            'statusbar': True,
            'style': "github",
            'toolbar': True,
            'vertical': False,
            'word-wrap': True,
            'zoom-level': 1,
            'rtl': False
        }
    
    def check_settings(self):
        """Check and create settings directory and file if they don't exist"""
        if not os.path.exists(self.path):
            os.makedirs(self.path)
            
        if not os.path.isfile(self.settings_path):
            self.settings = self.default_settings.copy()
            self.write_settings()
        else:
            self.load_settings_from_file()
    
    def load_settings_from_file(self):
        """Load settings from file"""
        try:
            with open(self.settings_path, 'r') as settings_file:
                self.settings = eval(settings_file.read())
            
            # Add any missing default settings
            for key, value in self.default_settings.items():
                if key not in self.settings:
                    self.settings[key] = value
                    
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            self.settings = self.default_settings.copy()
    
    def write_settings(self):
        """Write settings to file"""
        try:
            with open(self.settings_path, 'w') as settings_file:
                settings_file.write(str(self.settings))
        except Exception as e:
            logger.error(f"Error writing settings: {e}")
    
    def get_setting(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set_setting(self, key, value):
        """Set a setting value and save to file"""
        self.settings[key] = value
        self.write_settings()
    
    def get_all_settings(self):
        """Get all settings"""
        return self.settings.copy()
    
    def update_settings(self, new_settings):
        """Update multiple settings at once"""
        self.settings.update(new_settings)
        self.write_settings()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = self.default_settings.copy()
        self.write_settings()
    
    # Convenience methods for common settings
    def is_nightmode_enabled(self):
        return self.get_setting('nightmode', False)
    
    def is_word_wrap_enabled(self):
        return self.get_setting('word-wrap', True)
    
    def is_live_preview_enabled(self):
        return self.get_setting('live-preview', True)
    
    def is_toolbar_visible(self):
        return self.get_setting('toolbar', True)
    
    def is_statusbar_visible(self):
        return self.get_setting('statusbar', True)
    
    def is_line_numbers_enabled(self):
        return self.get_setting('line-numbers', True)
    
    def is_vertical_layout(self):
        return self.get_setting('vertical', False)
    
    def is_rtl_enabled(self):
        return self.get_setting('rtl', False)
    
    def get_font(self):
        return self.get_setting('font', "Sans 10")
    
    def get_style(self):
        return self.get_setting('style', "github")
    
    def get_zoom_level(self):
        return self.get_setting('zoom-level', 1)
    
    def get_custom_css(self):
        return self.get_setting('css', '')