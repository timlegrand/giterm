# -*- coding: utf-8 -*-


class ArgumentException(Exception):
    pass


class NotAGitRepositoryException(Exception):
    pass


class GitNotFoundException(Exception):
    pass


class CommandErrorException(Exception):
    pass
