from __future__ import unicode_literals

import mock

from pre_commit_mirror_maker.main import main


def test_main_passes_args():
    mock_make_repo = mock.Mock(return_value=0)
    ret = main(
        argv=[
            '.', 'ruby', 'scss-lint', r'\.scss$', '--entry', 'scss-lint-entry',
        ],
        make_repo_fn=mock_make_repo,
    )
    assert ret == 0
    mock_make_repo.assert_called_once_with(
        '.', 'ruby', 'scss-lint', r'\.scss$', 'scss-lint-entry', (),
    )


def test_main_defaults_entry_to_package_name():
    mock_make_repo = mock.Mock(return_value=0)
    ret = main(
        argv=['.', 'ruby', 'scss-lint', r'\.scss$'],
        make_repo_fn=mock_make_repo,
    )
    assert ret == 0
    mock_make_repo.assert_called_once_with(
        '.', 'ruby', 'scss-lint', r'\.scss$', 'scss-lint', (),
    )


def test_main_with_args():
    mock_make_repo = mock.Mock(return_value=0)
    main(
        argv=[
            '.', 'python', 'yapf', r'\.py$',
            r'--args=-i,--ignore=E265\,E309\,E501',
        ],
        make_repo_fn=mock_make_repo,
    )
    mock_make_repo.assert_called_once_with(
        '.', 'python', 'yapf', r'\.py$', 'yapf',
        ('-i', '--ignore=E265,E309,E501'),
    )
