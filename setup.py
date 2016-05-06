#!/usr/bin/env python
from setuptools import setup

exec(open('src/giterm/_version.py').read())

with open("requirements.txt") as f:
    required = [l for l in f.read().splitlines() if not l.startswith("#")]

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='giterm',
    version=__version__,
    description='A terminal-based GUI client for Git',
    long_description=long_description,
    keywords='git, client, terminal, console',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console :: Curses',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
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
