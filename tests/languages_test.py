from __future__ import unicode_literals

import pytest

from pre_commit_mirror_maker import five
from pre_commit_mirror_maker.languages import node_get_package_versions
from pre_commit_mirror_maker.languages import python_get_package_versions
from pre_commit_mirror_maker.languages import ruby_get_package_versions


def assert_all_text(versions):
    for version in versions:
        assert type(version) is five.text


@pytest.mark.integration
def test_node_get_package_version_output():
    ret = node_get_package_versions('jshint')
    assert ret
    assert_all_text(ret)


@pytest.mark.integration
def test_python_get_package_version_output():
    ret = python_get_package_versions('flake8')
    assert ret
    assert_all_text(ret)


@pytest.mark.integration
def test_ruby_get_package_version_output():
    ret = ruby_get_package_versions('scss-lint')
    assert ret
    assert_all_text(ret)
