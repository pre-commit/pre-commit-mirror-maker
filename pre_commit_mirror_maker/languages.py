from __future__ import annotations

import json
import os
import re
import subprocess
import urllib.error
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


def golang_get_package_versions(package_name: str) -> list[str]:
    # https://pkg.go.dev/golang.org/x/mod/module#EscapePath
    # https://github.com/golang/mod/blob/d271cf332fd221d661d13b186b51a11d7e66ff74/module/module.go#L707
    escaped = re.sub(
        r'[A-Z]',
        lambda m: f'!{m.group(0).lower()}', package_name,
    )

    # Greedily choose the longest non-404 path
    # (based on https://go.dev/ref/mod#resolve-pkg-mod)
    while escaped:
        url = f'https://proxy.golang.org/{escaped}/@v/list'
        try:
            resp = urllib.request.urlopen(url).read().decode()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                escaped = os.path.dirname(escaped)
                continue
            raise

        return sorted(
            (v.removeprefix('v') for v in resp.splitlines()),
            key=version.parse,
        )

    raise ValueError(
        f'Cannot find package name {package_name} on proxy.golang.org',
    )


def node_get_additional_dependencies(
        package_name: str, package_version: str,
) -> list[str]:
    return [f'{package_name}@{package_version}']


def rust_get_additional_dependencies(
        package_name: str, package_version: str,
) -> list[str]:
    return [f'cli:{package_name}:{package_version}']


def golang_get_additional_dependencies(
        package_name: str, package_version: str,
) -> list[str]:
    return [f'{package_name}@v{package_version}']


LIST_VERSIONS = {
    'golang': golang_get_package_versions,
    'node': node_get_package_versions,
    'python': python_get_package_versions,
    'ruby': ruby_get_package_versions,
    'rust': rust_get_package_versions,
}

ADDITIONAL_DEPENDENCIES = {
    'golang': golang_get_additional_dependencies,
    'node': node_get_additional_dependencies,
    'rust': rust_get_additional_dependencies,
}
