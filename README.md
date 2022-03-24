[![Build Status](https://dev.azure.com/asottile/asottile/_apis/build/status/pre-commit.pre-commit-mirror-maker?branchName=main)](https://dev.azure.com/asottile/asottile/_build/latest?definitionId=59&branchName=main)
[![Azure DevOps coverage](https://img.shields.io/azure-devops/coverage/asottile/asottile/59/main.svg)](https://dev.azure.com/asottile/asottile/_build/latest?definitionId=59&branchName=main)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/pre-commit/pre-commit-mirror-maker/main.svg)](https://results.pre-commit.ci/latest/github/pre-commit/pre-commit-mirror-maker/main)

pre-commit-mirror-maker
=======================

Scripts for creating mirror repositories that do not have
.pre-commit-hooks.yaml


### Installation

`$ pip install pre-commit-mirror-maker`


### Sample Usage

To see all supported configuration options, run:

```console
$ pre-commit-mirror --help
```

For example: making a mirror of the yapf package:

```console
$ git init mirrors-yapf
Initialized empty Git repository in /tmp/mirrors-yapf/.git/

$ pre-commit-mirror mirrors-yapf --language python --package-name yapf --args=-i --types python
[main (root-commit) 88bffee] Mirror: 0.1.3
 3 files changed, 16 insertions(+)
 create mode 100644 .pre-commit-hooks.yaml
 create mode 100644 .version
 create mode 100644 setup.py
[main 24cd5f4] Mirror: 0.1.4
 2 files changed, 2 insertions(+), 2 deletions(-)
[main 6695a76] Mirror: 0.1.5

...

[main 091ab92] Mirror: 0.22.0
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
