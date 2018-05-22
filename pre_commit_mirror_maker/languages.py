import json
import subprocess
import urllib.request
import xmlrpc.client


def ruby_get_package_versions(package_name):
    url = f'https://rubygems.org/api/v1/versions/{package_name}.json'
    resp = json.load(urllib.request.urlopen(url))
    return list(reversed([version['number'] for version in resp]))


def node_get_package_versions(package_name):
    cmd = ('npm', 'view', package_name, '--json')
    output = json.loads(subprocess.check_output(cmd))
    return output['versions']


def python_get_package_versions(package_name):
    client = xmlrpc.client.ServerProxy('https://pypi.org/pypi')
    versions = client.package_releases(package_name, True)
    return list(reversed(versions))


LIST_VERSIONS = {
    'node': node_get_package_versions,
    'python': python_get_package_versions,
    'ruby': ruby_get_package_versions,
}
