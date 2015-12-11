# -*- coding: utf-8 -*-
import subprocess
import os


def run(cmd):
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0].split('\n')
    return [x for x in output if x]


def git_status(staged=False):
    output = run('git status -s --porcelain')
    data = []
    for line in output:
        if staged:
            code = line[0:1]
        else:
            code = line[1:2]
        if code in 'CRADUM':
            data.append(line)
        elif code in ' ':
            pass
        elif code in '?!':
            if not staged:
                data.append(line)
        else:
            data.append('X' + line)

    return data


def git_changed():
    return git_status(False)


def git_staged():
    return git_status(True)


def git_history():
    data = run('git log --pretty=oneline --abbrev-commit --graph --decorate')
    return data


def git_branches():
    data = run('git branch')
    for i, line in enumerate(data):
        data[i] = line[2:] if line[0] != '*' else line[2:] + '*'
    indent(data, 2)
    data.insert(0, 'Branches:')
    return data + [' ']


def git_stashes():
    data = run('git stash list')
    for i, line in enumerate(data):
        data[i] = line[14:]
    indent(data, 2)
    data.insert(0, 'Stashes:')
    return data + [' ']


def git_remotes():
    data = run('git remote show')
    indent(data, 2)
    data.insert(0, 'Remotes:')
    return data + [' ']


def git_submodules():
    data = run('git submodule status')
    for i, line in enumerate(data):
        data[i] = line.split()[1]
    indent(data, 2)
    data.insert(0, 'Submodules:')
    return data + [' ']


def indent(data, n):
    for i, line in enumerate(data):
        data[i] = '└' + ' ' * (n-1) + line


def git_hierarchies():
    data = git_branches()
    data += git_stashes()
    data += git_remotes()
    data += git_submodules()
    return data


def git_diff(path):
    if not path:
        return []
    data = run('git diff -- %s' % path)
    if not data:
        data = run('git diff -- /dev/null %s' % path)
    hunks = chainsaw(data)
    screen_content = []
    for h in hunks:
        screen_content += remove_superfluous_alineas(h)
        screen_content.append('─' * 80)
    return screen_content


def chainsaw(data):
    '''Splits diff data into diff hunks.
    '''
    no_header = data[4:]
    hunks = []
    hunk = []
    for line in no_header:
        if line.startswith('@@'):  # New hunk
            if hunk:
                hunks.append(hunk)
                hunk = []
        hunk.append(line)
    if hunk:  # Last hunk if any
        hunks.append(hunk)
    return hunks


def remove_superfluous_alineas(hunk):
    min_alinea = 1000
    for i, line in enumerate(hunk[1:]):
        line = tabs_to_spaces(line, num_spaces=2)
        hunk[i+1] = line
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
        first_char = line[0]
        result.append(line[0] + line[offset+1:])
    return result


def run_simple_command(command, path):
    if not path:
        raise ArgumentException('Cannot stage without a file name.')
    command = 'git %s -- %s' % (command, path)
    with open(os.devnull, "w") as dev_null:
        error = subprocess.call(command.split(),
            stdout=dev_null, stderr=subprocess.STDOUT)
        if error != 0:
            raise Exception('Error %s while running "%s"' % (error, command))


def git_stage_file(path):
    run_simple_command('add', path)


def git_unstage_file(path):
    run_simple_command('reset', path)


if __name__ == '__main__':
    print git_changed()
    print git_staged()
    print git_history()
    print git_hierarchies()
    for line in git_diff(path='rungit.py'):
        print line
