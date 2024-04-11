from __future__ import annotations

from pre_commit_mirror_maker.languages import _node_get_package_versions
from pre_commit_mirror_maker.languages import node_get_package_versions
from pre_commit_mirror_maker.languages import python_get_package_versions
from pre_commit_mirror_maker.languages import ruby_get_package_versions
from pre_commit_mirror_maker.languages import rust_get_package_versions


def assert_all_text(versions):
    for version in versions:
        assert type(version) is str

def test__node_get_package_version_output():
    package_json = {
        # versions sorted according to number
        "versions": [
            "1.0.0",
            "2.0.0",
            "2.0.1",
            "2.0.2",
            "3.0.0-beta",
            "3.0.1-beta",
            "3.0.2",
        ],
        # versions released out of order
        "time": {
            "1.0.0": "2017-01-10T03:45:38.963Z",
            "2.0.0": "2017-01-10T04:31:28.120Z",
            "3.0.0-beta": "2017-01-10T17:18:52.417Z",
            "2.0.1": "2017-01-11T04:52:50.871Z",
            "3.0.1-beta": "2017-01-11T08:55:07.338Z",
            "2.0.2": "2017-01-11T16:55:07.338Z",
            "3.0.2": "2017-01-13T20:14:11.275Z",
        }
    }
    # return versions matches the order they were release in
    assert _node_get_package_versions(package_json) == [
        "1.0.0",
        "2.0.0",
        "3.0.0-beta",
        "2.0.1",
        "3.0.1-beta",
        "2.0.2",
        "3.0.2",
    ]


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
