# -*- coding: utf-8 -*-
import subprocess
import os

import textutils


def run(cmd):
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0].split('\n')
    code = process.returncode
    return [x for x in output if x]


def run_with_error_code(cmd):
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0].split('\n')
    code = process.returncode
    # if code:
    #     raise Exception('Command "{0}" returned code {1}.'.format(cmd, str(code)))
    return [x for x in output if x], code


def check_is_git_repository():
    output, error = run_with_error_code('git rev-parse --git-dir')
    if error:
        raise NotAGitRepositoryException('Please cd in a Git repository first.')

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
        sha1 = commit[0].split()[1]
        main = commit[0].split('(', 1)
        branches = '(' + main[1] + ' ' if len(main) == 2 else ''
        author = commit[1].split(' ', 1)[1].lstrip()
        date = commit[2].split(' ', 1)[1].lstrip()
        message = [x for x in commit[3:] if x][0].lstrip()
        line = branches + message + ' ' + author + ' ' + date + ' ' + sha1
        output.append(line)
    return output


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
    hunks = textutils.blocks(data, lambda x: x and x.startswith('@@'))
    screen_content = []
    for h in hunks:
        screen_content += textutils.remove_superfluous_alineas(h)
        screen_content.append('─' * 80)
    return screen_content


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


class NotAGitRepositoryException(Exception):
    pass


if __name__ == '__main__':
    print check_is_git_repository()
    print git_changed()
    print git_staged()
    print git_history()
    print git_hierarchies()
    for line in git_diff(path='rungit.py'):
        print line
