import json
import subprocess
import urllib.request
from typing import List

from packaging import version


def docker_image_get_package_versions(image_name: str) -> List[str]:
    """Returns the subset of tags that is formatted like versions.
    I.e. this will not return the typical docker tag 'latest', but will return
    tags like 'v1.2.3' or '1.2.3'.
    See https://packaging.pypa.io/en/latest/version/ for more information.
    """
    if len(image_name.split('/')) != 2:
        raise Exception(
            'Only canonical DockerHub images <user>/<repo> supported.',
        )
    url = f'https://registry.hub.docker.com/v1/repositories/{image_name}/tags'
    resp = json.load(urllib.request.urlopen(url))
    versions = []
    for tag in [info['name'] for info in resp]:
        if isinstance(version.parse(tag), version.Version):
            versions.append(tag)
    return sorted(versions)


def ruby_get_package_versions(package_name: str) -> List[str]:
    url = f'https://rubygems.org/api/v1/versions/{package_name}.json'
    resp = json.load(urllib.request.urlopen(url))
    return list(reversed([version['number'] for version in resp]))


def node_get_package_versions(package_name: str) -> List[str]:
    cmd = ('npm', 'view', package_name, '--json')
    output = json.loads(subprocess.check_output(cmd))
    return output['versions']


def python_get_package_versions(package_name: str) -> List[str]:
    url = f'https://pypi.org/pypi/{package_name}/json'
    resp = json.load(urllib.request.urlopen(url))
    return sorted(resp['releases'], key=lambda k: version.parse(k))


def rust_get_package_versions(package_name: str) -> List[str]:
    url = f'https://crates.io/api/v1/crates/{package_name}'
    resp = json.load(urllib.request.urlopen(url))
    return list(reversed([version['num'] for version in resp['versions']]))


def node_get_additional_dependencies(
        package_name: str, package_version: str,
) -> List[str]:
    return [f'{package_name}@{package_version}']


def rust_get_additional_dependencies(
        package_name: str, package_version: str,
) -> List[str]:
    return [f'cli:{package_name}:{package_version}']


LIST_VERSIONS = {
    'docker_image': docker_image_get_package_versions,
    'node': node_get_package_versions,
    'python': python_get_package_versions,
    'ruby': ruby_get_package_versions,
    'rust': rust_get_package_versions,
}

ADDITIONAL_DEPENDENCIES = {
    'node': node_get_additional_dependencies,
    'rust': rust_get_additional_dependencies,
}
