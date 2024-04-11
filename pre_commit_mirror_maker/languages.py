from __future__ import annotations

import json
import subprocess
import urllib.request
from typing import Any

from packaging import requirements
from packaging import version


def ruby_get_package_versions(package_name: str) -> list[str]:
    url = f'https://rubygems.org/api/v1/versions/{package_name}.json'
    resp = json.load(urllib.request.urlopen(url))
    return list(reversed([version['number'] for version in resp]))


def _node_get_package_versions(package_json: dict[str, Any]) -> list[str]:
    versions = package_json['versions']
    version_timestamps = package_json['time']

    # Sort the versions according to their timestamps, to prevent versions
    # from being missed if they get released out of order.
    versions.sort(key=lambda e: version_timestamps.get(e, ''))
    return versions


def node_get_package_versions(package_name: str) -> list[str]:
    cmd = ('npm', 'view', package_name, '--json')
    output = json.loads(subprocess.check_output(cmd))
    return _node_get_package_versions(output)


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
