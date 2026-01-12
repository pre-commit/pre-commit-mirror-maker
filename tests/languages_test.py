from __future__ import annotations

from pre_commit_mirror_maker.languages import golang_get_package_versions
from pre_commit_mirror_maker.languages import node_get_package_versions
from pre_commit_mirror_maker.languages import python_get_package_versions
from pre_commit_mirror_maker.languages import ruby_get_package_versions
from pre_commit_mirror_maker.languages import rust_get_package_versions


def assert_all_text(versions):
    for version in versions:
        assert type(version) is str


def test_node_get_package_version_output():
    ret = node_get_package_versions('jshint')
    assert ret
    assert_all_text(ret)


def test_python_get_package_version_output():
    ret = python_get_package_versions('flake8')
    assert ret
    assert_all_text(ret)


def test_python_get_package_version_extras_output():
    ret = python_get_package_versions('bandit[yaml]')
    assert ret
    assert_all_text(ret)


def test_ruby_get_package_version_output():
    ret = ruby_get_package_versions('scss-lint')
    assert ret
    assert_all_text(ret)


def test_rust_get_package_version_output():
    ret = rust_get_package_versions('clap')
    assert ret
    assert_all_text(ret)


def test_golang_get_package_version_output():
    ret = golang_get_package_versions('mvdan.cc/gofumpt')
    assert ret
    assert_all_text(ret)
