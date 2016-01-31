# -*- coding: utf-8 -*-
import subprocess
import os

import textutils


class ArgumentException(Exception):
    pass


def run(cmd):
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0].split('\n')
    # code = process.returncode
    return [x for x in output if x]


def run_with_error_code(cmd):
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0].split('\n')
    code = process.returncode
    return [x for x in output if x], code


def git_root_path():
    output, error = run_with_error_code('git rev-parse --show-toplevel')
    if error or len(output) != 1:
        raise NotAGitRepositoryException(
            'Please cd in a Git repository first.')
    return output[0]


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
    return git_status(staged=False)


def git_staged():
    return git_status(staged=True)


def git_history():
    data = run('git log --abbrev-commit --decorate --date=iso')
    commits = textutils.blocks(data, lambda x: x and x[:6] == 'commit')
    output = []
    for commit in commits:
        text = []
        for line in commit:
            if line.startswith('commit'):
                sha1 = line.split()[1]
                main = line.split('(', 1)
                branches = '(' + main[1] if len(main) == 2 else ''
            elif line.startswith('Author'):
                author = line.split(' ', 1)[1].lstrip()
            elif line.startswith('Date'):
                date = line.split(' ', 1)[1].lstrip()
            elif line.startswith('Merge'):
                pass
            else:
                text.append(line.lstrip())
        message = ' | '.join([x for x in text if x])
        history_line = ' '.join([branches, message, author, date, sha1])
        output.append(history_line.lstrip())
    output[0] = '*' + output[0]
    return output


def git_branches():
    data = run('git branch')
    for i, line in enumerate(data):
        data[i] = line[2:] if line[0] != '*' else '*' + line[2:]
    return data


def git_stashes():
    data = run('git stash list')
    for i, line in enumerate(data):
        data[i] = line[14:]
    return data


def git_remotes():
    data = run('git remote show')
    return data


def git_submodules():
    data = run('git submodule status')
    for i, line in enumerate(data):
        data[i] = line.split()[1]
    return data


def git_tags():
    data = run('git tag')
    # If Git >= 2.3.3:
    # git log --date-order --tags --simplify-by-decoration --pretty=format:"%d"
    return data


def git_diff(path, cached=False):
    if not path or type(path) is not str:
        raise Exception('Path not supported: ' + str(path))

    opt = '--cached' if cached else ''
    cmd = 'git diff {} -- {}'.format(opt, path)
    data, error = run_with_error_code(cmd)
    if not data:
        cmd = 'git diff -- /dev/null %s' % path
        data, error = run_with_error_code(cmd)
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
    with open(os.devnull, "w") as dev_null:
        error = subprocess.call(command.split(),
                                stdout=dev_null, stderr=subprocess.STDOUT)
        if error != 0:
            raise Exception('Error %s while running "%s"' % (error, command))


def git_stage_file(path):
    run_simple_command('add', path)


def git_unstage_file(path):
    run_simple_command('reset', path)


class NotAGitRepositoryException(Exception):
    pass


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
    print git_diff(path='rungit.py')
