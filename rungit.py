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

def git_branch():
	data = run('git branch -a')
	return data

def git_diff(path):
	data = run('git diff -- %s' % path)
	return data[4:]

if __name__ == '__main__':
	print git_changed()
	print git_staged()
	print git_history()
	print git_branch()
	print git_diff(path='panel.py')
