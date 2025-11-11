"""CSS style declarations for markdown rendering."""

import os
from reremarkable_lib import reremarkableconfig

# Available style names mapped to their CSS filenames
AVAILABLE_STYLES = {
    'dark': 'dark.css',
    'foghorn': 'foghorn.css',
    'github': 'github-markdown.css',
    'github_dark': 'github-markdown-dark.css',
    'github_light': 'github-markdown-light.css',
    'handwriting': 'handwriting.css',
    'markdown': 'markdown.css',
    'metro_vibes': 'metro_vibes.css',
    'metro_vibes_dark': 'metro_vibes_dark.css',
    'modern': 'modern.css',
    'screen': 'screen.css',
    'solarized_dark': 'solarized_dark.css',
    'solarized_light': 'solarized_light.css',
}

# Github is the default style applied to the markdown
__current_style = 'github'
__rtl = False
__css_cache = {}


def _get_css_directory():
    """Get the CSS files directory path."""
    try:
        data_path = reremarkableconfig.get_data_path()
        return os.path.join(data_path, 'media', 'css')
    except Exception:
        # Fallback for development/testing
        return os.path.join(os.path.dirname(__file__), '..', 'data', 'media', 'css')


def _load_css_file(style_name):
    """Load CSS content from file.

    Args:
        style_name: Name of the style to load

    Returns:
        CSS content as string, or empty string if file not found
    """
    if style_name not in AVAILABLE_STYLES:
        return ''

    # Check cache first
    if style_name in __css_cache:
        return __css_cache[style_name]

    css_dir = _get_css_directory()
    css_file = os.path.join(css_dir, AVAILABLE_STYLES[style_name])

    try:
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read().strip()
            __css_cache[style_name] = css_content
            return css_content
    except (IOError, OSError) as e:
        print(f"Warning: Could not load CSS file {css_file}: {e}")
        return ''


def set_style(style_name):
    """Set the current CSS style.
    
    Args:
        style_name: Name of the style to set as current
    """
    global __current_style
    if style_name in AVAILABLE_STYLES:
        __current_style = style_name
    else:
        print(f"Warning: Unknown style '{style_name}', keeping current style '{__current_style}'")


def get_current_style():
    """Get the current CSS style.
    
    Returns:
        Current CSS style string, with RTL direction if enabled
    """
    css = _load_css_file(__current_style)
    
    if __rtl and css:
        css += ' body { direction: rtl; }'
    
    return css


def get_available_styles():
    """Get list of available style names.
    
    Returns:
        List of available style names
    """
    return list(AVAILABLE_STYLES.keys())


def rtl(enabled=None):
    """Get or set RTL (right-to-left) text direction.
    
    Args:
        enabled: Boolean to enable/disable RTL, or None to get current state
        
    Returns:
        Current RTL state if enabled is None
    """
    global __rtl
    
    if enabled is None:
        return __rtl
    
    __rtl = bool(enabled)


def clear_cache():
    """Clear the CSS cache to force reloading from files."""
    global __css_cache
    __css_cache.clear()


# Legacy function names for backward compatibility
def set(style_input):
    """Legacy function: Set the current CSS style.
    
    Args:
        style_input: Either a style name (str) or CSS content (str).
                    If CSS content is provided, it will be mapped back to the style name.
    """
    # Check if this is CSS content or a style name
    if isinstance(style_input, str) and len(style_input) > 50 and style_input.startswith('/**** '):
        # This looks like CSS content, extract the style name from the comment
        try:
            # Look for pattern: /**** style_name.css ***/
            if '.css ***/' in style_input[:100]:
                start = style_input.find('/**** ') + 6
                end = style_input.find('.css ***/')
                if start < end:
                    extracted_name = style_input[start:end]
                    if extracted_name in AVAILABLE_STYLES:
                        set_style(extracted_name)
                        return
            # If extraction failed, fall back to exact match
            for style_name in AVAILABLE_STYLES:
                if _load_css_file(style_name) == style_input:
                    set_style(style_name)
                    return
            print(f"Warning: Could not map CSS content to style name")
        except Exception as e:
            print(f"Warning: Error processing CSS content: {e}")
    else:
        # This is likely a style name, use it directly
        set_style(style_input)


def get():
    """Legacy function: Get the current CSS style."""
    return get_current_style()


# Legacy module attributes for backward compatibility
# These provide the old direct access to CSS content
def __getattr__(name):
    """Provide backward compatibility for direct CSS access like styles.github."""
    if name in AVAILABLE_STYLES:
        return _load_css_file(name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Initialize module-level variables for all available styles
# This provides direct attribute access for backward compatibility
def _initialize_style_attributes():
    """Initialize module-level variables for CSS styles."""
    import sys
    current_module = sys.modules[__name__]
    
    for style_name in AVAILABLE_STYLES:
        # Create a property-like object that loads CSS when accessed
        def _make_css_getter(style):
            def _get_css():
                return _load_css_file(style)
            return _get_css
        
        # Set the CSS content as a module attribute
        setattr(current_module, style_name, _load_css_file(style_name))

# Initialize style attributes on module import
_initialize_style_attributes()
