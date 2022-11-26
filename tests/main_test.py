from __future__ import annotations

from unittest import mock

import pytest

from pre_commit_mirror_maker import main


@pytest.fixture
def mock_make_repo():
    with mock.patch.object(main, 'make_repo', return_value=0) as mck:
        yield mck


@pytest.mark.parametrize(
    ('input_s', 'expected'),
    (
        ('', ()),
        (None, ()),
        ('onearg', ('onearg',)),
        ('two,args', ('two', 'args')),
        (r'arg,with\,escaped', ('arg', 'with,escaped')),
        (r'-i,--ignore=E265\,E501', ('-i', '--ignore=E265,E501')),
    ),
)
def test_split_by_commas(input_s, expected):
    output = main.split_by_commas(input_s)
    assert output == expected


def test_main_passes_args(mock_make_repo):
    assert not main.main((
        '.',
        '--language', 'ruby',
        '--package-name', 'scss-lint',
        '--files-regex', r'\.scss$',
        '--entry', 'scss-lint-entry',
        '--id', 'scss-lint-id',
    ))
    mock_make_repo.assert_called_once_with(
        '.',
        language='ruby', name='scss-lint', description='',
        entry='scss-lint-entry',
        id='scss-lint-id', match_key='files', match_val=r'\.scss$', args='[]',
        require_serial='false', minimum_pre_commit_version='0',
        version_exclude='!.*',
    )


def test_main_defaults_entry_to_package_name(mock_make_repo):
    assert not main.main((
        '.',
        '--language', 'ruby',
        '--package-name', 'scss-lint',
        '--files-regex', r'\.scss$',
    ))
    assert mock_make_repo.call_args[1]['entry'] == 'scss-lint'


def test_main_defaults_id_to_entry(mock_make_repo):
    assert not main.main((
        '.',
        '--language', 'ruby',
        '--package-name', 'scss-lint',
        '--entry', 'scss-lint',
        '--files-regex', r'\.scss$',
    ))
    assert mock_make_repo.call_args[1]['id'] == 'scss-lint'


def test_main_with_args(mock_make_repo):
    assert not main.main((
        '.',
        '--language', 'python',
        '--package-name', 'yapf',
        '--files-regex', r'\.py$',
        r'--args=-i,--ignore=E265\,E501',
    ))
    expected = '["-i", "--ignore=E265,E501"]'
    assert mock_make_repo.call_args[1]['args'] == expected


def test_main_with_types_and_types_or(mock_make_repo, capsys):
    with pytest.raises(SystemExit) as exc_info:
        main.main((
            '.',
            '--language', 'python',
            '--package-name', 'yapf',
            '--types=c',
            '--types-or=c',
            '--types-or=c++',
        ))

    assert exc_info.value.args[0] == 2

    out, err = capsys.readouterr()
    assert out == ''
    assert 'argument --types-or: not allowed with argument --types' in err


def test_main_types(mock_make_repo):
    assert not main.main((
        '.',
        '--language', 'python',
        '--package-name', 'yapf',
        '--types=c',
    ))
    print(mock_make_repo.call_args[1])
    assert mock_make_repo.call_args[1]['match_key'] == 'types'
    assert mock_make_repo.call_args[1]['match_val'] == '[c]'
    assert mock_make_repo.call_args[1]['minimum_pre_commit_version'] == '0'


def test_main_types_or_multi(mock_make_repo):
    assert not main.main((
        '.',
        '--language', 'python',
        '--package-name', 'yapf',
        '--types-or=c++',
        '--types-or=c',
    ))
    print(mock_make_repo.call_args[1])
    assert mock_make_repo.call_args[1]['match_key'] == 'types_or'
    assert mock_make_repo.call_args[1]['match_val'] == '[c++, c]'
    assert mock_make_repo.call_args[1]['minimum_pre_commit_version'] == '2.9.2'


def test_main_errors_when_hook_id_has_spaces(mock_make_repo):
    with pytest.raises(SystemExit) as excinfo:
        main.main((
            '.',
            '--language', 'python',
            '--package-name', 'clang-format',
            '--entry', 'clang-format -i',
            '--types', 'c',
        ))
    msg, = excinfo.value.args
    assert msg == (
        'hook id should not contain spaces, perhaps specify --id?\n\n'
        '-   id: clang-format -i'
    )
