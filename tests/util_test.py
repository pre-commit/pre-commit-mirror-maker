from __future__ import unicode_literals

import pytest

from pre_commit_mirror_maker.util import from_utf8
from pre_commit_mirror_maker.util import get_output
from pre_commit_mirror_maker.util import split_by_commas


@pytest.mark.parametrize(
    ('input_str', 'output'),
    ((b'hello', 'hello'), ('hello', 'hello')),
)
def test_from_utf8(input_str, output):
    ret = from_utf8(input_str)
    assert type(ret) is not bytes
    assert ret == output


def test_get_output():
    output = get_output('echo', 'hi')
    assert output == 'hi\n'


@pytest.mark.parametrize(
    ('input_s', 'expected'),
    (
        ('', ()),
        (None, ()),
        ('onearg', ('onearg',)),
        ('two,args', ('two', 'args')),
        (r'arg,with\,escaped', ('arg', 'with,escaped')),
        (r'-i,--ignore=E265\,E309\,E501', ('-i', '--ignore=E265,E309,E501')),
    ),
)
def test_split_by_commas(input_s, expected):
    output = split_by_commas(input_s)
    assert output == expected
