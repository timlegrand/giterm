# -*- coding: utf-8 -*-
import commands
import os

import textutils

from exception import *


def run(cmd):
    code, output = commands.getstatusoutput(cmd)
    return code, [x for x in output.split('\n') if x]


def git_root_path():
    error, output = run('git rev-parse --show-toplevel')
    if error:
        if error == 32512:
            raise GitNotFoundException(
                'Git not found. Please install Git first.')
        else:
            raise NotAGitRepositoryException(
                'Please cd in a Git repository first.')
    return output[0]


def git_status(staged=False):
    error, output = run('git status -s --porcelain')
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
                    error, paths = run('find %s -type f' % path)
                    data += [full_code + ' ' + x for x in paths]
                else:
                    data.append(line)
        else:
            data.append('X' + line)
    return data


def git_changed():
    return git_status(staged=False)


def git_staged():
    return git_status(staged=True)


def git_history():
    error, data = run('git log --abbrev-commit --decorate --date=iso')
    commits = textutils.blocks(data, lambda x: x and x[:6] == 'commit')
    output = []
    for commit in commits:
        text = []
        for line in commit:
            if line.startswith('commit'):
                sha1 = line.split()[1]
                main = line.split('(', 1)
                labels = ''
                if len(main) == 2:
                    labels = main[1].split(')', 1)[0]
                    labels = labels.split(', ')
            elif line.startswith('Author'):
                author = line.split(' ', 1)[1].lstrip()
            elif line.startswith('Date'):
                date = line.split(' ', 1)[1].lstrip()
            elif line.startswith('Merge'):
                pass
            else:
                text.append(line.lstrip())
        message = ' | '.join([x for x in text if x])
        history_line = [labels, message, author, date, sha1]
        output.append(history_line)
    return output


def git_branches():
    error, data = run('git branch')
    for i, line in enumerate(data):
        data[i] = line[2:] if line[0] != '*' else '*' + line[2:]
    return data


def git_stashes():
    error, data = run('git stash list')
    for i, line in enumerate(data):
        data[i] = line[14:]
    return data


def git_remotes():
    error, data = run('git remote show')
    return data


def git_submodules():
    error, data = run('git submodule status')
    for i, line in enumerate(data):
        data[i] = line.split()[1]
    return data


def git_tags():
    error, data = run('git tag')
    # If Git >= 2.3.3:
    # git log --date-order --tags --simplify-by-decoration --pretty=format:"%d"
    return data


def git_diff(path, cached=False):
    if not path or type(path) is not str:
        raise Exception('Path not supported: ' + str(path))

    opt = '--cached' if cached else ''
    cmd = 'git diff {} -- {}'.format(opt, path)
    error, data = run(cmd)
    if not data:
        cmd = 'git diff -- /dev/null %s' % path
        error, data = run(cmd)
        if data:
            data = data[5:]
            error = 0
    else:
        data = data[4:]
    if error:
        raise Exception('Error executing "' + cmd + '" (error = ' + str(error))
    hunks = list(textutils.blocks(data, lambda x: x and x.startswith('@@')))
    return hunks


def run_simple_command(command, path):
    if not path:
        raise ArgumentException('File name missing.')
    command = 'git %s -- %s' % (command, path)
    code, output = commands.getstatusoutput(command)
    if code != 0:
        raise Exception('Error %s while running "%s"' % (code, command))


def git_stage_file(path):
    run_simple_command('add', path)


def git_unstage_file(path):
    run_simple_command('reset', path)


if __name__ == '__main__':
    print git_root_path()
    print git_changed()
    print git_staged()
    print git_history()
    print git_branches()
    print git_stashes()
    print git_remotes()
    print git_submodules()
    print git_tags()
    print git_diff(path='src/giterm/rungit.py')
