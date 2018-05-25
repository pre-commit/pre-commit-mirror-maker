import subprocess
import sys
from unittest import mock

import pytest
import yaml

from pre_commit_mirror_maker.languages import LIST_VERSIONS
from pre_commit_mirror_maker.make_repo import _commit_version
from pre_commit_mirror_maker.make_repo import format_files
from pre_commit_mirror_maker.make_repo import make_repo


def _cmd(*cmd):
    return subprocess.check_output(cmd).strip().decode()


def test_format_files(tmpdir):
    src = tmpdir.join('src').ensure_dir()
    dest = tmpdir.join('dest').ensure_dir()

    src.join('file1.txt').write('{foo} bar {baz}')
    src.join('file2.txt').write('hello world')
    src.join('file3.txt').write('foo bar {baz}')

    format_files(src, dest, foo='herp', baz='derp')

    assert dest.join('file1.txt').read() == 'herp bar derp'
    assert dest.join('file2.txt').read() == 'hello world'
    assert dest.join('file3.txt').read() == 'foo bar derp'


def test_format_files_skips_pyc(tmpdir):
    src = tmpdir.join('src').ensure_dir()
    dest = tmpdir.join('dest').ensure_dir()

    src.join('setup.py').write('# Setup.py')
    src.join('setup.pyc').write("# Setup.pyc, don't copy me!")

    format_files(src, dest)

    assert dest.join('setup.py').exists()
    assert not dest.join('setup.pyc').exists()


def test_skips_directories(tmpdir):
    src = tmpdir.join('src').ensure_dir()
    dest = tmpdir.join('dest').ensure_dir()

    src.join('__pycache__').ensure_dir()
    format_files(src, dest)
    assert not dest.join('__pycache__').exists()


@pytest.fixture
def in_git_dir(tmpdir):
    git_path = tmpdir.join('gits')
    subprocess.check_call(('git', 'init', git_path))
    with git_path.as_cwd():
        yield git_path


def test_commit_version(in_git_dir):
    _commit_version(
        '.',
        version='0.24.1', language='ruby', name='scss-lint', entry='scss-lint',
        match_key='files', match_val=r'\.scss$', args='[]',
        additional_dependencies=[],
    )

    # Assert that our things got copied over
    assert in_git_dir.join('.pre-commit-hooks.yaml').exists()
    assert in_git_dir.join('__fake_gem.gemspec').exists()
    # Assert that we set the version file correctly
    assert in_git_dir.join('.version').read().strip() == '0.24.1'

    # Assert some things about the gits
    assert _cmd('git', 'status', '-s') == ''
    assert _cmd('git', 'tag', '-l') == 'v0.24.1'
    assert _cmd('git', 'log', '--oneline').split()[1:] == ['Mirror:', '0.24.1']


def test_arguments(in_git_dir):
    _commit_version(
        '.',
        version='0.6.2', language='python', name='yapf', entry='yapf',
        match_key='files', match_val=r'\.py$', args='["-i"]',
        additional_dependencies=['scikit-learn'],
    )
    contents = in_git_dir.join('.pre-commit-hooks.yaml').read()
    assert yaml.safe_load(contents) == [{
        'id': 'yapf',
        'name': 'yapf',
        'entry': 'yapf',
        'language': 'python',
        'files': r'\.py$',
        'args': ['-i'],
        'additional_dependencies': ['scikit-learn'],
    }]


@pytest.fixture
def fake_versions():
    fns = {'ruby': lambda _: ('0.23.1', '0.24.0', '0.24.1')}
    with mock.patch.dict(LIST_VERSIONS, fns):
        yield


def test_make_repo_starting_empty(in_git_dir, fake_versions):
    make_repo(
        '.',
        language='ruby', name='scss-lint', entry='scss-lint',
        match_key='files', match_val=r'\.scss$', args='[]',
    )

    # Assert that our things got copied over
    assert in_git_dir.join('.pre-commit-hooks.yaml').exists()
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


def test_make_repo_starting_at_version(in_git_dir, fake_versions):
    # Write a version file (as if we've already run this before)
    in_git_dir.join('.version').write('0.23.1')
    # make sure this is gone afterwards
    in_git_dir.join('hooks.yaml').ensure()

    make_repo(
        '.',
        language='ruby', name='scss-lint', entry='scss-lint',
        match_key='files', match_val=r'\.scss$', args='[]',
    )

    assert not in_git_dir.join('hooks.yaml').exists()

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
    make_repo(
        '.',
        language='ruby', name='scss-lint', entry='scss-lint',
        match_key='files', match_val=r'\.scss$', args='[]',
    )
    # Our files should exist
    assert in_git_dir.join('.version').exists()
    assert in_git_dir.join('.pre-commit-hooks.yaml').exists()
    assert in_git_dir.join('__fake_gem.gemspec').exists()

    # Should have made _some_ tags
    assert _cmd('git', 'tag', '-l')
    # Should have made _some_ commits
    assert _cmd('git', 'log', '--oneline')

    # TODO: test that the gem is installable


@pytest.mark.integration
def test_node_integration(in_git_dir):
    make_repo(
        '.',
        language='node', name='jshint', entry='jshint',
        match_key='files', match_val=r'\.js$', args='[]',
    )
    # Our files should exist
    assert in_git_dir.join('.version').exists()
    assert in_git_dir.join('.pre-commit-hooks.yaml').exists()
    assert in_git_dir.join('package.json').exists()

    # Should have made _some_ tags
    assert _cmd('git', 'tag', '-l')
    # Should have made _some_ commits
    assert _cmd('git', 'log', '--oneline')

    # TODO: test that the package is installable


def test_python_integration(in_git_dir):
    make_repo(
        '.',
        language='python', name='flake8', entry='flake8',
        match_key='files', match_val=r'\.py$', args='[]',
    )
    # Our files should exist
    assert in_git_dir.join('.version').exists()
    assert in_git_dir.join('.pre-commit-hooks.yaml').exists()
    assert in_git_dir.join('setup.py').exists()

    # Should have made _some_ tags
    assert _cmd('git', 'tag', '-l')
    # Should have made _some_ commits
    assert _cmd('git', 'log', '--oneline')

    # To make sure the name is valid
    subprocess.check_call((sys.executable, 'setup.py', 'egg_info'))

    # TODO: test that the package is installable


@pytest.mark.integration
def test_rust_integration(in_git_dir):
    make_repo(
        '.',
        language='rust', name='shellharden', entry='shellharden',
        match_key='types', match_val='shell', args='["--replace"]',
    )
    # Our files should exist
    assert in_git_dir.join('.version').exists()
    assert in_git_dir.join('.pre-commit-hooks.yaml').exists()
    assert in_git_dir.join('Cargo.toml').exists()
    assert in_git_dir.join('main.rs').exists()

    # Should have made _some_ tags
    assert _cmd('git', 'tag', '-l')
    # Should have made _some_ commits
    assert _cmd('git', 'log', '--oneline')

    # TODO: test that the package is installable
