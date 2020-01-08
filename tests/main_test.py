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
        '--id', 'my-scss-lint',
    ))
    mock_make_repo.assert_called_once_with(
        '.',
        language='ruby', name='scss-lint', entry='scss-lint-entry',
        id='my-scss-lint', match_key='files', match_val=r'\.scss$', args='[]',
        require_serial='false',
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
        '--language', 'docker_image',
        '--package-name', 'mvdan/shfmt',
        '--types', 'shell',
        '--entry', 'shfmt',
    ))
    assert mock_make_repo.call_args[1]['id'] == 'shfmt'


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
