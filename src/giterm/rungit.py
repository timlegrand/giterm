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
        for line in commit:
            text = []
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
                text.append(line)
        message = [x for x in text if x][0].lstrip()
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
    return data


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
    print git_branches()
    print git_stashes()
    print git_remotes()
    print git_submodules()
    print git_tags()
    print git_diff(path='rungit.py')
