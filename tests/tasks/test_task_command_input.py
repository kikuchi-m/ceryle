import os

import pytest

from ceryle.tasks.task import CommandInput, SingleValueCommandInput, MultiCommandInput


class TestCommandInput:

    @pytest.mark.parametrize(
        'args', [(), ('a', 'b', 'c')])
    def test_init_raise_when_unexpected_args_length(self, args):
        with pytest.raises(ValueError):
            CommandInput(*args)

    @pytest.mark.parametrize(
        'args', [
            (None,), (1,), (1.1,), (True,),
            ('a', None), ('a', 1,), ('a', 1.1,), ('a', True,),
        ])
    def test_init_raise_when_non_str_value(self, args):
        with pytest.raises(TypeError):
            CommandInput(*args)

    @pytest.mark.parametrize(
        'args, key', [
            (('a',), 'a'),
            (('a', 'b',), ('a', 'b')),
        ])
    def test_init_success(self, args, key):
        ci = CommandInput(*args)

        assert ci.key == key

    @pytest.mark.parametrize(
        'args, expected', [
            (('out',), ['a', 'b']),
            (('g1', 'out'), ['a', 'b']),
            (('g2', 'out'), ['c', 'd']),
            (('err',), None),
            (('g2', 'err'), None),
        ])
    def test_resolve(self, args, expected):
        ci = CommandInput(*args)
        reg = {
            'g1': {
                'out': ['a', 'b'],
            },
            'g2': {
                'out': ['c', 'd'],
            }
        }

        assert ci.resolve(reg, 'g1') == expected

    @pytest.mark.parametrize(
        'args', [('a',), ('a', 'b',)])
    def test_eq_with_self(self, args):
        ci = CommandInput(*args)

        assert ci == ci

    @pytest.mark.parametrize(
        'args', [('a',), ('a', 'b',)])
    def test_eq_with_same_key(self, args):
        ci1 = CommandInput(*args)
        ci2 = CommandInput(*args)

        assert ci1 == ci2

    @pytest.mark.parametrize('args', [('a',), ('a', 'b',)])
    @pytest.mark.parametrize('other', [
        1, 1.1, True, False, None, 'a', ('a', 'b'), object(),
        SingleValueCommandInput('a'), SingleValueCommandInput('a', 'b'),
        MultiCommandInput('a'),
    ])
    def test_not_eq(self, args, other):
        ci = CommandInput(*args)

        assert ci != other

    @pytest.mark.parametrize('key, expected', [
        (['A'], 'A'),
        (['A', 'B'], '(A, B)'),
    ])
    def test_str(self, key, expected):
        ci = CommandInput(*key)

        assert str(ci) == expected


class TestSingleValueCommandInput:

    @pytest.mark.parametrize(
        'args', [(), ('a', 'b', 'c')])
    def test_init_raise_when_unexpected_args_length(self, args):
        with pytest.raises(ValueError):
            SingleValueCommandInput(*args)

    @pytest.mark.parametrize(
        'args', [
            (None,), (1,), (1.1,), (True,),
            ('a', None), ('a', 1,), ('a', 1.1,), ('a', True,),
        ])
    def test_init_raise_when_non_str_value(self, args):
        with pytest.raises(TypeError):
            SingleValueCommandInput(*args)

    @pytest.mark.parametrize(
        'args, key', [
            (('a',), 'a'),
            (('a', 'b',), ('a', 'b')),
        ])
    def test_init_success(self, args, key):
        ci = SingleValueCommandInput(*args)

        assert ci.key == key

    @pytest.mark.parametrize(
        'args, expected', [
            (('out',), [f'a{os.linesep}b']),
            (('g1', 'out'), [f'a{os.linesep}b']),
            (('g2', 'out'), [f'c{os.linesep}d']),
            (('err',), None),
            (('g2', 'err'), None),
        ])
    def test_resolve(self, args, expected):
        ci = SingleValueCommandInput(*args)
        reg = {
            'g1': {
                'out': ['a', 'b'],
            },
            'g2': {
                'out': ['c', 'd'],
            }
        }

        assert ci.resolve(reg, 'g1') == expected

    @pytest.mark.parametrize(
        'args', [('a',), ('a', 'b',)])
    def test_eq_with_self(self, args):
        ci = SingleValueCommandInput(*args)

        assert ci == ci

    @pytest.mark.parametrize(
        'args', [('a',), ('a', 'b',)])
    def test_eq_with_same_key(self, args):
        ci1 = SingleValueCommandInput(*args)
        ci2 = SingleValueCommandInput(*args)

        assert ci1 == ci2

    @pytest.mark.parametrize('args', [('a',), ('a', 'b',)])
    @pytest.mark.parametrize('other', [
        1, 1.1, True, False, None, 'a', ('a', 'b'), object(),
        CommandInput('a'), CommandInput('a', 'b'),
        MultiCommandInput('a'),
    ])
    def test_not_eq(self, args, other):
        ci = SingleValueCommandInput(*args)

        assert ci != other

    @pytest.mark.parametrize('key, expected', [
        (['A'], 'A (as single value)'),
        (['A', 'B'], '(A, B) (as single value)'),
    ])
    def test_str(self, key,  expected):
        ci = SingleValueCommandInput(*key)

        assert str(ci) == expected


class TestMultiCommandInput:

    def test_init_raise_when_no_key(self):
        with pytest.raises(ValueError):
            MultiCommandInput()

    @pytest.mark.parametrize(
        'args', [
            (None,), (1,), (1.1,), (True,),
            ('a', None), ('a', 1,), ('a', 1.1,), ('a', True,),
        ])
    def test_init_raise_when_non_str_value(self, args):
        with pytest.raises(TypeError):
            MultiCommandInput(*args)

    @pytest.mark.parametrize(
        'args, key', [
            (['a'], [CommandInput('a')]),
            ([('a', 'b')], [CommandInput('a', 'b')]),
            (['a', ('a', 'b')], [CommandInput('a'), CommandInput('a', 'b')]),
            ([SingleValueCommandInput('a')], [SingleValueCommandInput('a')]),
        ])
    def test_init_success(self, args, key):
        ci = MultiCommandInput(*args)

        assert ci.key == key

    @pytest.mark.parametrize(
        'args, expected', [
            (['out'], ['a', 'b']),
            ([('g1', 'out')], ['a', 'b']),
            ([('g2', 'out')], ['c', 'd']),
            (['err'], None),
            ([('g2', 'err')], None),
            (['out', ('g2', 'out')], ['a', 'b', 'c', 'd']),
            (['out', SingleValueCommandInput('g2', 'out')], ['a', 'b', f'c{os.linesep}d']),
            (['out', ('g2', 'err')], None),
        ])
    def test_resolve(self, args, expected):
        ci = MultiCommandInput(*args)
        reg = {
            'g1': {
                'out': ['a', 'b'],
            },
            'g2': {
                'out': ['c', 'd'],
            }
        }

        assert ci.resolve(reg, 'g1') == expected

    @pytest.mark.parametrize(
        'args', [
            ['a'],
            [('a', 'b')],
            ['a', ('a', 'b')],
            ['a', ('a', 'b'), SingleValueCommandInput('a', 'b')],
        ])
    def test_eq_with_self(self, args):
        ci = MultiCommandInput(*args)

        assert ci == ci

    @pytest.mark.parametrize(
        'args', [
            ['a'],
            [('a', 'b')],
            ['a', ('a', 'b')],
            ['a', ('a', 'b'), SingleValueCommandInput('a', 'b')],
        ])
    def test_eq_with_same_key(self, args):
        ci1 = MultiCommandInput(*args)
        ci2 = MultiCommandInput(*args)

        assert ci1 == ci2

    @pytest.mark.parametrize(
        'args', [
            ['a'],
            [('a', 'b')],
            ['a', ('a', 'b')],
            ['a', ('a', 'b'), SingleValueCommandInput('a', 'b')],
        ])
    @pytest.mark.parametrize('other', [
        1, 1.1, True, False, None, 'a', ('a', 'b'), object(),
        CommandInput('a'), CommandInput('a', 'b'),
        SingleValueCommandInput('a'), SingleValueCommandInput('a', 'b'),
        MultiCommandInput('a', 'b'),
    ])
    def test_not_eq(self, args, other):
        ci = MultiCommandInput(*args)

        assert ci != other

    @pytest.mark.parametrize('key, expected', [
        (['A'], '[A]'),
        ([('A', 'B')], '[(A, B)]'),
        ([CommandInput('A')], '[A]'),
        ([SingleValueCommandInput('A')], '[A (as single value)]'),
        (['A', 'B'], '[A, B]'),
        ([('A', 'B'), 'C'], '[(A, B), C]'),
        ([SingleValueCommandInput('A', 'B'), CommandInput('C')], '[(A, B) (as single value), C]'),
    ])
    def test_str(self, key,  expected):
        ci = MultiCommandInput(*key)

        assert str(ci) == expected
