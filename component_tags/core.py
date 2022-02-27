# -*- coding: utf-8 -*-
from operator import attrgetter

from django.template import Node
from django.template.loader import render_to_string
from django.utils import six

from .arguments import Argument
from .blocks import BlockDefinition
from .parser import Parser
from .utils import get_default_name
from .registry import ComponentRegistry


class Options(object):
    """
    Option class holding the arguments of a tag.
    """
    def __init__(self, *options, **kwargs):
        self._options = options
        self._kwargs = kwargs
        self.arguments = [ attr for attr in options if isinstance(attr, Argument) ]
        self.all_argument_names = [ a.name for a in self.arguments ]
        self.parser_class = Parser

        self.blocks = []
        for block in kwargs.get('blocks', []):
            if isinstance(block, six.string_types):
                block_definition = BlockDefinition(block, block)
            else:
                block_definition = BlockDefinition(block[1], block[0])
            self.blocks.append(block_definition)

    def __repr__(self): # pragma: no cover
        arguments = ''
        if self.arguments:
            arguments = ','.join([a.__repr__() for a in self.arguments])

        blocks = ''
        if self.blocks:
            blocks = ';%s' % ','.join(map(attrgetter('alias'), self.blocks))

        return '<Options:%s%s>' % (arguments, blocks)

    def get_parser_class(self):
        return self.parser_class

    def parse(self, parser, tokens):
        """
        Parse template tokens into a dictionary
        """
        argument_parser_class = self.get_parser_class()
        argument_parser = argument_parser_class(self)
        return argument_parser.parse(parser, tokens)



class TagMeta(type):
    """
    Metaclass for the Tag class that set's the name attribute onto the class
    and a _decorated_function pseudo-function which is used by Django's
    template system to get the tag name.
    """
    def __new__(cls, name, bases, attrs):
        parents = [base for base in bases if isinstance(base, TagMeta)]
        if not parents:
            return super(TagMeta, cls).__new__(cls, name, bases, attrs)
        tag_name = str(attrs.get('name', get_default_name(name)))

        def fake_func():
            pass  # pragma: no cover

        fake_func.__name__ = tag_name
        attrs['_decorated_function'] = fake_func
        attrs['name'] = str(tag_name)
        return super(TagMeta, cls).__new__(cls, name, bases, attrs)


class Tag(TagMeta('TagMeta', (Node,), {})):
    """
    Main Tag class.
    """
    class Media:
        template = None
        css = []
        js = []
    
    CSS_TEMPLATE = '<link href="{}" type="text/css" rel="stylesheet" />'
    JS_TEMPLATE = '<script type="text/javascript" src="{}"></script>'

    options = Options()
    name = None

    def __init__(self, parser, tokens):
        self.kwargs, self.blocks = self.options.parse(parser, tokens)
        self.child_nodelists = []
        for key, value in self.blocks.items():
            setattr(self, key, value)
            self.child_nodelists.append(key)
        if not self.name in registry._registry.keys():
            registry.register(self)

    def render(self, context):
        """
        INTERNAL method to prepare rendering
        Usually you should not override this method, but rather use render_tag.
        """
        items = self.kwargs.items()
        blocks = self.blocks.items()
        kwargs = dict([(key, value.resolve(context)) for key, value in items])
        kwargs.update(self.blocks)
        for key, value in blocks:
            kwargs[key] = value.render(context)
        return self.render_tag(context, **kwargs)

    def render_tag(self, context, **kwargs):
        """
        The method you could override in your component tags
        """
        return render_to_string(self.Media.template, kwargs)

    @classmethod
    def render_dependencies(cls):
        dependencies = []
        for css_path in cls.Media.css:
            dependencies.append(cls.CSS_TEMPLATE.format(css_path))
        for js_path in cls.Media.js:
            dependencies.append(cls.JS_TEMPLATE.format(js_path))

        return dependencies

    def __repr__(self): # pragma: no cover
        return '<Tag: %s>' % self.name


registry = ComponentRegistry()
