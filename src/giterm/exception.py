# -*- coding: utf-8 -*-


class GitermException(Exception):
    pass


class ArgumentException(GitermException):
    pass


class NotAGitRepositoryException(GitermException):
    pass


class GitNotFoundException(GitermException):
    pass
