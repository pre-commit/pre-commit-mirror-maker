import argparse

from pre_commit_mirror_maker.make_repo import make_repo
from pre_commit_mirror_maker.make_repo import VERSION_LIST_FUNCTIONS


def split_by_commas(maybe_s):
    """Split a string by commas, but allow escaped commas.
    - If maybe_s is falsey, returns an empty tuple
    - Ignore backslashed commas
    """
    if not maybe_s:
        return ()
    parts = []
    split_by_backslash = maybe_s.split(r'\,')
    for split_by_backslash_part in split_by_backslash:
        splitby_comma = split_by_backslash_part.split(',')
        if parts:
            parts[-1] += ',' + splitby_comma[0]
        else:
            parts.append(splitby_comma[0])
        parts.extend(splitby_comma[1:])
    return tuple(parts)


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

    repo_path = args.repo_path
    language = args.language
    package_name = args.package_name
    files_regex = args.files_regex
    hook_args = split_by_commas(args.args)
    entry = args.entry or package_name

    return make_repo_fn(
        repo_path, language, package_name, files_regex, entry, hook_args,
    )


if __name__ == '__main__':
    exit(main())
