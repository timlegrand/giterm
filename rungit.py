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
        path = line.split()[1]
        full_code = line[0:2]
        if staged:
            code = full_code[0]
        else:
            code = full_code[1]
        if code in 'CRADUM':
            data.append(line)
        elif code in ' ':
            pass
        elif code in '?!':
            if not staged:
                if os.path.isdir(path):
                    paths = run('find %s -type f' % path)
                    data += [full_code + ' ' + x for x in paths]
                else:
                    data.append(line)
        else:
            data.append('X' + line)
    return data


def git_changed():
    return git_status(False)


def git_staged():
    return git_status(True)


def git_history():
    data = run('git log --abbrev-commit --decorate --date=iso')
    commits = blocks(data, lambda x: x and x[:6] == 'commit')
    output = []
    for commit in commits:
        sha1 = commit[0].split()[1]
        main = commit[0].split('(', 1)
        branches = '(' + main[1] + ' ' if len(main) == 2 else ''
        author = commit[1].split(' ', 1)[1].lstrip()
        date = commit[2].split(' ', 1)[1].lstrip()
        message = [x for x in commit[3:] if x][0].lstrip()
        line = branches + message + ' ' + author + ' ' + date + ' ' + sha1
        output.append(line)
    return output


def blocks(iterable, start_pattern):
    accumulator= []
    for line in iterable:
        if start_pattern(line):
            if accumulator:
                yield accumulator
                accumulator= []
        accumulator.append(line)
    if accumulator:
        yield accumulator


def git_hierarchies():
    data = git_branches()
    data += git_stashes()
    data += git_remotes()
    data += git_submodules()
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


def git_diff(path):
    if not path or type(path) is not str:
        raise Exception('Path not supported: ' + str(path))
    data = run('git diff -- %s' % path)[4:]
    if not data:
        data = run('git diff -- /dev/null %s' % path)[5:]
    hunks = blocks(data, lambda x: x and x.startswith('@@'))
    screen_content = []
    for h in hunks:
        screen_content += remove_superfluous_alineas(h)
        screen_content.append('─' * 80)
    return screen_content


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
