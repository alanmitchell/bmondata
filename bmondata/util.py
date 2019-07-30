"""Utility functions for the bmondata package.
"""

def cs_to_list(cs_str):
    """Converts a comma-separated and new-line separated string into
    a list.  Does not return any zero-length strings.
    """
    s = cs_str.replace('\n', ',')
    return [it.strip() for it in s.split(',') if it.strip()]
