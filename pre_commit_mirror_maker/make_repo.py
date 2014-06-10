from __future__ import unicode_literals

import contextlib
import io
import os
import os.path
import pkg_resources
import requests
import simplejson
import subprocess

from pre_commit_mirror_maker import five
from pre_commit_mirror_maker.util import from_utf8


# pylint:disable=star-args,too-many-arguments


def get_output(*cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    assert not proc.returncode, (proc.returncode, stdout, stderr)
    return from_utf8(stdout)


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
        contents = io.open(os.path.join(src, filename)).read()
        output_contents = contents.format(**format_vars)
        with io.open(os.path.join(dest, filename), 'w') as file_obj:
            file_obj.write(output_contents)


GEMS_API_URL = 'https://rubygems.org/api/v1/versions/{0}.json'


def ruby_get_package_versions(package_name):
    resp = requests.get(GEMS_API_URL.format(package_name)).json()
    return list(reversed([version['number'] for version in resp]))


def node_get_package_versions(package_name):
    output = simplejson.loads(get_output(
        'npm', 'view', package_name, '--json',
    ))
    return output['versions']


def python_get_package_versions(package_name):
    client = five.xmlrpclib.ServerProxy('https://pypi.python.org/pypi')
    versions = client.package_releases(package_name, True)
    return list(reversed([from_utf8(version) for version in versions]))


VERSION_LIST_FUNCTIONS = {
    'node': node_get_package_versions,
    'python': python_get_package_versions,
    'ruby': ruby_get_package_versions,
}


def _apply_version_and_commit(
        version,
        language,
        package_name,
        files_regex,
        entry
):
    # Write the version file
    with io.open('.version', 'w') as version_file:
        version_file.write(version)

    # Write the language-specific files
    src_dir = pkg_resources.resource_filename(
        'pre_commit_mirror_maker', language,
    )
    format_files_to_directory(
        src_dir,
        '.',
        {
            'version': version,
            'language': language,
            'name': package_name,
            'files': files_regex,
            'entry': entry,
        },
    )

    # Commit and tag
    subprocess.check_call(['git', 'add', '.'])
    subprocess.check_call([
        'git', 'commit', '-m', 'Mirror: {0}'.format(version)
    ])
    subprocess.check_call(['git', 'tag', 'v{0}'.format(version)])


def make_repo(
        repo,
        language,
        package_name,
        files_regex,
        entry,
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
            )
