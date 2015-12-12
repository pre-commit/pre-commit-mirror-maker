from __future__ import unicode_literals

import contextlib
import io
import os
import os.path
import subprocess

import pkg_resources
import yaml

from pre_commit_mirror_maker.languages import VERSION_LIST_FUNCTIONS


# pylint:disable=star-args,too-many-arguments


EXCLUDED_EXTENSIONS = frozenset(('.pyc',))


@contextlib.contextmanager
def cwd(directory):
    original_cwd = os.getcwd()
    os.chdir(directory)
    try:
        yield
    finally:
        os.chdir(original_cwd)


def format_files_to_directory(src, dest, format_vars):
    """Copies all files inside src into dest while formatting the contents
    of the files into the output.

    For example, a file with the following contents:

    {foo} bar {baz}

    and the vars {'foo': 'herp', 'baz': 'derp'}

    will end up in the output as

    herp bar derp
    :param text src: Source directory.
    :param text dest: Destination directory.
    :param dict format_vars: Vars to format into the files.
    """
    assert os.path.exists(src)
    assert os.path.exists(dest)
    # Only at the root.  Could be made more complicated and recursive later
    for filename in os.listdir(src):
        if any(
                filename.endswith(extension)
                for extension in EXCLUDED_EXTENSIONS
        ):
            continue
        # Flat directory structure
        if not os.path.isfile(os.path.join(src, filename)):
            continue
        contents = io.open(os.path.join(src, filename)).read()
        output_contents = contents.format(**format_vars)
        with io.open(os.path.join(dest, filename), 'w') as file_obj:
            file_obj.write(output_contents)


def _apply_version_and_commit(
        version,
        language,
        package_name,
        files_regex,
        entry,
        args,
):
    format_vars = {
        'version': version,
        'language': language,
        'name': package_name,
        'files': files_regex,
        'entry': entry,
        'args': yaml.safe_dump(args),
    }

    # Write the version file
    with io.open('.version', 'w') as version_file:
        version_file.write(version)

    # Write the hooks.yaml file
    hooks_yaml_filename = pkg_resources.resource_filename(
        'pre_commit_mirror_maker', 'hooks.yaml.template',
    )
    hooks_yaml_contents = io.open(hooks_yaml_filename).read()
    with io.open('hooks.yaml', 'w') as hooks_file:
        hooks_file.write(hooks_yaml_contents.format(**format_vars))

    # Write the language-specific files
    src_dir = pkg_resources.resource_filename(
        'pre_commit_mirror_maker', language,
    )
    format_files_to_directory(src_dir, '.', format_vars)

    # Commit and tag
    subprocess.check_call(('git', 'add', '.'))
    subprocess.check_call((
        'git', 'commit', '-m', 'Mirror: {0}'.format(version)
    ))
    subprocess.check_call(('git', 'tag', 'v{0}'.format(version)))


def make_repo(
        repo,
        language,
        package_name,
        files_regex,
        entry,
        args,
        version_list_fn_map=None,
):
    version_list_fn_map = version_list_fn_map or VERSION_LIST_FUNCTIONS
    assert os.path.exists(os.path.join(repo, '.git'))
    assert language in version_list_fn_map

    with cwd(repo):
        package_versions = version_list_fn_map[language](package_name)
        if os.path.exists('.version'):
            previous_version = io.open('.version').read()
            previous_version_index = package_versions.index(previous_version)
            versions_to_apply = package_versions[previous_version_index + 1:]
        else:
            versions_to_apply = package_versions

        for version in versions_to_apply:
            _apply_version_and_commit(
                version,
                language,
                package_name,
                files_regex,
                entry,
                args,
            )
