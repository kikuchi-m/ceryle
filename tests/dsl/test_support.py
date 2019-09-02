import pathlib

import ceryle.dsl.support as support


def test_joinpath():
    assert support.joinpath('foo', 'bar') == str(pathlib.Path('foo', 'bar'))
