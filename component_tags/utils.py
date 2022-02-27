# -*- coding: utf-8 -*-
import re
from copy import copy

from django.utils import six


class TemplateConstant(object):
    """
    A 'constant' internal template variable which basically allows 'resolving'
    returning it's initial value
    """
    def __init__(self, value):
        self.literal = value
        if isinstance(value, six.string_types):
            self.value = value.strip('"\'')
        else:
            self.value = value

    def __repr__(self):  # pragma: no cover
        return '<TemplateConstant: %s>' % repr(self.value)

    def resolve(self, context):
        value_in_context = None
        try:
            return context[self.value]
        except KeyError:
            try:
                return eval(self.value)
            except (TypeError, NameError, SyntaxError):
                return self.value



def get_default_name(name):
    """
    Turns "CamelCase" into "camel_case"
    """
    _re1 = re.compile('(.)([A-Z][a-z]+)')
    _re2 = re.compile('([a-z0-9])([A-Z])')
    return _re2.sub(r'\1_\2', _re1.sub(r'\1_\2', name)).lower()


def mixin(parent, child, attrs=None):
    attrs = attrs or {}
    return type(
        '%sx%s' % (parent.__name__, child.__name__),
        (child, parent),
        attrs
    )
