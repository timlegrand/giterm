# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import sys
import shlex

import giterm.textutils as textutils
import giterm.exception as ex
import git

global repo

getstatusoutput = None

# With Python3 subprocess
if sys.version_info[0] >= 3:
    import subprocess

    def get_status_output(*args, **kwargs):
        cmd = shlex.split(str(args[0])) if len(args) == 1 else args
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        return p.returncode, stdout.decode('utf-8')

    getstatusoutput = get_status_output

# With Python2 commands
else:
    import commands

    def get_status_output(*args, **kwargs):
        return commands.getstatusoutput(*args, **kwargs)

    getstatusoutput = get_status_output

def create_repo(wd=os.getcwd()):
    global repo

    repo = git.Repo(wd)

def run(cmd):
    code, output = getstatusoutput(cmd)
    return code, [x for x in output.split('\n') if x]


def git_root_path():
    try:
        error, output = run('git rev-parse --show-toplevel')
    except Exception.FileNotFoundError:
        raise ex.GitNotFoundException(
            'Git not found. Please install Git first.')
    if error:
        if error == 32512:
            raise ex.GitNotFoundException(
                'Git not found. Please install Git first.')
        else:
            raise ex.NotAGitRepositoryException(
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
    global repo

    try:
        data = repo.git.diff('--', path, cached=cached, minimal=True)
        return (False, list(textutils.blocks(data.split('\n'), lambda x: x and x.startswith('@@'))))
    except Exception as e:
        return (True, str(e))

def run_simple_command(command, path):
    if not path:
        raise ex.ArgumentException('File name missing.')
    command = 'git %s -- %s' % (command, path)
    code, output = getstatusoutput(command)
    if code != 0:
        raise Exception('Error %s while running "%s"' % (code, command))

def git_stage_file(path):
    run_simple_command('add', path)

def git_unstage_file(path):
    run_simple_command('reset', path)

def git_checkout_branch(branch):
    global repo
    
    try:
        output = repo.git.checkout(branch)
        return (False, output)
    except Exception as e:
        return (True, str(e))

def git_commit(msg, amend=False):
    global repo

    try:
        output = repo.git.commit(m=msg, amend=amend)
        return (False, output)
    except Exception as e:
        return (True, str(e))

if __name__ == '__main__':
    print(git_root_path())
    print(git_changed())
    print(git_staged())
    print(git_history())
    print(git_branches())
    print(git_stashes())
    print(git_remotes())
    print(git_submodules())
    print(git_tags())
    print(git_diff(path='src/giterm/rungit.py'))
