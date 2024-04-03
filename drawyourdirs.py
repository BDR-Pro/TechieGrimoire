import os
from functools import cache

@cache
def draw_tree(levels, file_limit):
    """Print the directory tree with file size limits."""
    prefix = ' ' * 4
    return_string = ''
    path = os.path.expanduser('~')
    for root, dirs, files in os.walk(path, topdown=True):
        level = root.replace(path, '').count(os.sep)
        indent = prefix * level
        subindent = prefix * (level + 1)



        # Early exit for deep directories
        if level > levels:
            continue

        # Print current directory
        return_string+=('{}{}/'.format(indent, os.path.basename(root)))
        return_string+=('\n')
        # Filter and sort files by size
        filtered_files = [(f, os.path.getsize(os.path.join(root, f))) for f in files]
        sorted_files = sorted(filtered_files, key=lambda x: x[1], reverse=True)

        # Print files, respecting the file limit
        for i, (f, size) in enumerate(sorted_files, 1):
            if i > file_limit:
                return_string+=('{}|-- #####'.format(subindent))
                return_string+=('\n')
                break
            return_string+=('{}|-- {} ({} )'.format(subindent, f, calc_size(size)))
            return_string+=('\n')
    return return_string

def calc_size(size):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return '{:.2f} {}'.format(size, unit)


