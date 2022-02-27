# -*- coding: utf-8 -*-
from django.template import TemplateSyntaxError

__all__ = ['ArgumentRequiredError', 'DuplicateArgument' 'TooManyArguments']


class BaseError(TemplateSyntaxError):
    template = ''

    def __str__(self):  # pragma: no cover
        return self.template % self.__dict__


class ArgumentRequiredError(BaseError):
    template = "The tag '%(tagname)s' requires the '%(argname)s' argument."

    def __init__(self, argument, tagname):
        self.argument = argument
        self.tagname = tagname
        self.argname = self.argument.name


class DuplicateArgument(BaseError):
    template = "The tag '%(tagname)s' got arguments with the same name: %(argname)s"

    def __init__(self, argument, tagname):
        self.argument = argument
        self.tagname = tagname
        self.argname = self.argument.name


class TooManyArguments(BaseError):
    template = "The tag '%(tagname)s' got too many arguments: %(extra)s"

    def __init__(self, tagname, extra):
        self.tagname = tagname
        self.extra = ', '.join(["'%s'" % e for e in extra])


class TemplateSyntaxWarning(Warning):
    """
    Used for variable cleaning TemplateSyntaxErrors when in non-debug-mode.
    """
