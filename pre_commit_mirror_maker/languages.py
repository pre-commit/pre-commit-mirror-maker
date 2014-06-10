from __future__ import unicode_literals

import requests
import simplejson

from pre_commit_mirror_maker import five
from pre_commit_mirror_maker.util import from_utf8
from pre_commit_mirror_maker.util import get_output


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
