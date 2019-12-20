import platform

import pytest

import ceryle.util as util


@pytest.mark.skipif(platform.system() != 'Linux', reason='Not a Linux platform')
def test_platform_is_linux():
    assert util.is_linux()
    assert not util.is_mac()
    assert not util.is_win()


@pytest.mark.skipif(platform.system() != 'Darwin', reason='Not a Mac platform')
def test_platform_is_mac():
    assert not util.is_linux()
    assert util.is_mac()
    assert not util.is_win()


@pytest.mark.skipif(platform.system() != 'Windows', reason='Not a Windows platform')
def test_platform_is_win():
    assert not util.is_linux()
    assert not util.is_mac()
    assert util.is_win()
