# -*- coding: utf-8 -*-

class BlockDefinition(object):
    """
    Definition of 'parse-until-blocks' used by the parser.
    """
    def __init__(self, alias, *names):
        self.alias = alias
        self.names = names