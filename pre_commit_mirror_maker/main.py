import argparse
import json

from pre_commit_mirror_maker.make_repo import LIST_VERSIONS
from pre_commit_mirror_maker.make_repo import make_repo


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


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'repo_path',
        help='Local path where the git repo is checked out.',
    )
    parser.add_argument(
        '--language', required=True, choices=LIST_VERSIONS,
        help='Which language to use.',
    )
    parser.add_argument(
        '--package-name', required=True,
        help='Package name as it appears on the remote package manager.',
    )

    mutex = parser.add_mutually_exclusive_group(required=True)
    mutex.add_argument(
        '--files-regex', help='Files regex to use in hooks.yaml',
    )
    mutex.add_argument('--types', help='`identify` type to match')

    parser.add_argument(
        '--entry', help='Entry point, defaults to the package name.',
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

    make_repo(
        args.repo_path,
        name=args.package_name,
        language=args.language,
        entry=args.entry or args.package_name,
        match_key='types' if args.types else 'files',
        match_val=f'[{args.types}]' if args.types else args.files_regex,
        args=json.dumps(split_by_commas(args.args)),
    )


if __name__ == '__main__':
    exit(main())
