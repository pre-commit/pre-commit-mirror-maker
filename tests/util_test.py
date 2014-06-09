from __future__ import unicode_literals

import pytest

from pre_commit_mirror_maker.util import from_utf8


@pytest.mark.parametrize(
    ('input_str', 'output'),
    ((b'hello', 'hello'), ('hello', 'hello')),
)
def test_from_utf8(input_str, output):
    ret = from_utf8(input_str)
    assert type(ret) is not bytes
    assert ret == output
