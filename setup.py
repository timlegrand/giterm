#!/usr/bin/env python
from setuptools import setup

with open("requirements.txt") as f:
    required = [l for l in f.read().splitlines() if not l.startswith("#")]

setup(
    name='giterm',
    version='0.3.1',
    description='A terminal-based GUI client for Git',
    keywords='git, client, terminal, console',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console :: Curses',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Natural Language :: English',
        'Topic :: Software Development :: Version Control',
        ],
    author='Tim Legrand',
    author_email='timlegrand.perso+dev@gmail.com',
    url='https://github.com/timlegrand/giterm',
    download_url='https://github.com/timlegrand/giterm',
    license='BSD 2-Clause',
    packages=['giterm'],
    package_dir={'giterm': 'src/giterm'},
    install_requires=required,
    entry_points={'console_scripts': ['giterm = giterm.giterm:_main']},
    )
