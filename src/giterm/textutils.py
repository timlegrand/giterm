# -*- coding: utf-8 -*-
import locale


locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()


def shorten(string, size, dots=True):
    printable = string.decode(code)
    # Is that really efficient? Shouldn't we store the raw data
    # in self.content instead?
    if len(printable) > size:
        if dots:
            printable = printable[:size - 3] + '...'
        else:
            printable = printable[:size]
    return printable.encode(code), len(string)


def blocks(iterable, start_pattern):
    block = []
    for line in iterable:
        if start_pattern(line):
            if block:
                yield block
                block = []
        block.append(line)
    if block:
        yield block


def remove_superfluous_alineas(hunk):
    min_alinea = 1000
    for i, line in enumerate(hunk[1:]):
        line = tabs_to_spaces(line, num_spaces=2)
        hunk[i + 1] = line
        min_alinea = get_new_minimum_alinea(line, min_alinea, 1)
    left_aligned_hunk = lstrip_hunk(hunk, min_alinea)
    return left_aligned_hunk


def tabs_to_spaces(text, num_spaces=2):
    return (num_spaces * ' ').join(text.split('\t'))


def get_new_minimum_alinea(line, previous_alinea, num_ignored_chars):
    line = line[1:]  # First char is diff-specific ('+' or '-' chars)
    lstripped_length = len(line.lstrip())
    if lstripped_length != 0:
        curr_alinea = len(line) - lstripped_length
        min_alinea = min(previous_alinea, curr_alinea)
        return min_alinea
    return previous_alinea


def lstrip_hunk(text, offset):
    '''Left-shifts of 'offset' chars every line of a given 'text',
    but saves the first character (typically '+' or '-' in diff output).
    '''
    result = []
    result.append(text[0])
    for line in text[1:]:
        result.append(line[0] + line[offset + 1:])
    return result
