from __future__ import annotations

import argparse
import json
from typing import Sequence

from pre_commit_mirror_maker.make_repo import LIST_VERSIONS
from pre_commit_mirror_maker.make_repo import make_repo


def split_by_commas(maybe_s: str) -> tuple[str, ...]:
    """Split a string by commas, but allow escaped commas.
    - If maybe_s is falsey, returns an empty tuple
    - Ignore backslashed commas
    """
    if not maybe_s:
        return ()
    parts: list[str] = []
    split_by_backslash = maybe_s.split(r'\,')
    for split_by_backslash_part in split_by_backslash:
        splitby_comma = split_by_backslash_part.split(',')
        if parts:
            parts[-1] += ',' + splitby_comma[0]
        else:
            parts.append(splitby_comma[0])
        parts.extend(splitby_comma[1:])
    return tuple(parts)


def main(argv: Sequence[str] | None = None) -> int:
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
    parser.add_argument(
        '--description', help='Hook description.', default='',
    )

    mutex = parser.add_mutually_exclusive_group(required=True)
    mutex.add_argument(
        '--files-regex', help='Files regex to use in hooks.yaml',
    )
    mutex.add_argument('--types', help='`identify` type to AND match')
    mutex.add_argument(
        '--types-or', action='append', help='`identify` type to OR match',
    )

    parser.add_argument(
        '--id', help='Hook id, defaults to the entry point.',
    )
    parser.add_argument(
        '--entry', help='Entry point, defaults to the package name.',
    )
    parser.add_argument(
        '--args',
        help=(
            'Comma separated arguments for the hook.  Escape commas in args '
            'with a backslash (\\).  '
            r"For example: --args='-i,--ignore=E265\,E501' would give "
            'you [-i, --ignore=E265,E501]'
        ),
    )
    parser.add_argument(
        '--require-serial', action='store_true',
        help='Set `require_serial: true` for the hook',
    )
    args = parser.parse_args(argv)

    minimum_pre_commit_version = '0'

    if args.types_or:
        match_key = 'types_or'
        match_val = '[{}]'.format(', '.join(args.types_or))
        minimum_pre_commit_version = '2.9.2'
    elif args.types:
        match_key = 'types'
        match_val = f'[{args.types}]'
    else:
        match_key = 'files'
        match_val = args.files_regex

    hook_id = args.id or args.entry or args.package_name
    if ' ' in hook_id:
        raise SystemExit(
            f'hook id should not contain spaces, perhaps specify --id?\n\n'
            f'-   id: {hook_id}',
        )

    make_repo(
        args.repo_path,
        name=args.package_name,
        description=args.description,
        language=args.language,
        entry=args.entry or args.package_name,
        id=hook_id,
        match_key=match_key,
        match_val=match_val,
        args=json.dumps(split_by_commas(args.args)),
        require_serial=json.dumps(args.require_serial),
        minimum_pre_commit_version=minimum_pre_commit_version,
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
