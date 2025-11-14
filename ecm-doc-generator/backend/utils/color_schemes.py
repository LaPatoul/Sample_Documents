"""
Color schemes for document layouts
Different professional color palettes for variety in generated documents
"""
import random

# Professional color schemes
COLOR_SCHEMES = {
    'blue_professional': {
        'name': 'Blue Professional',
        'primary': (41, 98, 255),      # Royal Blue
        'secondary': (33, 78, 204),    # Darker Blue
        'accent': (102, 153, 255),     # Light Blue
        'text_dark': (33, 37, 41),     # Almost Black
        'text_light': (108, 117, 125), # Gray
        'background': (248, 249, 250), # Very Light Gray
    },
    'green_corporate': {
        'name': 'Green Corporate',
        'primary': (16, 124, 16),      # Forest Green
        'secondary': (11, 87, 11),     # Dark Green
        'accent': (76, 175, 80),       # Light Green
        'text_dark': (33, 37, 41),
        'text_light': (96, 108, 96),
        'background': (245, 250, 245),
    },
    'burgundy_classic': {
        'name': 'Burgundy Classic',
        'primary': (136, 14, 79),      # Burgundy
        'secondary': (97, 10, 56),     # Dark Burgundy
        'accent': (194, 24, 91),       # Pink/Red
        'text_dark': (33, 37, 41),
        'text_light': (117, 108, 108),
        'background': (252, 245, 248),
    },
    'teal_modern': {
        'name': 'Teal Modern',
        'primary': (0, 121, 107),      # Teal
        'secondary': (0, 77, 64),      # Dark Teal
        'accent': (38, 166, 154),      # Light Teal
        'text_dark': (33, 37, 41),
        'text_light': (96, 125, 139),
        'background': (240, 252, 251),
    },
    'purple_executive': {
        'name': 'Purple Executive',
        'primary': (103, 58, 183),     # Deep Purple
        'secondary': (81, 45, 168),    # Darker Purple
        'accent': (149, 117, 205),     # Light Purple
        'text_dark': (33, 37, 41),
        'text_light': (117, 108, 125),
        'background': (248, 245, 252),
    },
    'orange_dynamic': {
        'name': 'Orange Dynamic',
        'primary': (230, 81, 0),       # Deep Orange
        'secondary': (191, 54, 12),    # Darker Orange
        'accent': (255, 138, 101),     # Light Orange
        'text_dark': (33, 37, 41),
        'text_light': (117, 101, 96),
        'background': (255, 248, 240),
    },
}


def get_color_scheme(scheme_name=None):
    """
    Get a color scheme by name, or a random one if name is None

    Args:
        scheme_name: Name of the scheme, or None for random

    Returns:
        Dictionary with color scheme
    """
    if scheme_name and scheme_name in COLOR_SCHEMES:
        return COLOR_SCHEMES[scheme_name]

    # Return a random scheme
    return random.choice(list(COLOR_SCHEMES.values()))


def get_random_scheme_name():
    """Get a random color scheme name"""
    return random.choice(list(COLOR_SCHEMES.keys()))


def rgb_to_hex(rgb):
    """Convert RGB tuple to hex color string"""
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])


def get_scheme_for_html(scheme):
    """
    Convert a color scheme to CSS-friendly hex values

    Args:
        scheme: Color scheme dictionary with RGB tuples

    Returns:
        Dictionary with hex color strings
    """
    return {
        'name': scheme['name'],
        'primary': rgb_to_hex(scheme['primary']),
        'secondary': rgb_to_hex(scheme['secondary']),
        'accent': rgb_to_hex(scheme['accent']),
        'text_dark': rgb_to_hex(scheme['text_dark']),
        'text_light': rgb_to_hex(scheme['text_light']),
        'background': rgb_to_hex(scheme['background']),
    }
