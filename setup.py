#!/usr/bin/env python
from setuptools import setup

with open("requirements.txt") as f:
    required_packages = [l for l in f.read().splitlines() if not l.startswith("#")]

setup(
    name='giterm',
    version='0.2.0',
    description='A terminal-based, graphical user interface for Git',
    keywords='git, gui, terminal, console',
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
    install_requires=required_packages,
    entry_points={'console_scripts': ['giterm = giterm.giterm:_main']},
    )
