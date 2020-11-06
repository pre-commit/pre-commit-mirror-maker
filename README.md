[![Build Status](https://dev.azure.com/asottile/asottile/_apis/build/status/pre-commit.pre-commit-mirror-maker?branchName=master)](https://dev.azure.com/asottile/asottile/_build/latest?definitionId=59&branchName=master)
[![Azure DevOps coverage](https://img.shields.io/azure-devops/coverage/asottile/asottile/59/master.svg)](https://dev.azure.com/asottile/asottile/_build/latest?definitionId=59&branchName=master)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/pre-commit/pre-commit-mirror-maker/master.svg)](https://results.pre-commit.ci/latest/github/pre-commit/pre-commit-mirror-maker/master)

pre-commit-mirror-maker
=======================

Scripts for creating mirror repositories that do not have
.pre-commit-hooks.yaml


### Installation

`$ pip install pre-commit-mirror-maker`


### Sample Usage

```
$ pre-commit-mirror --help
usage: pre-commit-mirror [-h] --language {node,python,ruby,rust}
                         --package-name PACKAGE_NAME
                         (--files-regex FILES_REGEX | --types TYPES)
                         [--entry ENTRY] [--args ARGS]
                         repo_path

positional arguments:
  repo_path             Local path where the git repo is checked out.

optional arguments:
  -h, --help            show this help message and exit
  --language {node,python,ruby,rust}
                        Which language to use.
  --package-name PACKAGE_NAME
                        Package name as it appears on the remote package
                        manager.
  --files-regex FILES_REGEX
                        Files regex to use in hooks.yaml
  --types TYPES         `identify` type to match
  --id ID               Hook id, defaults to the entry point.
  --entry ENTRY         Entry point, defaults to the package name.
  --args ARGS           Comma separated arguments for the hook. Escape commas
                        in args with a backslash (\). For example: --args='-i,
                        --ignore=E265\,E501' would give you [-i,
                        --ignore=E265,E501]
```


For example: making a mirror of the yapf package:

```console
$ git init mirrors-yapf
Initialized empty Git repository in /tmp/mirrors-yapf/.git/

$ pre-commit-mirror mirrors-yapf --language python --package-name yapf --args=-i --types python
[master (root-commit) 88bffee] Mirror: 0.1.3
 3 files changed, 16 insertions(+)
 create mode 100644 .pre-commit-hooks.yaml
 create mode 100644 .version
 create mode 100644 setup.py
[master 24cd5f4] Mirror: 0.1.4
 2 files changed, 2 insertions(+), 2 deletions(-)
[master 6695a76] Mirror: 0.1.5

...

[master 091ab92] Mirror: 0.22.0
 2 files changed, 2 insertions(+), 2 deletions(-)

$ ls -al mirrors-yapf/
total 24
drwxrwxr-x 3 asottile asottile 4096 May 26 10:00 .
drwxrwxr-x 8 asottile asottile 4096 May 26 10:00 ..
drwxrwxr-x 8 asottile asottile 4096 May 26 10:00 .git
-rw-rw-r-- 1 asottile asottile  136 May 26 10:00 .pre-commit-hooks.yaml
-rw-rw-r-- 1 asottile asottile  137 May 26 10:00 setup.py
-rw-rw-r-- 1 asottile asottile    7 May 26 10:00 .version
```
