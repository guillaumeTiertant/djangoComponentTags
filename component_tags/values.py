# -*- coding: utf-8 -*-
import warnings

from django import template
from django.conf import settings
from django.utils import six

from .exceptions import TemplateSyntaxWarning


class Value(object):
    errors = {}
    value_on_error = ""

    def __init__(self, var):
        self.var = var
        try:
            # django.template.base.Variable
            self.literal = self.var.literal
        except AttributeError:
            # django.template.base.FilterExpression
            self.literal = self.var.token

    def resolve(self, context):
        resolved = self.var.resolve(context)
        return self.clean(resolved)

    def clean(self, value):
        return value

    def error(self, value, category):
        data = self.get_extra_error_data()
        data['value'] = repr(value)
        message = self.errors.get(category, "") % data
        if settings.DEBUG:
            raise template.TemplateSyntaxError(message)
        else:
            warnings.warn(message, TemplateSyntaxWarning)
            return self.value_on_error

    def get_extra_error_data(self):
        return {}


class StringValue(Value):
    errors = {
        "clean": "%(value)s could not be converted to string",
    }
    value_on_error = ""

    def clean(self, value):
        try:
            return str (value)
        except (ValueError, TypeError): # pragma: no cover
            return self.error(value, "clean")


class StrictStringValue(Value):
    errors = {
        "clean": "%(value)s is not a string",
    }
    value_on_error = ""

    def clean(self, value):
        if not isinstance(value, six.string_types):
            return self.error(value, "clean")
        return value


class IntegerValue(Value):
    errors = {
        "clean": "%(value)s could not be converted to Integer",
    }
    value_on_error = 0

    def clean(self, value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return self.error(value, "clean")


class BooleanValue(Value):
    errors = {
        "clean": "%(value)s could not be converted to Boolean",
    }
    value_on_error = False

    def clean(self, value):
        try:
            return bool(value)
        except (ValueError, TypeError): # pragma: no cover
            return self.error(value, "clean")


class FloatValue(Value):
    errors = {
        "clean": "%(value)s could not be converted to Boolean",
    }
    value_on_error = 0

    def clean(self, value):
        try:
            return float(value)
        except (ValueError, TypeError):
            return self.error(value, "clean")


class IterableValue(Value):
    errors = {
        "clean": "%(value)s is not iterable",
    }

    value_on_error = []

    def clean(self, value):
        try:
            iter(value)
            return value
        except (ValueError, TypeError):
            return self.error(value, "clean")


class ListValue(Value):
    errors = {
        "clean": "%(value)s is not a list",
    }

    value_on_error = []

    def clean(self, value):
        if not isinstance(value, list):
            return self.error(value, "clean")
        return value


class DictValue(Value):
    errors = {
        "clean": "%(value)s is not a dictionnary",
    }

    value_on_error = {}

    def clean(self, value):
        if not isinstance(value, dict):
            return self.error(value, "clean")
        return value


class ChoiceValue(Value):
    errors = {
        "choice": "%(value)s is not a valid choice. Valid choices: "
                  "%(choices)s.",
    }
    choices = []

    def clean(self, value):
        cleaned = super(ChoiceValue, self).clean(value)
        if cleaned in self.choices:
            return cleaned
        else:
            return self.error(cleaned, "choice")

    def get_extra_error_data(self):
        data = super(ChoiceValue, self).get_extra_error_data()
        data['choices'] = self.choices
        return data
