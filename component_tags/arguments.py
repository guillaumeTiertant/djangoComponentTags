# -*- coding: utf-8 -*-
from django import template
from .exceptions import DuplicateArgument

from .utils import TemplateConstant, mixin
from .values import BooleanValue, ChoiceValue, Value


class Argument(object):
    """
    A basic single value argument.
    """
    def __init__(self, name, value_class=Value, default=None, required=True, resolve=True):
        self.name = name
        self.value_class = value_class
        self.default = default
        self.required = required
        self.resolve = resolve

    def __repr__(self):  # pragma: no cover
        return '<%s: %s>' % (self.__class__.__name__, self.name)

    def parse_token(self, parser, token):
        if self.resolve:
            return parser.compile_filter(token)
        else:
            return TemplateConstant(token)

    def parse(self, parser, token, kwargs):
        """
        Parse a token.
        """
        if self.name in kwargs:
            raise DuplicateArgument(self, parser.tagname)
        else:
            value = self.parse_token(parser, token)
            kwargs[self.name] = self.value_class(value)
            return True


class KeywordArgument(Argument):
    def __init__(self, name, choices=None, value_class=Value, default=None, required=True, resolve=True):
        super(KeywordArgument, self).__init__(name, value_class=value_class, default=default, required=required, resolve=resolve)
        if choices:
            if default or not required:
                value_on_error = default
            else:
                value_on_error = choices[0]
            self.value_class = mixin(
                self.value_class,
                ChoiceValue,
                attrs={
                    'choices': choices,
                    'value_on_error': value_on_error,
                }
            )


class Flag(KeywordArgument):
    """
    A boolean flag
    """
    def __init__(self, name):
        super(Flag, self).__init__(name, choices=[False, True], value_class=BooleanValue, default=False, required=False)