from __future__ import unicode_literals

import argparse

from pre_commit_mirror_maker.make_repo import make_repo
from pre_commit_mirror_maker.make_repo import VERSION_LIST_FUNCTIONS
from pre_commit_mirror_maker.util import from_utf8
from pre_commit_mirror_maker.util import split_by_commas


def main(argv=None, make_repo_fn=None):
    make_repo_fn = make_repo_fn or make_repo

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'repo_path',
        help='Local path where the git repo is checked out.',
    )
    parser.add_argument(
        'language',
        choices=VERSION_LIST_FUNCTIONS.keys(),
        help='Which language to use.',
    )
    parser.add_argument(
        'package_name',
        help='Package name as it appears on the remote package manager.',
    )
    parser.add_argument(
        'files_regex',
        help='Files regex to use in hooks.yaml',
    )
    parser.add_argument(
        '--entry',
        help='Entry point, defaults to the package name.',
    )
    parser.add_argument(
        '--args',
        help=(
            'Comma separated arguments for the hook.  Escape commas in args '
            'with a backslash (\\).  '
            r"For example: --args='-i,--ignore=E265\,E309\,E501' would give "
            'you [-i, --ignore=E265,E309,E501]'
        ),
    )
    args = parser.parse_args(argv)

    repo_path = from_utf8(args.repo_path)
    language = from_utf8(args.language)
    package_name = from_utf8(args.package_name)
    files_regex = from_utf8(args.files_regex)
    hook_args = split_by_commas(from_utf8(args.args))

    if args.entry is None:
        entry = package_name
    else:
        entry = from_utf8(args.entry)

    return make_repo_fn(
        repo_path, language, package_name, files_regex, entry, hook_args,
    )


if __name__ == '__main__':
    exit(main())
