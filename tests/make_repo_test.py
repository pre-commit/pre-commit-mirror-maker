import os.path
import subprocess
import sys
from unittest import mock

import pytest
import yaml

from pre_commit_mirror_maker.make_repo import _apply_version_and_commit
from pre_commit_mirror_maker.make_repo import cwd
from pre_commit_mirror_maker.make_repo import format_files_to_directory
from pre_commit_mirror_maker.make_repo import make_repo


def _cmd(*cmd):
    return subprocess.check_output(cmd).strip().decode()


def test_format_files_to_directory(tmpdir):
    src = tmpdir.join('src').ensure_dir()
    dest = tmpdir.join('dest').ensure_dir()

    src.join('file1.txt').write('{foo} bar {baz}')
    src.join('file2.txt').write('hello world')
    src.join('file3.txt').write('foo bar {baz}')

    format_files_to_directory(src, dest, {'foo': 'herp', 'baz': 'derp'})

    assert dest.join('file1.txt').read() == 'herp bar derp'
    assert dest.join('file2.txt').read() == 'hello world'
    assert dest.join('file3.txt').read() == 'foo bar derp'


def test_format_files_to_directory_skips_pyc(tmpdir):
    src = tmpdir.join('src').ensure_dir()
    dest = tmpdir.join('dest').ensure_dir()

    src.join('setup.py').write('# Setup.py')
    src.join('setup.pyc').write("# Setup.pyc, don't copy me!")

    format_files_to_directory(src, dest, {})

    assert dest.join('setup.py').exists()
    assert not dest.join('setup.pyc').exists()


def test_skips_directories(tmpdir):
    src = tmpdir.join('src').ensure_dir()
    dest = tmpdir.join('dest').ensure_dir()

    src.join('__pycache__').ensure_dir()
    format_files_to_directory(src, dest, {})
    assert not dest.join('__pycache__').exists()


def test_cwd(tmpdir):
    original_cwd = os.getcwd()
    with cwd(tmpdir.strpath):
        assert os.getcwd() == tmpdir.strpath
    assert os.getcwd() == original_cwd


@pytest.fixture
def in_git_dir(tmpdir):
    git_path = tmpdir.join('gits')
    subprocess.check_call(('git', 'init', git_path))
    with git_path.as_cwd():
        yield git_path


def test_apply_version_and_commit(in_git_dir):
    _apply_version_and_commit(
        '0.24.1', 'ruby', 'scss-lint', r'\.scss$', 'scss-lint', (),
    )

    # Assert that our things got copied over
    assert in_git_dir.join('.pre-commit-hooks.yaml').exists()
    assert in_git_dir.join('hooks.yaml').exists()
    assert in_git_dir.join('__fake_gem.gemspec').exists()
    # Assert that we set the version file correctly
    assert in_git_dir.join('.version').read().strip() == '0.24.1'

    # Assert some things about the gits
    assert _cmd('git', 'status', '-s') == ''
    assert _cmd('git', 'tag', '-l') == 'v0.24.1'
    assert _cmd('git', 'log', '--oneline').split()[1:] == ['Mirror:', '0.24.1']


def test_arguments(in_git_dir):
    _apply_version_and_commit(
        '0.6.2', 'python', 'yapf', r'\.py$', 'yapf', ('-i',),
    )
    contents = in_git_dir.join('.pre-commit-hooks.yaml').read()
    assert yaml.safe_load(contents) == [{
        'id': 'yapf',
        'name': 'yapf',
        'entry': 'yapf',
        'language': 'python',
        'files': r'\.py$',
        'args': ['-i'],
    }]


def returns_some_versions(_):
    return ['0.23.1', '0.24.0', '0.24.1']


def test_make_repo_starting_empty(in_git_dir):
    make_repo(
        '.', 'ruby', 'scss-lint', r'\.scss$', 'scss-lint', (),
        version_list_fn_map={'ruby': returns_some_versions},
    )

    # Assert that our things got copied over
    assert in_git_dir.join('.pre-commit-hooks.yaml').exists()
    assert in_git_dir.join('hooks.yaml').exists()
    assert in_git_dir.join('__fake_gem.gemspec').exists()
    # Assert that we set the version fiel correctly
    assert in_git_dir.join('.version').read().strip() == '0.24.1'

    # Assert some things about the gits
    assert _cmd('git', 'status', '--short') == ''
    expected = ['v0.23.1', 'v0.24.0', 'v0.24.1']
    assert _cmd('git', 'tag', '-l').split() == expected
    log_lines = _cmd('git', 'log', '--oneline').splitlines()
    log_lines_split = [log_line.split() for log_line in log_lines]
    assert log_lines_split == [
        [mock.ANY, 'Mirror:', '0.24.1'],
        [mock.ANY, 'Mirror:', '0.24.0'],
        [mock.ANY, 'Mirror:', '0.23.1'],
    ]


def test_make_repo_starting_at_version(in_git_dir):
    # Write a version file (as if we've already run this before)
    in_git_dir.join('.version').write('0.23.1')

    make_repo(
        '.', 'ruby', 'scss-lint', r'\.scss$', 'scss-lint', (),
        version_list_fn_map={'ruby': returns_some_versions},
    )

    # Assert that we only got tags / commits for the stuff we added
    assert _cmd('git', 'tag', '-l').split() == ['v0.24.0', 'v0.24.1']
    log_lines = _cmd('git', 'log', '--oneline').splitlines()
    log_lines_split = [log_line.split() for log_line in log_lines]
    assert log_lines_split == [
        [mock.ANY, 'Mirror:', '0.24.1'],
        [mock.ANY, 'Mirror:', '0.24.0'],
    ]


@pytest.mark.integration
def test_ruby_integration(in_git_dir):
    make_repo('.', 'ruby', 'scss-lint', r'\.scss$', 'scss-lint', ())
    # Our files should exist
    assert in_git_dir.join('.version').exists()
    assert in_git_dir.join('.pre-commit-hooks.yaml').exists()
    assert in_git_dir.join('hooks.yaml').exists()
    assert in_git_dir.join('__fake_gem.gemspec').exists()

    # Should have made _some_ tags
    assert _cmd('git', 'tag', '-l')
    # Should have made _some_ commits
    assert _cmd('git', 'log', '--oneline')

    # TODO: test that the gem is installable


@pytest.mark.integration
def test_node_integration(in_git_dir):
    make_repo('.', 'node', 'jshint', r'\.js$', 'jshint', ())
    # Our files should exist
    assert in_git_dir.join('.version').exists()
    assert in_git_dir.join('.pre-commit-hooks.yaml').exists()
    assert in_git_dir.join('hooks.yaml').exists()
    assert in_git_dir.join('package.json').exists()

    # Should have made _some_ tags
    assert _cmd('git', 'tag', '-l')
    # Should have made _some_ commits
    assert _cmd('git', 'log', '--oneline')

    # TODO: test that the package is installable


def test_python_integration(in_git_dir):
    make_repo('.', 'python', 'flake8', r'\.py$', 'flake8', ())
    # Our files should exist
    assert in_git_dir.join('.version').exists()
    assert in_git_dir.join('.pre-commit-hooks.yaml').exists()
    assert in_git_dir.join('hooks.yaml').exists()
    assert in_git_dir.join('setup.py').exists()

    # Should have made _some_ tags
    assert _cmd('git', 'tag', '-l')
    # Should have made _some_ commits
    assert _cmd('git', 'log', '--oneline')

    # To make sure the name is valid
    subprocess.check_call((sys.executable, 'setup.py', 'egg_info'))

    # TODO: test that the package is installable
