# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

import os
import sys
import subprocess
import logging
from gi.repository import Gtk

logger = logging.getLogger('reremarkable')

class FileManager:
    """Handles file operations for the markdown editor"""
    
    def __init__(self, window, text_buffer):
        self.window = window
        self.text_buffer = text_buffer
        self.current_file_path = "Untitled"
        self.recent_files_callback = None
        
    def set_recent_files_callback(self, callback):
        """Set callback function for managing recent files"""
        self.recent_files_callback = callback
    
    def get_current_file_path(self):
        """Get the current file path"""
        return self.current_file_path
    
    def set_current_file_path(self, path):
        """Set the current file path"""
        self.current_file_path = path
        
    def get_current_filename(self):
        """Get just the filename from the current path"""
        if self.current_file_path == "Untitled":
            return "Untitled"
        return os.path.basename(self.current_file_path)
    
    def get_text_content(self):
        """Get all text content from the buffer"""
        return self.text_buffer.get_text(
            self.text_buffer.get_start_iter(), 
            self.text_buffer.get_end_iter(), 
            False
        )
    
    def is_buffer_modified(self):
        """Check if the text buffer has been modified"""
        return self.text_buffer.get_modified()
    
    def is_buffer_empty(self):
        """Check if the text buffer is empty"""
        start, end = self.text_buffer.get_bounds()
        text = self.text_buffer.get_text(start, end, False)
        return len(text) == 0
    
    def set_file_chooser_path(self, chooser):
        """Set the default path for file chooser dialogs"""
        if self.current_file_path != "Untitled":
            chooser.set_current_folder(os.path.dirname(self.current_file_path))
    
    def show_save_confirmation_dialog(self):
        """
        Show save confirmation dialog when there are unsaved changes.
        Returns True if user wants to save, False otherwise.
        """
        if not self.is_buffer_modified():
            return False
            
        message = "Do you want to save the changes you have made?"
        dialog = Gtk.MessageDialog(
            self.window,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.QUESTION, 
            Gtk.ButtonsType.YES_NO,
            message
        )
        dialog.set_title("Save?")
        dialog.set_default_response(Gtk.ResponseType.YES)

        response = dialog.run()
        dialog.destroy()
        
        return response == Gtk.ResponseType.YES
    
    def load_file(self, file_path, title_callback=None):
        """
        Load a file into the text buffer.
        
        Args:
            file_path: Path to the file to load
            title_callback: Optional callback to update window title
        """
        try:
            self.text_buffer.begin_not_undoable_action()
            
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            self.current_file_path = file_path
            self.text_buffer.set_text(text)
            self.text_buffer.set_modified(False)
            self.text_buffer.end_not_undoable_action()
            
            # Update window title if callback provided
            if title_callback:
                filename = os.path.basename(file_path)
                title_callback(f"reRemarkable: {filename}")
            
            # Add to recent files
            if self.recent_files_callback:
                self.recent_files_callback(file_path)
                
            return True
            
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            self._show_error_dialog("File Load Error", f"Could not load file: {e}")
            return False
    
    def save_file(self, title_callback=None):
        """
        Save the current file.
        
        Args:
            title_callback: Optional callback to update window title
        
        Returns:
            True if saved successfully, False otherwise
        """
        if self.current_file_path == "Untitled":
            return self.save_file_as(title_callback)
        
        try:
            text = self.get_text_content()
            
            with open(self.current_file_path, 'w', encoding='utf-8') as file:
                file.write(text)
            
            self.text_buffer.set_modified(False)
            
            # Update window title if callback provided
            if title_callback:
                filename = os.path.basename(self.current_file_path)
                title_callback(f"reRemarkable: {filename}")
            
            # Add to recent files
            if self.recent_files_callback:
                self.recent_files_callback(self.current_file_path)
                
            return True
            
        except Exception as e:
            logger.error(f"Error saving file {self.current_file_path}: {e}")
            self._show_error_dialog("File Save Error", f"Could not save file: {e}")
            return False
    
    def save_file_as(self, title_callback=None):
        """
        Save the current file with a new name using a file chooser dialog.
        
        Args:
            title_callback: Optional callback to update window title
        
        Returns:
            True if saved successfully, False if cancelled or failed
        """
        self.window.set_sensitive(False)
        
        chooser = Gtk.FileChooserDialog(
            title=None, 
            action=Gtk.FileChooserAction.SAVE, 
            buttons=(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 
                Gtk.STOCK_SAVE, Gtk.ResponseType.OK
            )
        )
        
        self.set_file_chooser_path(chooser)
        chooser.set_do_overwrite_confirmation(True)
        
        current_title = self.get_current_filename()
        chooser.set_title(f"Save As: {current_title}")
        
        response = chooser.run()
        saved = False
        
        if response == Gtk.ResponseType.OK:
            new_path = chooser.get_filename()
            
            try:
                text = self.get_text_content()
                
                with open(new_path, 'w', encoding='utf-8') as file:
                    file.write(text)
                
                self.current_file_path = new_path
                self.text_buffer.set_modified(False)
                
                # Update window title if callback provided
                if title_callback:
                    filename = os.path.basename(new_path)
                    title_callback(f"reRemarkable: {filename}")
                
                # Add to recent files
                if self.recent_files_callback:
                    self.recent_files_callback(new_path)
                
                saved = True
                
            except Exception as e:
                logger.error(f"Error saving file as {new_path}: {e}")
                self._show_error_dialog("File Save Error", f"Could not save file: {e}")
        
        chooser.destroy()
        self.window.set_sensitive(True)
        return saved
    
    def open_file_dialog(self, title_callback=None):
        """
        Show file open dialog and handle the selected file.
        
        Args:
            title_callback: Optional callback to update window title
        
        Returns:
            True if file was opened, False otherwise
        """
        # Check if current buffer has content
        if not self.is_buffer_empty() or self.is_buffer_modified():
            # Open in new window if current buffer has content
            return self._open_file_dialog_new_window()
        else:
            # Load in current window if empty
            return self._open_file_dialog_current_window(title_callback)
    
    def _open_file_dialog_current_window(self, title_callback=None):
        """Open file dialog and load file in current window"""
        self.window.set_sensitive(False)
        
        chooser = Gtk.FileChooserDialog(
            title="Open File", 
            action=Gtk.FileChooserAction.OPEN, 
            buttons=(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 
                Gtk.STOCK_OPEN, Gtk.ResponseType.OK
            )
        )
        
        self.set_file_chooser_path(chooser)
        response = chooser.run()
        
        file_opened = False
        if response == Gtk.ResponseType.OK:
            selected_file = chooser.get_filename()
            file_opened = self.load_file(selected_file, title_callback)
        
        chooser.destroy()
        self.window.set_sensitive(True)
        return file_opened
    
    def _open_file_dialog_new_window(self):
        """Open file dialog and load file in new window"""
        self.window.set_sensitive(False)
        
        chooser = Gtk.FileChooserDialog(
            title="Open File", 
            action=Gtk.FileChooserAction.OPEN, 
            buttons=(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 
                Gtk.STOCK_OPEN, Gtk.ResponseType.OK
            )
        )
        
        self.set_file_chooser_path(chooser)
        response = chooser.run()
        
        file_opened = False
        if response == Gtk.ResponseType.OK:
            selected_file = chooser.get_filename()
            # Launch new instance with the selected file
            subprocess.Popen([sys.argv[0], selected_file])
            file_opened = True
        
        chooser.destroy()
        self.window.set_sensitive(True)
        return file_opened
    
    def new_file(self):
        """Create a new file by launching a new instance of the application"""
        subprocess.Popen(sys.argv[0])
    
    def can_close_safely(self, title_callback=None):
        """
        Check if the window can be closed safely, prompting for save if needed.
        
        Args:
            title_callback: Optional callback to update window title
        
        Returns:
            True if safe to close, False if user cancelled
        """
        if not self.is_buffer_empty() and self.show_save_confirmation_dialog():
            return self.save_file(title_callback)
        return True
    
    def _show_error_dialog(self, title, message):
        """Show an error dialog"""
        dialog = Gtk.MessageDialog(
            self.window,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK,
            message
        )
        dialog.set_title(title)
        dialog.run()
        dialog.destroy()