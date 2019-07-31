"""Utility functions for the bmondata package.
"""

def csnl_to_list(csnl_str):
    """Converts a comma-separated and new-line separated string into
    a list, stripping whitespace from both ends of each item.  Does not
    return any zero-length strings.
    """
    s = csnl_str.replace('\n', ',')
    return [it.strip() for it in s.split(',') if it.strip()]

def split_strip(s, delim=','):
    """Converts a delimited string into a list, stripping whitespace 
    from both ends of each item.  Does not return any zero-length strings.
    'delim' is the delimiter.
    """
    return [it.strip() for it in s.split(',') if it.strip()]
