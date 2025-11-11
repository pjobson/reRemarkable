
import datetime
import re


class MarkdownFormatter:
    """Handles markdown formatting operations for text buffers"""

    def __init__(self, text_buffer):
        self.text_buffer = text_buffer

    def _wrap_selection_or_cursor(self, prefix, suffix=None, cursor_offset=None):
        """
        Generic method to wrap text with markdown formatting.

        Args:
            prefix: Text to insert before selection/cursor
            suffix: Text to insert after selection/cursor (defaults to prefix if None)
            cursor_offset: Number of characters to move cursor back when no selection
        """
        if suffix is None:
            suffix = prefix
        if cursor_offset is None:
            cursor_offset = len(suffix)

        if not self.text_buffer.get_has_selection():
            # No selection - insert prefix+suffix and position cursor
            full_text = prefix + suffix
            self.text_buffer.insert_at_cursor(full_text)
            loc = self.text_buffer.get_iter_at_mark(self.text_buffer.get_insert())
            loc.backward_chars(cursor_offset)
            self.text_buffer.place_cursor(loc)
        else:
            # Has selection - wrap the selected text
            selection_bounds = self.text_buffer.get_selection_bounds()
            mark1 = self.text_buffer.create_mark(None, selection_bounds[0], False)
            mark2 = self.text_buffer.create_mark(None, selection_bounds[1], False)
            self.text_buffer.insert(self.text_buffer.get_iter_at_mark(mark1), prefix)
            self.text_buffer.insert(self.text_buffer.get_iter_at_mark(mark2), suffix)

    def _add_line_prefix(self, prefix):
        """Add a prefix to each line in selection or current line"""
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()
            start_line = start.get_line()
            end_line = end.get_line()

            line_number = start_line
            while line_number <= end_line:
                temp_iter = self.text_buffer.get_iter_at_line(line_number)
                self.text_buffer.insert(temp_iter, prefix)
                line_number += 1
        else:
            temp_iter = self.text_buffer.get_iter_at_mark(self.text_buffer.get_insert())
            line_number = temp_iter.get_line()
            start_iter = self.text_buffer.get_iter_at_line(line_number)
            self.text_buffer.insert(start_iter, prefix)

    def apply_bold(self):
        """Apply bold formatting (**text**)"""
        self._wrap_selection_or_cursor("**", "**", 2)

    def apply_italic(self):
        """Apply italic formatting (*text*)"""
        self._wrap_selection_or_cursor("*", "*", 1)

    def apply_strikethrough(self):
        """Apply strikethrough formatting (~~text~~)"""
        self._wrap_selection_or_cursor("~~", "~~", 2)

    def apply_highlight(self):
        """Apply highlight formatting (==text==)"""
        self._wrap_selection_or_cursor("==", "==", 2)

    def apply_superscript(self):
        """Apply superscript formatting (^text^)"""
        self._wrap_selection_or_cursor("^", "^", 1)

    def apply_subscript(self):
        """Apply subscript formatting (~text~)"""
        self._wrap_selection_or_cursor("~", "~", 1)

    def apply_block_quote(self):
        """Apply block quote formatting (> text)"""
        self._add_line_prefix(">")

    def apply_code_block(self):
        """Apply code block formatting (tab indentation)"""
        self._add_line_prefix("\t")

    def apply_bullet_list(self):
        """Apply bullet list formatting (- text)"""
        self._add_line_prefix("- ")

    def apply_numbered_list(self):
        """Apply numbered list formatting (1. text, 2. text, etc.)"""
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()
            start_line = start.get_line()
            end_line = end.get_line()
            i = 1
            line_number = start_line
            while line_number <= end_line:
                temp_iter = self.text_buffer.get_iter_at_line(line_number)
                self.text_buffer.insert(temp_iter, str(i) + ". ")
                line_number += 1
                i += 1
        else:
            temp_iter = self.text_buffer.get_iter_at_mark(self.text_buffer.get_insert())
            line_number = temp_iter.get_line()
            start_iter = self.text_buffer.get_iter_at_line(line_number)
            self.text_buffer.insert(start_iter, "1. ")

    def apply_heading(self, level):
        """
        Apply heading formatting (# text, ## text, etc.)

        Args:
            level: Heading level (1-6)
        """
        if level < 1 or level > 6:
            raise ValueError("Heading level must be between 1 and 6")

        # Get iters for start and end of line at cursor
        temp_iter = self.text_buffer.get_iter_at_mark(self.text_buffer.get_insert())
        line_number = temp_iter.get_line()
        start_iter = self.text_buffer.get_iter_at_line(line_number)
        end_iter = self.text_buffer.get_iter_at_line(line_number)
        end_iter.forward_to_line_end()

        # Get the text on the current line and check if there is already a heading
        text = self.text_buffer.get_text(start_iter, end_iter, True)

        if len(text) == 0:
            # This line is empty, add the #'s
            text = ("#" * level) + " "
        elif text.lstrip() and text.lstrip()[0] == "#":
            # This line is already a heading. Remove #'s and replace with new #'s
            text_without_heading = "".join(re.split("^#+", text)).lstrip()
            text = ("#" * level) + " " + text_without_heading
        else:
            # This line doesn't already have a heading, simple prepend #'s
            text = ("#" * level) + " " + text

        # Replace text with new heading character(s)
        self.text_buffer.delete(start_iter, end_iter)
        self.text_buffer.insert(start_iter, text)

    def insert_horizontal_rule(self):
        """Insert horizontal rule (---)"""
        if not self.text_buffer.get_has_selection():
            self.text_buffer.insert_at_cursor("\n***\n")
        else:
            selection_bounds = self.text_buffer.get_selection_bounds()
            mark_end = self.text_buffer.create_mark(None, selection_bounds[1], False)
            self.text_buffer.insert(self.text_buffer.get_iter_at_mark(mark_end), "\n***\n")

    def insert_timestamp(self):
        """Insert current timestamp"""
        text = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p") + " "
        self.text_buffer.insert_at_cursor(text + "\n")

    def insert_link(self, alt_text, url):
        """
        Insert markdown link [alt_text](url)

        Args:
            alt_text: Link text
            url: Link URL
        """
        link = f"[{alt_text}]({url}) "

        # Delete highlighted text before inserting the link if there's a selection
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()
            self.text_buffer.delete(start, end)

        self.text_buffer.insert_at_cursor(link)

    def insert_image(self, alt_text, url, title=None):
        """
        Insert markdown image ![alt_text](url "title")

        Args:
            alt_text: Image alt text
            url: Image URL/path
            title: Optional image title
        """
        if title:
            link = f'![{alt_text}]({url}  "{title}")'
        else:
            link = f"![{alt_text}]({url}) "

        self.text_buffer.insert_at_cursor(link)

    def create_table(self, rows, columns):
        """
        Create a markdown table

        Args:
            rows: Number of rows
            columns: Number of columns
        """
        if rows <= 0 or columns <= 0:
            return

        table_str = ""
        line = ("|  " * columns) + "|"
        header_line = ("|--" * columns) + "|"

        table_str = line + "\n" + header_line + "\n"
        if rows > 1:
            remaining_rows = rows - 1
            while remaining_rows > 0:
                table_str += line + "\n"
                remaining_rows -= 1

        self.text_buffer.insert_at_cursor(table_str)
