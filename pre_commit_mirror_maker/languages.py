from __future__ import annotations

import json
import subprocess
import urllib.request

from packaging import requirements
from packaging import version


def ruby_get_package_versions(package_name: str) -> list[str]:
    url = f'https://rubygems.org/api/v1/versions/{package_name}.json'
    resp = json.load(urllib.request.urlopen(url))
    return list(reversed([version['number'] for version in resp]))


def node_get_package_versions(package_name: str) -> list[str]:
    cmd = ('npm', 'view', package_name, '--json')
    output = json.loads(subprocess.check_output(cmd))
    return output['versions']


def python_get_package_versions(package_name: str) -> list[str]:
    pypi_name = requirements.Requirement(package_name).name
    url = f'https://pypi.org/pypi/{pypi_name}/json'
    resp = json.load(urllib.request.urlopen(url))
    return sorted(resp['releases'], key=lambda k: version.parse(k))


def rust_get_package_versions(package_name: str) -> list[str]:
    url = f'https://crates.io/api/v1/crates/{package_name}'
    resp = json.load(urllib.request.urlopen(url))
    return list(reversed([version['num'] for version in resp['versions']]))


def docker_image_get_package_versions(package_name: str) -> list[str]:
    # If package_name contains a slash, it's a user/org repository,
    # otherwise it's an official repository
    if '/' not in package_name:
        package_name = f'library/{package_name}'
    base_url = (
        'https://hub.docker.com/v2/repositories/'
        f'{package_name}/tags?page_size=100'
    )

    all_tags: list[str] = []
    url = base_url

    # Fetch all pages of results
    while url:
        resp = json.load(urllib.request.urlopen(url))
        # Add tags from the current page
        all_tags.extend(tag['name'] for tag in resp['results'])
        # Get URL for next page, if any
        url = resp.get('next')

    return list(reversed(all_tags))


def node_get_additional_dependencies(
        package_name: str, package_version: str,
) -> list[str]:
    return [f'{package_name}@{package_version}']


def rust_get_additional_dependencies(
        package_name: str, package_version: str,
) -> list[str]:
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
