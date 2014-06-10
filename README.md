[![Build Status](https://travis-ci.org/pre-commit/pre-commit-mirror-maker.svg?branch=master)](https://travis-ci.org/pre-commit/pre-commit-mirror-maker)
[![Coverage Status](https://img.shields.io/coveralls/pre-commit/pre-commit-mirror-maker.svg?branch=master)](https://coveralls.io/r/pre-commit/pre-commit-mirror-maker)

pre-commit-mirror-maker
==========

Scripts for creating mirror repositories that do not have hooks.yaml


### Installation

`$ pip install pre-commit-mirror-maker`


### Sample Usage

    $ pre-commit-mirror --help
    usage: pre-commit-mirror [-h] [--entry ENTRY]
                             repo_path {node,python,ruby} package_name files_regex

    positional arguments:
      repo_path           Local path where the git repo is checked out.
      {node,python,ruby}  Which language to use.
      package_name        Package name as it appears on the remote package
                          manager.
      files_regex         Files regex to use in hooks.yaml

    optional arguments:
      -h, --help          show this help message and exit
      --entry ENTRY       Entry point, defaults to the package name.


For example: making a mirror of the scss-lint gem


    $ git init scss-lint-mirror
    Initialized empty Git repository in /tmp/scss-lint-mirror/.git/
    $ pre-commit-mirror scss-lint-mirror ruby scss-lint '\.scss$'
    [master (root-commit) 18fcbd9] Mirror: 0.1
     3 files changed, 14 insertions(+)
     create mode 100644 .version
     create mode 100644 __fake_gem.gemspec
     create mode 100644 hooks.yaml
    [master 145ced4] Mirror: 0.2
     2 files changed, 2 insertions(+), 2 deletions(-)
    [master f575b53] Mirror: 0.3
     2 files changed, 2 insertions(+), 2 deletions(-)
    [master bcf6b11] Mirror: 0.4

    ...

    [master 26e2058] Mirror: 0.24.0
     2 files changed, 2 insertions(+), 2 deletions(-)
    [master d1f8e64] Mirror: 0.24.1
     2 files changed, 2 insertions(+), 2 deletions(-)

    $ ls -al scss-lint-mirror/
    total 60
    drwxrwxr-x  3 asottile asottile  4096 Jun 10 09:00 .
    drwxrwxrwt 23 root     root     36864 Jun 10 08:59 ..
    -rw-rw-r--  1 asottile asottile   267 Jun 10 09:00 __fake_gem.gemspec
    drwxrwxr-x  8 asottile asottile  4096 Jun 10 09:00 .git
    -rw-rw-r--  1 asottile asottile    97 Jun 10 09:00 hooks.yaml
    -rw-rw-r--  1 asottile asottile     6 Jun 10 09:00 .version
