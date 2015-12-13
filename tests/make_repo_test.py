from __future__ import unicode_literals

import io
import os.path
import subprocess

import mock
import pytest
import yaml

from pre_commit_mirror_maker.make_repo import _apply_version_and_commit
from pre_commit_mirror_maker.make_repo import cwd
from pre_commit_mirror_maker.make_repo import format_files_to_directory
from pre_commit_mirror_maker.make_repo import make_repo
from pre_commit_mirror_maker.util import get_output


def test_format_files_to_directory(tmpdir):
    src_dir = os.path.join(tmpdir.strpath, 'src')
    dest_dir = os.path.join(tmpdir.strpath, 'dest')
    os.mkdir(src_dir)
    os.mkdir(dest_dir)

    # Create some files in src
    def _write_file_in_src(filename, contents):
        with io.open(os.path.join(src_dir, filename), 'w') as file_obj:
            file_obj.write(contents)

    _write_file_in_src('file1.txt', '{foo} bar {baz}')
    _write_file_in_src('file2.txt', 'hello world')
    _write_file_in_src('file3.txt', 'foo bar {baz}')

    format_files_to_directory(
        src_dir, dest_dir, {'foo': 'herp', 'baz': 'derp'},
    )

    def _read_file_in_dest(filename):
        return io.open(os.path.join(dest_dir, filename)).read()

    assert _read_file_in_dest('file1.txt') == 'herp bar derp'
    assert _read_file_in_dest('file2.txt') == 'hello world'
    assert _read_file_in_dest('file3.txt') == 'foo bar derp'


def test_format_files_to_directory_skips_pyc(tmpdir):
    src_dir = os.path.join(tmpdir.strpath, 'src')
    dest_dir = os.path.join(tmpdir.strpath, 'dest')
    os.mkdir(src_dir)
    os.mkdir(dest_dir)

    # Create some files in src
    def _write_file_in_src(filename, contents):
        with io.open(os.path.join(src_dir, filename), 'w') as file_obj:
            file_obj.write(contents)

    _write_file_in_src('setup.py', '# Setup.py')
    _write_file_in_src('setup.pyc', "# Setup.pyc, don't copy me!")

    format_files_to_directory(src_dir, dest_dir, {})

    assert os.path.exists(os.path.join(dest_dir, 'setup.py'))
    assert not os.path.exists(os.path.join(dest_dir, 'setup.pyc'))


def test_skips_directories(tmpdir):
    src_dir = os.path.join(tmpdir.strpath, 'src')
    dest_dir = os.path.join(tmpdir.strpath, 'dest')
    os.mkdir(src_dir)
    os.mkdir(dest_dir)

    os.mkdir(os.path.join(src_dir, '__pycache__'))
    format_files_to_directory(src_dir, dest_dir, {})
    assert not os.path.exists(os.path.join(dest_dir, '__pycache__'))


def test_cwd(tmpdir):
    original_cwd = os.getcwd()
    with cwd(tmpdir.strpath):
        assert os.getcwd() == tmpdir.strpath
    assert os.getcwd() == original_cwd


@pytest.yield_fixture
def in_git_dir(tmpdir):
    git_path = os.path.join(tmpdir.strpath, 'gits')
    subprocess.check_call(['git', 'init', git_path])
    with cwd(git_path):
        yield


@pytest.mark.usefixtures('in_git_dir')
def test_apply_version_and_commit():
    _apply_version_and_commit(
        '0.24.1', 'ruby', 'scss-lint', r'\.scss$', 'scss-lint', (),
    )

    # Assert that our things got copied over
    assert os.path.exists('hooks.yaml')
    assert os.path.exists('__fake_gem.gemspec')
    # Assert that we set the version file correctly
    assert os.path.exists('.version')
    assert io.open('.version').read().strip() == '0.24.1'

    # Assert some things about the gits
    assert get_output('git', 'status', '-s').strip() == ''
    assert get_output('git', 'tag', '-l').strip() == 'v0.24.1'
    assert get_output('git', 'log', '--oneline').strip().split() == [
        mock.ANY, 'Mirror:', '0.24.1',
    ]


@pytest.mark.usefixtures('in_git_dir')
def test_arguments():
    _apply_version_and_commit(
        '0.6.2', 'python', 'yapf', r'\.py$', 'yapf', ('-i',),
    )
    assert yaml.safe_load(io.open('hooks.yaml').read()) == [{
        'id': 'yapf',
        'name': 'yapf',
        'entry': 'yapf',
        'language': 'python',
        'files': r'\.py$',
        'args': ['-i'],
    }]


def returns_some_versions(_):
    return ['0.23.1', '0.24.0', '0.24.1']


@pytest.mark.usefixtures('in_git_dir')
def test_make_repo_starting_empty():
    make_repo(
        '.', 'ruby', 'scss-lint', r'\.scss$', 'scss-lint', (),
        version_list_fn_map={'ruby': returns_some_versions},
    )

    # Assert that our things got copied over
    assert os.path.exists('hooks.yaml')
    assert os.path.exists('__fake_gem.gemspec')
    # Assert that we set the version fiel correctly
    assert os.path.exists('.version')
    assert io.open('.version').read().strip() == '0.24.1'

    # Assert some things about hte gits
    assert get_output('git', 'status', '-s').strip() == ''
    assert get_output('git', 'tag', '-l').strip().split() == [
        'v0.23.1', 'v0.24.0', 'v0.24.1',
    ]
    log_lines = get_output('git', 'log', '--oneline').strip().splitlines()
    log_lines_split = [log_line.split() for log_line in log_lines]
    assert log_lines_split == [
        [mock.ANY, 'Mirror:', '0.24.1'],
        [mock.ANY, 'Mirror:', '0.24.0'],
        [mock.ANY, 'Mirror:', '0.23.1'],
    ]


@pytest.mark.usefixtures('in_git_dir')
def test_make_repo_starting_at_version():
    # Write a version file (as if we've already run this before)
    with io.open('.version', 'w') as version_file:
        version_file.write('0.23.1')

    make_repo(
        '.', 'ruby', 'scss-lint', r'\.scss$', 'scss-lint', (),
        version_list_fn_map={'ruby': returns_some_versions},
    )

    # Assert that we only got tags / commits for the stuff we added
    assert get_output('git', 'tag', '-l').strip().split() == [
        'v0.24.0', 'v0.24.1',
    ]
    log_lines = get_output('git', 'log', '--oneline').strip().splitlines()
    log_lines_split = [log_line.split() for log_line in log_lines]
    assert log_lines_split == [
        [mock.ANY, 'Mirror:', '0.24.1'],
        [mock.ANY, 'Mirror:', '0.24.0'],
    ]


@pytest.mark.integration
@pytest.mark.usefixtures('in_git_dir')
def test_ruby_integration():
    make_repo('.', 'ruby', 'scss-lint', r'\.scss$', 'scss-lint', ())
    # Our files should exist
    assert os.path.exists('.version')
    assert os.path.exists('hooks.yaml')
    assert os.path.exists('__fake_gem.gemspec')

    # Should have made _some_ tags
    assert get_output('git', 'tag', '-l').strip()
    # Should have made _some_ commits
    assert get_output('git', 'log', '--oneline').strip()

    # TODO: test that the gem is installable


@pytest.mark.integration
@pytest.mark.usefixtures('in_git_dir')
def test_node_integration():
    make_repo('.', 'node', 'jshint', r'\.js$', 'jshint', ())
    # Our files should exist
    assert os.path.exists('.version')
    assert os.path.exists('hooks.yaml')
    assert os.path.exists('package.json')

    # Should have made _some_ tags
    assert get_output('git', 'tag', '-l').strip()
    # Should have made _some_ commits
    assert get_output('git', 'log', '--oneline').strip()

    # TODO: test that the package is installable


@pytest.mark.integration
@pytest.mark.usefixtures('in_git_dir')
def test_python_integration():
    make_repo('.', 'python', 'flake8', r'\.py$', 'flake8', ())
    # Our files should exist
    assert os.path.exists('.version')
    assert os.path.exists('hooks.yaml')
    assert os.path.exists('setup.py')

    # Should have _some_ tags
    assert get_output('git', 'tag', '-l').strip()
    # Should have _some_ commits
    assert get_output('git', 'log', '--oneline').strip()

    # TODO: test that the package is installable
