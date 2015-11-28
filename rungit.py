# -*- coding: utf-8 -*-
import subprocess


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
    data2 = []
    # Convert tabs to spaces (2 spaces per tab)
    for line in data[4:]:
        data2.append((2 * ' ').join(line.split('\t')))
    return data2


if __name__ == '__main__':
    print git_changed()
    print git_staged()
    print git_history()
    print git_hierarchies()
    print git_diff(path='panel.py')
