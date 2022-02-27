# -*- coding: utf-8 -*-
from unittest import TestCase

from django import template
from django.template import Context

from component_tags import arguments, core, exceptions, utils, values

from .context_managers import SettingsOverride, TemplateTags


class DummyTokens(list):
    def __init__(self, *tokens):
        # super(DummyTokens, self).__init__(['dummy_tag'] + list(tokens))
        super(DummyTokens, self).__init__(['dummy_tag'] + [str(t) for t in tokens])

    def split_contents(self):
        return self


class DummyParser(object):
    tagname = 'dummy_tag'

    @staticmethod
    def compile_filter(token):
        return utils.TemplateConstant(token)


dummy_parser = DummyParser()


class ComponentTagParserTests(TestCase):
    def test_parse_argument(self):
        options = core.Options(
            arguments.Argument('myarg'),
        )
        dummy_tokens = DummyTokens('myval')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')

        dummy_tokens = DummyTokens()
        with self.assertRaises(exceptions.ArgumentRequiredError):
            options.parse(dummy_parser, dummy_tokens)

    def test_parse_argument_not_resolved(self):
        options = core.Options(
            arguments.Argument('myarg', resolve=False),
        )
        dummy_tokens = DummyTokens('myval')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {'myarg': "foo"}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')

    def test_parse_arguments_with_same_name(self):
        options = core.Options(
            arguments.Argument('myarg'),
            arguments.Argument('myarg')
        )
        dummy_tokens = DummyTokens('foo', 'bar')

        with self.assertRaises(exceptions.DuplicateArgument):
            options.parse(dummy_parser, dummy_tokens)

    def test_parse_multi_argument(self):
        options = core.Options(
            arguments.Argument('myarg'),
            arguments.Argument('myarg2'),
        )
        dummy_tokens = DummyTokens('myval', 'myval2')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'myval2')

    def test_parse_too_many_arguments_should_not_pass(self):
        options = core.Options(
            arguments.Argument('myarg'),
        )
        dummy_tokens = DummyTokens('myval', 'myval2')

        with self.assertRaises(exceptions.TooManyArguments):
            options.parse(dummy_parser, dummy_tokens)

    def test_parse_argument_not_required_with_default_given(self):
        options = core.Options(
            arguments.Argument('myarg'),
            arguments.Argument('myarg2', required=False, default="foo"),
        )
        dummy_tokens = DummyTokens('myval', 'myval2')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'myval2')

    def test_parse_argument_not_required_with_default_not_given(self):
        options = core.Options(
            arguments.Argument('myarg'),
            arguments.Argument('myarg2', required=False, default='foo'),
        )
        dummy_tokens = DummyTokens('myval')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'foo')

    def test_parse_argument_not_required_without_default_given(self):
        options = core.Options(
            arguments.Argument('myarg'),
            arguments.Argument('myarg2', required=False),
        )
        dummy_tokens = DummyTokens('myval', 'myval2')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'myval2')

        options = core.Options(
            arguments.Argument('myarg'),
            arguments.Argument('myarg2', required=False, default=None),
        )
        dummy_tokens = DummyTokens('myval', 'myval2')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'myval2')

    def test_parse_argument_not_required_without_default_not_given(self):
        options = core.Options(
            arguments.Argument('myarg'),
            arguments.Argument('myarg2', required=False),
        )
        dummy_tokens = DummyTokens('myval')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')

        options = core.Options(
            arguments.Argument('myarg'),
            arguments.Argument('myarg2', required=False, default=None),
        )
        dummy_tokens = DummyTokens('myval')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')

    def test_parse_argument_required_with_default_given(self):
        options = core.Options(
            arguments.Argument('myarg'),
            arguments.Argument('myarg2', default="foo"),
        )
        dummy_tokens = DummyTokens('myval', 'myval2')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'myval2')

        options = core.Options(
            arguments.Argument('myarg'),
            arguments.Argument('myarg2', required=True, default="foo"),
        )
        dummy_tokens = DummyTokens('myval', 'myval2')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'myval2')

    def test_parse_argument_required_with_default_not_given_should_not_pass(self):
        options = core.Options(
            arguments.Argument('myarg'),
            arguments.Argument('myarg2', default='foo'),
        )
        dummy_tokens = DummyTokens('myval')
        with self.assertRaises(exceptions.ArgumentRequiredError):
            options.parse(dummy_parser, dummy_tokens)

        options = core.Options(
            arguments.Argument('myarg'),
            arguments.Argument('myarg2', required=True, default='foo'),
        )
        dummy_tokens = DummyTokens('myval')
        with self.assertRaises(exceptions.ArgumentRequiredError):
            options.parse(dummy_parser, dummy_tokens)

    def test_parse_argument_required_without_default_given(self):
        options = core.Options(
            arguments.Argument('myarg'),
            arguments.Argument('myarg2'),
        )
        dummy_tokens = DummyTokens('myval', 'myval2')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'myval2')

        options = core.Options(
            arguments.Argument('myarg'),
            arguments.Argument('myarg2', required=True, default=None),
        )
        dummy_tokens = DummyTokens('myval', 'myval2')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'myval2')

    def test_parse_argument_required_without_default_not_given_should_not_pass(self):
        options = core.Options(
            arguments.Argument('myarg'),
            arguments.Argument('myarg2'),
        )
        dummy_tokens = DummyTokens('myval')
        with self.assertRaises(exceptions.ArgumentRequiredError):
            options.parse(dummy_parser, dummy_tokens)

        options = core.Options(
            arguments.Argument('myarg'),
            arguments.Argument('myarg2', required=True, default=None),
        )
        dummy_tokens = DummyTokens('myval')
        with self.assertRaises(exceptions.ArgumentRequiredError):
            options.parse(dummy_parser, dummy_tokens)

    def test_parse_argument_with_value_class_is_value(self):
        options = core.Options(
            arguments.Argument('myarg'),
        )
        for i in [42, "foo", 3.2, True, False, None, [3], {3:3}]:
            dummy_tokens = DummyTokens(i)
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)
            dummy_context = {}
            self.assertEqual(kwargs['myarg'].resolve(dummy_context), i)

    def test_parse_argument_with_value_class_is_string_and_given_is_string(self):
        options = core.Options(
            arguments.Argument('myarg', value_class=values.StringValue),
        )
        dummy_tokens = DummyTokens('myval')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')

    def test_parse_argument_with_value_class_is_string_and_given_is_not_string(self):
        options = core.Options(
            arguments.Argument('myarg', value_class=values.StringValue),
        )

        for i in [42, True, None]:
            dummy_tokens = DummyTokens(i)
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)
            dummy_context = {}
            self.assertEqual(kwargs['myarg'].resolve(dummy_context), str(i))

    def test_parse_argument_with_value_class_is_strict_string_and_given_is_string(self):
        options = core.Options(
            arguments.Argument('myarg', value_class=values.StrictStringValue),
        )
        dummy_tokens = DummyTokens('myval')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')

    def test_parse_argument_with_value_class_is_strict_string_and_given_is_not_string_should_not_pass(self):
        options = core.Options(
            arguments.Argument('myarg', value_class=values.StrictStringValue),
        )
        dummy_context = {}

        for i in [42, 42.42, True, None, ["foo"], {"foo": "bar"}]:
            dummy_tokens = DummyTokens(i)
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)

            #  TODO: test resolve called in render
            with SettingsOverride(DEBUG=False):
                with self.assertWarns(exceptions.TemplateSyntaxWarning):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), '')

            with SettingsOverride(DEBUG=True):
                with self.assertRaises(exceptions.TemplateSyntaxError):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), '')

    def test_parse_argument_with_value_class_is_float_and_given_is_float(self):
        options = core.Options(
            arguments.Argument('myarg', value_class=values.FloatValue),
        )
        dummy_tokens = DummyTokens(42.42)
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 42.42)

    def test_parse_argument_with_value_class_is_float_and_given_is_not_float(self):
        options = core.Options(
            arguments.Argument('myarg', value_class=values.FloatValue),
        )
        dummy_context = {}

        for i in ["42.42", 42, True, False]:
            dummy_tokens = DummyTokens(i)
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)
            dummy_context = {}
            self.assertEqual(kwargs['myarg'].resolve(dummy_context), float(i))

        for i in ["foo", ["foo"], {"foo": "bar"}, None]:
            dummy_tokens = DummyTokens(i)
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)

            with SettingsOverride(DEBUG=False):
                with self.assertWarns(exceptions.TemplateSyntaxWarning):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), 0)

            with SettingsOverride(DEBUG=True):
                with self.assertRaises(exceptions.TemplateSyntaxError):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), 0)

        options = core.Options(
            arguments.Argument('myarg', value_class=values.Value),
        )
        dummy_tokens = DummyTokens('myval')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        pass

    def test_parse_argument_with_value_class_is_integer_and_given_is_integer(self):
        options = core.Options(
            arguments.Argument('myarg', value_class=values.IntegerValue),
        )
        dummy_tokens = DummyTokens(42)
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 42)

    def test_parse_argument_with_value_class_is_integer_and_given_is_not_integer(self):
        options = core.Options(
            arguments.Argument('myarg', value_class=values.IntegerValue),
        )
        dummy_context = {}

        for i in ["42", 42.42, True]:
            dummy_tokens = DummyTokens(i)
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)
            dummy_context = {}
            self.assertEqual(kwargs['myarg'].resolve(dummy_context), int(i))

        for i in ["foo", ["foo"], {"foo": "bar"}, None]:
            dummy_tokens = DummyTokens(i)
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)

            with SettingsOverride(DEBUG=False):
                with self.assertWarns(exceptions.TemplateSyntaxWarning):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), 0)

            with SettingsOverride(DEBUG=True):
                with self.assertRaises(exceptions.TemplateSyntaxError):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), 0)

        options = core.Options(
            arguments.Argument('myarg', value_class=values.Value),
        )
        dummy_tokens = DummyTokens('myval')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        pass

    def test_parse_argument_with_value_class_is_boolean_and_given_is_boolean(self):
        options = core.Options(
            arguments.Argument('myarg', value_class=values.BooleanValue),
        )
        dummy_context = {}

        for i in [True, False]:
            dummy_tokens = DummyTokens(i)
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)
            dummy_context = {}
            self.assertEqual(kwargs['myarg'].resolve(dummy_context), i)
        options = core.Options(
            arguments.Argument('myarg', value_class=values.Value),
        )

    def test_parse_argument_with_value_class_is_boolean_and_given_is_not_boolean(self):
        options = core.Options(
            arguments.Argument('myarg', value_class=values.BooleanValue),
        )
        dummy_context = {}

        for i in [42, -42.42, 0, "foo", ["foo"], {"foo": "bar"}, None]:
            dummy_tokens = DummyTokens(i)
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)
            dummy_context = {}
            self.assertEqual(kwargs['myarg'].resolve(dummy_context), bool(i))

    def test_parse_argument_with_value_class_is_iterable_and_given_is_iterable(self):
        options = core.Options(
            arguments.Argument('myarg', value_class=values.IterableValue),
        )
        dummy_tokens = DummyTokens('myval')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)

        for i in ["foo", ["bar"], {"foo": "bar"}, (1,2,3)]:
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)
            dummy_context = {'myval': i}
            self.assertEqual(kwargs['myarg'].resolve(dummy_context), i)

    def test_parse_argument_with_value_class_is_iterable_and_given_is_not_iterable(self):
        options = core.Options(
            arguments.Argument('myarg', value_class=values.IterableValue),
        )
        dummy_context = {}

        for i in [42, 42.42, True, False, None]:
            dummy_tokens = DummyTokens(i)
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)

            with SettingsOverride(DEBUG=False):
                with self.assertWarns(exceptions.TemplateSyntaxWarning):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), [])

            with SettingsOverride(DEBUG=True):
                with self.assertRaises(exceptions.TemplateSyntaxError):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), [])

    def test_parse_argument_with_value_class_is_list_and_given_is_list(self):
        options = core.Options(
            arguments.Argument('myarg', value_class=values.ListValue),
        )
        my_list = [42, "foo", None]
        dummy_tokens = DummyTokens('mylist')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {'mylist': my_list}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), my_list)

    def test_parse_argument_with_value_class_is_list_and_given_is_not_list(self):
        options = core.Options(
            arguments.Argument('myarg', value_class=values.ListValue),
        )
        dummy_context = {}

        for i in [42, 42.42, True, None, "foo", {"foo": "bar"}]:
            dummy_tokens = DummyTokens(i)
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)

            with SettingsOverride(DEBUG=False):
                with self.assertWarns(exceptions.TemplateSyntaxWarning):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), [])

            with SettingsOverride(DEBUG=True):
                with self.assertRaises(exceptions.TemplateSyntaxError):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), [])

    def test_parse_argument_with_value_class_is_dict_and_given_is_dict(self):
        options = core.Options(
            arguments.Argument('myarg', value_class=values.DictValue),
        )
        my_dict = {
            "answer_to_life_the_universe_and_everything" : 42,
            "foo" : "bar",
            "None": None,
            "mydict": {}
        }
        dummy_tokens = DummyTokens('mydict')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {'mydict': my_dict}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), my_dict)

    def test_parse_argument_with_value_class_is_dict_and_given_is_not_dict(self):
        options = core.Options(
            arguments.Argument('myarg', value_class=values.DictValue),
        )
        dummy_context = {}

        for i in [42, 42.42, True, None, ["foo"], "bar"]:
            dummy_tokens = DummyTokens(i)
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)

            with SettingsOverride(DEBUG=False):
                with self.assertWarns(exceptions.TemplateSyntaxWarning):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), {})

            with SettingsOverride(DEBUG=True):
                with self.assertRaises(exceptions.TemplateSyntaxError):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), {})



    def test_parse_keyword_argument(self):
        options = core.Options(
            arguments.KeywordArgument('myarg'),
        )
        dummy_tokens = DummyTokens("myarg='myval'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')

        dummy_tokens = DummyTokens("myval")
        with self.assertRaises(exceptions.ArgumentRequiredError):
            options.parse(dummy_parser, dummy_tokens)

        dummy_tokens = DummyTokens()
        with self.assertRaises(exceptions.ArgumentRequiredError):
            options.parse(dummy_parser, dummy_tokens)

    def test_parse_multi_keyword_arguments(self):
        options = core.Options(
            arguments.KeywordArgument('myarg'),
            arguments.KeywordArgument('myarg2'),
        )
        dummy_tokens = DummyTokens("myarg='myval'", "myarg2='myval2'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'myval2')

    def test_parse_multi_keyword_arguments_shuffled(self):
        options = core.Options(
            arguments.KeywordArgument('myarg'),
            arguments.KeywordArgument('myarg2'),
        )
        dummy_tokens = DummyTokens("myarg2='myval2'", "myarg='myval'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'myval2')

    def test_parse_too_many_keyword_arguments_should_not_pass(self):
        options = core.Options(
            arguments.KeywordArgument('myarg'),
        )

        dummy_tokens = DummyTokens("myarg='myval'", "myarg2='myval2'")
        with self.assertRaises(exceptions.TooManyArguments):
            options.parse(dummy_parser, dummy_tokens)

    def test_parse_keyword_argument_not_required_with_default_given(self):
        options = core.Options(
            arguments.KeywordArgument('myarg'),
            arguments.KeywordArgument('myarg2', required=False, default="foo"),
        )
        dummy_tokens = DummyTokens("myarg='myval'", "myarg2='myval2'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'myval2')

    def test_parse_keyword_argument_not_required_with_default_not_given(self):
        options = core.Options(
            arguments.KeywordArgument('myarg'),
            arguments.KeywordArgument('myarg2', required=False, default='foo'),
        )
        dummy_tokens = DummyTokens("myarg='myval'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'foo')

    def test_parse_keyword_argument_not_required_without_default_given(self):
        options = core.Options(
            arguments.KeywordArgument('myarg'),
            arguments.KeywordArgument('myarg2', required=False),
        )
        dummy_tokens = DummyTokens("myarg='myval'", "myarg2='myval2'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'myval2')

        options = core.Options(
            arguments.KeywordArgument('myarg'),
            arguments.KeywordArgument('myarg2', required=False, default=None),
        )
        dummy_tokens = DummyTokens("myarg='myval'", "myarg2='myval2'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'myval2')

    def test_parse_keyword_argument_not_required_without_default_not_given(self):
        options = core.Options(
            arguments.KeywordArgument('myarg'),
            arguments.KeywordArgument('myarg2', required=False),
        )
        dummy_tokens = DummyTokens("myarg='myval'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')

        options = core.Options(
            arguments.KeywordArgument('myarg'),
            arguments.KeywordArgument('myarg2', required=False, default=None),
        )
        dummy_tokens = DummyTokens("myarg='myval'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')

    def test_parse_keyword_argument_required_with_default_given(self):
        options = core.Options(
            arguments.KeywordArgument('myarg'),
            arguments.KeywordArgument('myarg2', default="foo"),
        )
        dummy_tokens = DummyTokens("myarg='myval'", "myarg2='myval2'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'myval2')

        options = core.Options(
            arguments.KeywordArgument('myarg'),
            arguments.KeywordArgument('myarg2', required=True, default="foo"),
        )
        dummy_tokens = DummyTokens("myarg='myval'", "myarg2='myval2'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'myval2')

    def test_parse_keyword_argument_required_with_default_not_given_should_not_pass(self):
        options = core.Options(
            arguments.KeywordArgument('myarg'),
            arguments.KeywordArgument('myarg2', default='foo'),
        )

        dummy_tokens = DummyTokens("myarg='myval'")
        with self.assertRaises(exceptions.ArgumentRequiredError):
            options.parse(dummy_parser, dummy_tokens)

        options = core.Options(
            arguments.KeywordArgument('myarg'),
            arguments.KeywordArgument('myarg2', required=True, default='foo'),
        )

        dummy_tokens = DummyTokens("myarg='myval'")
        with self.assertRaises(exceptions.ArgumentRequiredError):
            options.parse(dummy_parser, dummy_tokens)

    def test_parse_keyword_argument_required_without_default_given(self):
        options = core.Options(
            arguments.KeywordArgument('myarg'),
            arguments.KeywordArgument('myarg2'),
        )
        dummy_tokens = DummyTokens("myarg='myval'", "myarg2='myval2'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'myval2')

        options = core.Options(
            arguments.KeywordArgument('myarg'),
            arguments.KeywordArgument('myarg2', required=True, default=None),
        )
        dummy_tokens = DummyTokens("myarg='myval'", "myarg2='myval2'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'myval2')

    def test_parse_keyword_argument_required_without_default_not_given_should_not_pass(self):
        options = core.Options(
            arguments.KeywordArgument('myarg'),
            arguments.KeywordArgument('myarg2'),
        )
        dummy_tokens = DummyTokens("myarg='myval'")
        with self.assertRaises(exceptions.ArgumentRequiredError):
            options.parse(dummy_parser, dummy_tokens)

        options = core.Options(
            arguments.KeywordArgument('myarg'),
            arguments.KeywordArgument('myarg2', required=True, default=None),
        )
        dummy_tokens = DummyTokens("myarg='myval'")
        with self.assertRaises(exceptions.ArgumentRequiredError):
            options.parse(dummy_parser, dummy_tokens)

    def test_parse_keyword_argument_with_value_class_is_value(self):
        options = core.Options(
            arguments.KeywordArgument('myarg'),
        )
        for i in [42, "foo", 3.2, True, False, None, [3], {3:3}]:
            dummy_tokens = DummyTokens("myarg={}".format(i))
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)
            dummy_context = {}
            self.assertEqual(kwargs['myarg'].resolve(dummy_context), i)

    def test_parse_keyword_argument_with_value_class_is_string_and_given_is_string(self):
        options = core.Options(
            arguments.KeywordArgument('myarg', value_class=values.StringValue),
        )
        dummy_tokens = DummyTokens("myarg='myval'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')

    def test_parse_keyword_argument_with_value_class_is_string_and_given_is_not_string(self):
        options = core.Options(
            arguments.KeywordArgument('myarg', value_class=values.StringValue),
        )

        for i in [42, True, None]:
            dummy_tokens = DummyTokens("myarg={}".format(i))
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)
            dummy_context = {}
            self.assertEqual(kwargs['myarg'].resolve(dummy_context), str(i))

    def test_parse_keyword_argument_with_value_class_is_strict_string_and_given_is_string(self):
        options = core.Options(
            arguments.KeywordArgument('myarg', value_class=values.StrictStringValue),
        )
        dummy_tokens = DummyTokens("myarg='myval'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')

    def test_parse_keyword_argument_with_value_class_is_strict_string_and_given_is_not_string_should_not_pass(self):
        options = core.Options(
            arguments.KeywordArgument('myarg', value_class=values.StrictStringValue),
        )
        dummy_context = {}

        for i in [42, 42.42, True, None, ["foo"], {"foo": "bar"}]:
            dummy_tokens = DummyTokens("myarg={}".format(i))
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)

            #  TODO: test resolve called in render
            with SettingsOverride(DEBUG=False):
                with self.assertWarns(exceptions.TemplateSyntaxWarning):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), '')

            with SettingsOverride(DEBUG=True):
                with self.assertRaises(exceptions.TemplateSyntaxError):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), '')

    def test_parse_keyword_argument_with_value_class_is_float_and_given_is_float(self):
        options = core.Options(
            arguments.KeywordArgument('myarg', value_class=values.FloatValue),
        )
        dummy_tokens = DummyTokens("myarg=42.42")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 42.42)

    def test_parse_keyword_argument_with_value_class_is_float_and_given_is_not_float(self):
        options = core.Options(
            arguments.KeywordArgument('myarg', value_class=values.FloatValue),
        )
        dummy_context = {}

        for i in ["42.42", 42, True, False]:
            dummy_tokens = DummyTokens("myarg={}".format(i))
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)
            dummy_context = {}
            self.assertEqual(kwargs['myarg'].resolve(dummy_context), float(i))

        for i in ["foo", ["foo"], {"foo": "bar"}, None]:
            dummy_tokens = DummyTokens("myarg={}".format(i))
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)

            with SettingsOverride(DEBUG=False):
                with self.assertWarns(exceptions.TemplateSyntaxWarning):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), 0)

            with SettingsOverride(DEBUG=True):
                with self.assertRaises(exceptions.TemplateSyntaxError):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), 0)

        options = core.Options(
            arguments.KeywordArgument('myarg', value_class=values.Value),
        )
        dummy_tokens = DummyTokens("myarg='myval'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        pass

    def test_parse_keyword_argument_with_value_class_is_integer_and_given_is_integer(self):
        options = core.Options(
            arguments.KeywordArgument('myarg', value_class=values.IntegerValue),
        )
        dummy_tokens = DummyTokens('myarg=42')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 42)

    def test_parse_keyword_argument_with_value_class_is_integer_and_given_is_not_integer(self):
        options = core.Options(
            arguments.KeywordArgument('myarg', value_class=values.IntegerValue),
        )
        dummy_context = {}

        for i in ["42", 42.42, True]:
            dummy_tokens = DummyTokens("myarg={}".format(i))
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)
            dummy_context = {}
            self.assertEqual(kwargs['myarg'].resolve(dummy_context), int(i))

        for i in ["foo", ["foo"], {"foo": "bar"}, None]:
            dummy_tokens = DummyTokens("myarg={}".format(i))
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)

            with SettingsOverride(DEBUG=False):
                with self.assertWarns(exceptions.TemplateSyntaxWarning):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), 0)

            with SettingsOverride(DEBUG=True):
                with self.assertRaises(exceptions.TemplateSyntaxError):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), 0)

        options = core.Options(
            arguments.KeywordArgument('myarg', value_class=values.Value),
        )
        dummy_tokens = DummyTokens("myarg='myval'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        pass

    def test_parse_keyword_argument_with_value_class_is_boolean_and_given_is_boolean(self):
        options = core.Options(
            arguments.KeywordArgument('myarg', value_class=values.BooleanValue),
        )
        dummy_context = {}

        for i in [True, False]:
            dummy_tokens = DummyTokens("myarg={}".format(i))
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)
            dummy_context = {}
            self.assertEqual(kwargs['myarg'].resolve(dummy_context), i)
        options = core.Options(
            arguments.KeywordArgument('myarg', value_class=values.Value),
        )

    def test_parse_keyword_argument_with_value_class_is_boolean_and_given_is_not_boolean(self):
        options = core.Options(
            arguments.KeywordArgument('myarg', value_class=values.BooleanValue),
        )
        dummy_context = {}

        for i in [42, -42.42, 0, "foo", ["foo"], {"foo": "bar"}, None]:
            dummy_tokens = DummyTokens("myarg={}".format(i))
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)
            dummy_context = {}
            self.assertEqual(kwargs['myarg'].resolve(dummy_context), bool(i))

    def test_parse_keyword_argument_with_value_class_is_iterable_and_given_is_iterable(self):
        options = core.Options(
            arguments.KeywordArgument('myarg', value_class=values.IterableValue),
        )
        dummy_tokens = DummyTokens("myarg='myval'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)

        for i in ["foo", ["bar"], {"foo": "bar"}, (1,2,3)]:
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)
            dummy_context = {'myval': i}
            self.assertEqual(kwargs['myarg'].resolve(dummy_context), i)

    def test_parse_keyword_argument_with_value_class_is_iterable_and_given_is_not_iterable(self):
        options = core.Options(
            arguments.KeywordArgument('myarg', value_class=values.IterableValue),
        )
        dummy_context = {}

        for i in [42, 42.42, True, False, None]:
            dummy_tokens = DummyTokens("myarg={}".format(i))
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)

            with SettingsOverride(DEBUG=False):
                with self.assertWarns(exceptions.TemplateSyntaxWarning):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), [])

            with SettingsOverride(DEBUG=True):
                with self.assertRaises(exceptions.TemplateSyntaxError):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), [])

    def test_parse_keyword_argument_with_value_class_is_list_and_given_is_list(self):
        options = core.Options(
            arguments.KeywordArgument('myarg', value_class=values.ListValue),
        )
        my_list = [42, "foo", None]
        dummy_tokens = DummyTokens("myarg='mylist'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {'mylist': my_list}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), my_list)

    def test_parse_keyword_argument_with_value_class_is_list_and_given_is_not_list(self):
        options = core.Options(
            arguments.KeywordArgument('myarg', value_class=values.ListValue),
        )
        dummy_context = {}

        for i in [42, 42.42, True, None, "foo", {"foo": "bar"}]:
            dummy_tokens = DummyTokens("myarg={}".format(i))
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)

            with SettingsOverride(DEBUG=False):
                with self.assertWarns(exceptions.TemplateSyntaxWarning):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), [])

            with SettingsOverride(DEBUG=True):
                with self.assertRaises(exceptions.TemplateSyntaxError):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), [])

    def test_parse_keyword_argument_with_value_class_is_dict_and_given_is_dict(self):
        options = core.Options(
            arguments.KeywordArgument('myarg', value_class=values.DictValue),
        )
        my_dict = {
            "answer_to_life_the_universe_and_everything" : 42,
            "foo" : "bar",
            "None": None,
            "mydict": {}
        }
        dummy_tokens = DummyTokens("myarg='mydict'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {'mydict': my_dict}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), my_dict)

    def test_parse_keyword_argument_with_value_class_is_dict_and_given_is_not_dict(self):
        options = core.Options(
            arguments.KeywordArgument('myarg', value_class=values.DictValue),
        )
        dummy_context = {}

        for i in [42, 42.42, True, None, ["foo"], "bar"]:
            dummy_tokens = DummyTokens("myarg={}".format(i))
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)

            with SettingsOverride(DEBUG=False):
                with self.assertWarns(exceptions.TemplateSyntaxWarning):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), {})

            with SettingsOverride(DEBUG=True):
                with self.assertRaises(exceptions.TemplateSyntaxError):
                    self.assertEqual(kwargs['myarg'].resolve(dummy_context), {})

    def test_parse_keyword_argument_with_choices_and_given_is_in_choices(self):
        choices = ["foo", "bar", "myval"]

        options = core.Options(
            arguments.KeywordArgument('myarg', choices=choices),
            arguments.KeywordArgument('myarg2', choices=choices),
        )
        dummy_tokens = DummyTokens("myarg='foo'", "myarg2='bar'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'foo')
        self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'bar')

    def test_parse_keyword_argument_with_choices_and_given_is_not_in_choices(self):
        choices = ["foo", "bar", "myval"]

        options = core.Options(
            arguments.KeywordArgument('myarg', choices=choices),
            arguments.KeywordArgument('myarg2', choices=choices),
        )
        dummy_tokens = DummyTokens("myarg='myval'", "myarg2='toto'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')

        with self.assertWarns(exceptions.TemplateSyntaxWarning):
            self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'foo')

    def test_parse_keyword_argument_name_same_as_arg_value(self):
        options = core.Options(
            arguments.KeywordArgument('myarg'),
            arguments.Argument('myarg2'),
        )
        dummy_tokens = DummyTokens("myarg", "myarg='foo'")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {'myarg': 'bar'}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'foo')
        self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'bar')


    def test_parse_flag(self):
        options = core.Options(
            arguments.Flag('myarg'),
        )

        tokens_values = [
            {"token": ["myarg"], "value": True},
            {"token": ["myarg=True"], "value": True},
            {"token": ["myarg=False"], "value": False},
            {"token": [], "value": False}
        ]

        for i in tokens_values:
            dummy_tokens = DummyTokens(*i["token"])
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)
            dummy_context = {}
            self.assertEqual(kwargs['myarg'].resolve(dummy_context), i["value"])

    def test_parse_flag_name_same_as_arg_value(self):
        options = core.Options(
            arguments.Flag('myarg'),
            arguments.Argument('myarg2', required=False),
        )
        dummy_context = {'myarg': 'bar'}

        dummy_tokens = DummyTokens("myarg", "myarg")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        self.assertTrue(kwargs['myarg'].resolve(dummy_context))
        self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'bar')

        dummy_tokens = DummyTokens("myarg")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        self.assertTrue(kwargs['myarg'].resolve(dummy_context))
        # self.assertEqual(kwargs['myarg2'].resolve(dummy_context), 'bar')

    def test_parse_too_many_flag_should_not_pass(self):
        options = core.Options(
            arguments.Flag('myarg'),
            arguments.Flag('myarg2'),
        )

        dummy_tokens = DummyTokens("myarg", "myarg2", "myarg3")
        with self.assertRaises(exceptions.TooManyArguments):
            options.parse(dummy_parser, dummy_tokens)

    def test_parse_flag_given_is_not_boolean(self):
        options = core.Options(
            arguments.Flag('myarg'),
        )

        tokens_values = [
            {"token": "myarg='foo'", "value": True},
            {"token": "myarg=''", "value": False},
            {"token": "myarg=None", "value": False},
            {"token": "myarg=['foo']", "value": True},
            {"token": "myarg=[]", "value": False},
            {"token": "myarg={'bar': 42}", "value": True},
            {"token": "myarg={}", "value": False},
        ]

        for i in tokens_values:
            dummy_tokens = DummyTokens(i["token"])
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 1)
            dummy_context = {}
            self.assertEqual(kwargs['myarg'].resolve(dummy_context), i["value"])

    def test_parse_flags_shuffled(self):
        options = core.Options(
            arguments.Flag('myarg'),
            arguments.Flag('myarg2'),
            arguments.Flag('myarg3'),
        )

        dummy_tokens = DummyTokens("myarg3=False", "myarg=True", "myarg2=False")
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 3)
        dummy_context = {}
        self.assertTrue(kwargs['myarg'].resolve(dummy_context))
        self.assertFalse(kwargs['myarg2'].resolve(dummy_context))
        self.assertFalse(kwargs['myarg3'].resolve(dummy_context))


    def test_parse_args_kwargs_flags_shuffled(self):
        options = core.Options(
            arguments.Flag('myarg'),
            arguments.KeywordArgument('myarg2'),
            arguments.Argument('myarg3'),
        )

        tokens = [
            [42, "myarg2='foo'", "myarg"],
            ["myarg2='foo'", "myarg", 42],
            ["myarg2='foo'", 42, "myarg=True"],
            [42, "myarg=True", "myarg2='foo'"],
            ["myarg=True", "myarg2='foo'", 42]
        ]

        for i in tokens:
            dummy_tokens = DummyTokens(*i)
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 3)
            dummy_context = {}
            self.assertTrue(kwargs['myarg'].resolve(dummy_context))
            self.assertEqual(kwargs['myarg2'].resolve(dummy_context), "foo")
            self.assertEqual(kwargs['myarg3'].resolve(dummy_context), 42)

        tokens = [
            ["myarg2='foo'", 42],
            [42, "myarg2='foo'"],
            ["myarg2='foo'", 42, "myarg=False"],
            [42, "myarg=False", "myarg2='foo'"],
            ["myarg=False", "myarg2='foo'", 42]
        ]

        for i in tokens:
            dummy_tokens = DummyTokens(*i)
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            self.assertEqual(blocks, {})
            self.assertEqual(len(kwargs), 3)
            dummy_context = {}
            self.assertFalse(kwargs['myarg'].resolve(dummy_context))
            self.assertEqual(kwargs['myarg2'].resolve(dummy_context), "foo")
            self.assertEqual(kwargs['myarg3'].resolve(dummy_context), 42)




    def test_parse_blocks(self):
        class TestTag(core.Tag):
            name="test"
            options = core.Options(
                blocks=[
                    ('enda', 'a'),
                    ('endb', 'b'),
                    ('endc', 'c'),
                    ('endtest', 'd'),
                ]
            )

            def render_tag(self, context, **kwargs): # pragma: no cover
                blocks = self.blocks.items()
                for key, value in blocks:
                    kwargs[key] = value.render(context)
                return "a: {}, b: {}, c: {}, d: {}".format(
                    kwargs["a"],
                    kwargs["b"],
                    kwargs["c"],
                    kwargs["d"],
                )

        with TemplateTags(TestTag):
            ctx = template.Context({})
            tpl = template.Template(
                "{% test %}<p>a</p>{% enda %}<div>b-elements</div>{% endb %}it's c{% endc %}d<br/>{% endtest %}"
            )
        output = tpl.render(ctx)
        expected_output = "a: <p>a</p>, b: <div>b-elements</div>, c: it's c, d: d<br/>"

        self.assertEqual(output, expected_output)

    def test_parse_blocks_with_blocks_are_string_not_tuple(self):
        class TestTag(core.Tag):
            name="test"
            options = core.Options(
                blocks = ['a', 'b', 'c', ('endtest', 'd')]
            )

            def render_tag(self, context, **kwargs): # pragma: no cover
                blocks = self.blocks.items()
                for key, value in blocks:
                    kwargs[key] = value.render(context)
                return "a: {}, b: {}, c: {}, d: {}".format(
                    kwargs["a"],
                    kwargs["b"],
                    kwargs["c"],
                    kwargs["d"],
                )

        with TemplateTags(TestTag):
            ctx = template.Context({})
            tpl = template.Template(
                "{% test %}<p>a</p>{% a %}<div>b-elements</div>{% b %}it's c{% c %}d<br/>{% endtest %}"
            )
        output = tpl.render(ctx)
        expected_output = "a: <p>a</p>, b: <div>b-elements</div>, c: it's c, d: d<br/>"

        self.assertEqual(output, expected_output)

    def test_parse_empty_block(self):
        class TestTag(core.Tag):
            name="test"
            options = core.Options(
                blocks=[('endtest', 'emptyblock')]
            )

            def render_tag(self, context, **kwargs): # pragma: no cover
                blocks = self.blocks.items()
                for key, value in blocks:
                    kwargs[key] = value.render(context)
                return "block: {}".format(kwargs["emptyblock"])

        with TemplateTags(TestTag):
            ctx = template.Context({})
            tpl = template.Template(
                "{% test %}{% endtest %}"
            )
        output = tpl.render(ctx)
        expected_output = "block: "
        self.assertEqual(output, expected_output)

    def test_parse_block_not_given(self):
        class TestTag(core.Tag):
            name="test"
            options = core.Options(
                blocks=[
                    ('enda', 'a'),
                    ('endb', 'b'),
                    ('endc', 'c'),
                    ('endtest', 'd'),
                ]
            )

            def render_tag(self, context, **kwargs):
                blocks = self.blocks.items()
                for key, value in blocks:
                    kwargs[key] = value.render(context)
                return "a: {}, b: {}, c: {}, d: {}".format(
                    kwargs["a"],
                    kwargs["b"],
                    kwargs["c"],
                    kwargs["d"],
                )

        with TemplateTags(TestTag):
            ctx = template.Context({})
            tpl = template.Template(
                "{% test %}<p>a</p>{% enda %}<div>b-elements</div>{% endtest %}"
            )
        output = tpl.render(ctx)
        expected_output = "a: <p>a</p>, b: <div>b-elements</div>, c: , d: "
        self.assertEqual(output, expected_output)

    def test_parse_too_many_blocks_should_not_pass(self):
        class TestTag(core.Tag):
            name="test"
            options = core.Options(
                blocks=[
                    ('enda', 'a'),
                    ('endb', 'b'),
                    ('endtest', 'c'),
                ]
            )

            def render_tag(self, context, **kwargs): # pragma: no cover
                blocks = self.blocks.items()
                for key, value in blocks:
                    kwargs[key] = value.render(context)
                return "a: {}, b: {}, c: {}".format(
                    kwargs["a"],
                    kwargs["b"],
                    kwargs["c"]
                )

        with self.assertRaises(exceptions.TemplateSyntaxError):
            with TemplateTags(TestTag):
                ctx = template.Context({})
                tpl = template.Template(
                    "{% test %}<p>a</p>{% enda %}<div>b-elements</div>{% endb %}it's c{% endc %}d<br/>{% endtest %}"
                )


class ComponentTagRenderTests(TestCase):

    def test_render_template(self):
        class TestTag(core.Tag):
            class Media:
                template = 'tests/foo.html'
                css = []
                js = []

            name="test"

        with TemplateTags(TestTag):
            ctx = template.Context({})
            tpl = template.Template(
                "{% test %}"
            )
        output = tpl.render(ctx)
        expected_output = "foo"
        self.assertEqual(output, expected_output)

    def test_render_template_with_arguments(self):
        class TestTag(core.Tag):
            class Media:
                template = 'tests/arguments.html'
                css = []
                js = []

            name="test"
            options =  core.Options(
                arguments.Argument('myarg'),
                arguments.KeywordArgument('mykwarg'),
                arguments.Flag('myflag'),
            )

        with TemplateTags(TestTag):
            ctx = template.Context({})
            tpl = template.Template(
                "{% test 'foo' mykwarg='bar' myflag %}"
            )

        output = tpl.render(ctx)
        expected_output = "myarg = foo / mykwarg = bar / myflag is True"
        self.assertEqual(output, expected_output)

        with TemplateTags(TestTag):
            ctx = template.Context({
                "foo": 42,
                "bar": "myval"
            })
            tpl = template.Template(
                "{% test foo mykwarg=bar myflag %}"
            )

        output = tpl.render(ctx)
        expected_output = "myarg = 42 / mykwarg = myval / myflag is True"
        self.assertEqual(output, expected_output)

    def test_render_template_with_blocks(self):
        class TestTag(core.Tag):
            class Media:
                template = 'tests/blocks.html'
                css = []
                js = []

            name="test"
            options =  core.Options(
                blocks = [('middle', 'before_blockmiddle'), ('endtest', 'after_middleblock')]
            )

        with TemplateTags(TestTag):
            ctx = template.Context({})
            tpl = template.Template(
                "{% test %}foo{% middle %}bar{% endtest %}"
            )

        output = tpl.render(ctx)
        expected_output = "before_blockmiddle : foo / after_middleblock : bar"
        self.assertEqual(output, expected_output)

    def test_render_dependencies_css(self):
        core.registry.clear()

        class TestTag(core.Tag):
            class Media:
                template = 'tests/foo.html'
                css = ['/foo.css', '/bar.css']
                js = []

            name="test"

        with TemplateTags(TestTag):
            ctx = template.Context({})
            tpl = template.Template(
                "{% load component_tags %}{% dependencies %}{% test %}"
            )

        output = tpl.render(ctx)
        expected_output = "{bar_css}\n{foo_css}\n{test}".format(
            bar_css='<link href="/bar.css" type="text/css" rel="stylesheet" />',
            foo_css='<link href="/foo.css" type="text/css" rel="stylesheet" />',
            test='foo'
        )
        self.assertEqual(output, expected_output)

    def test_render_dependencies_js(self):
        core.registry.clear()
        
        class TestTag(core.Tag):
            class Media:
                template = 'tests/foo.html'
                css = []
                js = ['/foo.js', '/bar.js']

            name="test"

        with TemplateTags(TestTag):
            ctx = template.Context({})
            tpl = template.Template(
                "{% load component_tags %}{% dependencies %}{% test %}"
            )

        output = tpl.render(ctx)
        expected_output = "{bar_js}\n{foo_js}\n{test}".format(
            foo_js='<script type="text/javascript" src="/foo.js"></script>',
            bar_js='<script type="text/javascript" src="/bar.js"></script>',
            test='foo'
        )
        self.assertEqual(output, expected_output)

    def test_render_dependencies(self):
        core.registry.clear()
        
        class TestTag(core.Tag):
            class Media:
                template = 'tests/foo.html'
                css = ['/foo.css']
                js = ['/bar.js']

            name="test"

        with TemplateTags(TestTag):
            ctx = template.Context({})
            tpl = template.Template(
                "{% load component_tags %}{% dependencies %}{% test %}"
            )

        output = tpl.render(ctx)
        expected_output = "{}\n{}\n{}".format(
            '<link href="/foo.css" type="text/css" rel="stylesheet" />',
            '<script type="text/javascript" src="/bar.js"></script>',
            'foo'
        )
        self.assertEqual(output, expected_output)

    def test_component_dependencies_with_component_use_same_media(self):
        core.registry.clear()
        
        class TestTag(core.Tag):
            class Media:
                template = 'tests/foo.html'
                css = ['/foo.css']
                js = ['/foo.js', '/bar.js']

            name="test"

        class OtherTestTag(core.Tag):
            class Media:
                template = 'tests/foo.html'
                css = ['/foo.css', '/bar.css']
                js = ['/foo.js']

            name="othertest"

        with TemplateTags(TestTag):
            with TemplateTags(OtherTestTag):
                ctx = template.Context({})
                tpl = template.Template(
                    "{% load component_tags %}{% dependencies %}{% test %}{% othertest %}"
                )

        output = tpl.render(ctx)
        expected_output = "{bar_css}\n{foo_css}\n{bar_js}\n{foo_js}\n{test}{othertest}".format(
            bar_css='<link href="/bar.css" type="text/css" rel="stylesheet" />',
            foo_css='<link href="/foo.css" type="text/css" rel="stylesheet" />',
            bar_js='<script type="text/javascript" src="/bar.js"></script>',
            foo_js='<script type="text/javascript" src="/foo.js"></script>',
            test='foo',
            othertest='foo'
        )
        self.assertEqual(output, expected_output)
