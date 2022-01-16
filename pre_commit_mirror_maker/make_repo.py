from __future__ import annotations

import json
import os.path
import subprocess

import pkg_resources

from pre_commit_mirror_maker.languages import ADDITIONAL_DEPENDENCIES
from pre_commit_mirror_maker.languages import LIST_VERSIONS


EXCLUDED_EXTENSIONS = ('.pyc',)


def format_files(src: str, dest: str, **fmt_vars: str) -> None:
    """Copies all files inside src into dest while formatting the contents
    of the files into the output.

    For example, a file with the following contents:

    {foo} bar {baz}

    and the vars {'foo': 'herp', 'baz': 'derp'}

    will end up in the output as

    herp bar derp
    :param text src: Source directory.
    :param text dest: Destination directory.
    :param dict fmt_vars: Vars to format into the files.
    """
    assert os.path.exists(src)
    assert os.path.exists(dest)
    # Only at the root.  Could be made more complicated and recursive later
    for filename in os.listdir(src):
        if filename.endswith(EXCLUDED_EXTENSIONS):
            continue
        # Flat directory structure
        elif not os.path.isfile(os.path.join(src, filename)):
            continue
        with open(os.path.join(src, filename)) as f:
            output_contents = f.read().format(**fmt_vars)
        with open(os.path.join(dest, filename), 'w') as file_obj:
            file_obj.write(output_contents)


def _commit_version(
        repo: str, *,
        language: str,
        version: str,
        **fmt_vars: str,
) -> None:
    # 'all' writes the .version and .pre-commit-hooks.yaml files
    for lang in ('all', language):
        src = pkg_resources.resource_filename('pre_commit_mirror_maker', lang)
        format_files(src, repo, language=language, version=version, **fmt_vars)

    hooks_yaml = os.path.join(repo, 'hooks.yaml')
    if os.path.exists(hooks_yaml):
        os.remove(hooks_yaml)

    def git(*cmd: str) -> None:
        subprocess.check_call(('git', '-C', repo) + cmd)

    # Commit and tag
    git('add', '.')
    git('commit', '-m', f'Mirror: {version}')
    git('tag', f'v{version}')


def make_repo(repo: str, *, language: str, name: str, **fmt_vars: str) -> None:
    assert os.path.exists(os.path.join(repo, '.git')), repo

    package_versions = LIST_VERSIONS[language](name)
    version_file = os.path.join(repo, '.version')
    if os.path.exists(version_file):
        previous_version = open(version_file).read().strip()
        previous_version_index = package_versions.index(previous_version)
        versions_to_apply = package_versions[previous_version_index + 1:]
    else:
        versions_to_apply = package_versions

    for version in versions_to_apply:
        if language in ADDITIONAL_DEPENDENCIES:
            additional_dependencies = ADDITIONAL_DEPENDENCIES[language](
                name,
                version,
            )
        else:
            additional_dependencies = []

        _commit_version(
            repo,
            name=name,
            language=language,
            version=version,
            additional_dependencies=json.dumps(additional_dependencies),
            **fmt_vars,
        )
