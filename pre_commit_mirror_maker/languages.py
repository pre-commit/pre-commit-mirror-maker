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
    versions = output['versions']
    dist_tags = output.get('dist-tags', {})
    latest = dist_tags.get('latest')
    latest_index = (
        versions.index(latest) if latest in versions else len(versions)
    )
    return output['versions'][: latest_index + 1]


def python_get_package_versions(package_name: str) -> list[str]:
    pypi_name = requirements.Requirement(package_name).name
    url = f'https://pypi.org/pypi/{pypi_name}/json'
    resp = json.load(urllib.request.urlopen(url))
    return sorted(resp['releases'], key=lambda k: version.parse(k))


def rust_get_package_versions(package_name: str) -> list[str]:
    url = f'https://crates.io/api/v1/crates/{package_name}'
    resp = json.load(urllib.request.urlopen(url))
    return list(reversed([version['num'] for version in resp['versions']]))


def node_get_additional_dependencies(
        package_name: str, package_version: str,
) -> list[str]:
    return [f'{package_name}@{package_version}']


def rust_get_additional_dependencies(
        package_name: str, package_version: str,
) -> list[str]:
    return [f'cli:{package_name}:{package_version}']


LIST_VERSIONS = {
    'node': node_get_package_versions,
    'python': python_get_package_versions,
    'ruby': ruby_get_package_versions,
    'rust': rust_get_package_versions,
}

ADDITIONAL_DEPENDENCIES = {
    'node': node_get_additional_dependencies,
    'rust': rust_get_additional_dependencies,
}
