# -*- coding: utf-8 -*-
from copy import copy, deepcopy

from django import template

from .arguments import Argument, Flag, KeywordArgument
from .exceptions import ArgumentRequiredError, TooManyArguments


class Parser(object):
    """
    Argument parsing class. A new instance of this gets created each time a tag
    gets parsed.
    """
    def __init__(self, options):
        self.options = options#.bootstrap()

    def parse(self, parser, tokens):
        """
        Parse a token stream
        """
        self.parser = parser
        self.bits = tokens.split_contents()
        self.tagname = self.bits.pop(0)
        self.kwargs = {}
        self.blocks = {}
        self.arguments = copy(self.options.arguments)

        # get a copy of the bits (tokens)
        self.todo = list(self.bits)
        # parse the bits (tokens)
        self.parse_kwargs()

        # parse block tags
        self.parse_blocks()
        return self.kwargs, self.blocks

    def parse_kwargs(self):
        kwargs_arguments = []
        flag_arguments = []
        args_arguments = []

        for a in self.arguments:
            if isinstance(a, Flag):
                flag_arguments.append(a)
            elif isinstance(a, KeywordArgument):
                kwargs_arguments.append(a)
            else:
                args_arguments.append(a)

        bits = self.todo

        for a in kwargs_arguments:
            for b in bits:
                if b.startswith(a.name):
                    try:
                        key, value = b.split('=', 1)
                        if key == a.name:
                            self.todo.remove(b)
                            a.parse(self.parser, value, self.kwargs)
                            break
                    except ValueError:
                        pass
            if not a.name in self.kwargs.keys():
                if a.required:
                    raise ArgumentRequiredError(a, self.tagname)
                if a.default != None:
                    a.parse(self.parser, a.default, self.kwargs)

        bits = self.todo
        for a in flag_arguments:
            for b in bits:
                if b.startswith(a.name):
                    try:
                        key, value = b.split('=', 1)
                        if key == a.name:
                            self.todo.remove(b)
                            a.parse(self.parser, value, self.kwargs)
                            break
                        else:
                            continue
                    except ValueError:
                        if b == a.name:
                            a.parse(self.parser, 'True', self.kwargs)
                            self.todo.remove(b)
                            break
            if not a.name in self.kwargs.keys():
                a.parse(self.parser, False, self.kwargs)

        bits = self.todo
        nb_bits = len(bits)
        nb_args = len(args_arguments)
        if nb_args < nb_bits:
            raise TooManyArguments(self.tagname, [ bits[i] for i in range(nb_args, nb_bits) ])
        else:
            for i in range(nb_bits):
                args_arguments[i].parse( self.parser, bits[i], self.kwargs)
            if nb_args > nb_bits:
                for i in range(nb_bits, nb_args):
                    current_arg = args_arguments[i]
                    if current_arg.required:
                        raise ArgumentRequiredError(current_arg, self.tagname)
                    elif current_arg.default:
                        current_arg.parse(self.parser, current_arg.default, self.kwargs)

    def parse_blocks(self):
        """
        Parse template blocks for block tags.
        Example:
            {% a %} b {% c %} d {% e %} f {% g %}
             => pre_c: b
                pre_e: d
                pre_g: f
            {% a %} b {% f %}
             => pre_c: b
                pre_e: None
                pre_g: None
        """
        # if no blocks are defined, bail out
        if not self.options.blocks:
            return
        # copy the blocks
        blocks = deepcopy(self.options.blocks)
        identifiers = {}
        for block in blocks:
            identifiers[block] = block.names
        while blocks:
            current_block = blocks.pop(0)
            current_identifiers = identifiers[current_block]
            block_identifiers = list(current_identifiers)
            for block in blocks:
                block_identifiers += identifiers[block]
            nodelist = self.parser.parse(block_identifiers)
            token = self.parser.next_token()
            while token.contents not in current_identifiers:
                empty_block = blocks.pop(0)
                current_identifiers = identifiers[empty_block]
                self.blocks[empty_block.alias] = template.NodeList()
            self.blocks[current_block.alias] = nodelist

