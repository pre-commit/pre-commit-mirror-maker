from setuptools import find_packages
from setuptools import setup


setup(
    name='pre-commit-mirror-maker',
    description="Scripts for creating mirror repositories that do not have hooks.yaml",
    url='https://github.com/pre-commit/pre-commit-mirror-maker',
    version='0.4.0',

    author='Anthony Sottile',
    author_email='asottile@umich.edu',

    platforms='all',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    packages=find_packages(exclude=('tests*', 'testing*')),
    install_requires=[
        'pyyaml',
        'requests',
    ],

    entry_points={
        'console_scripts': [
            'pre-commit-mirror = pre_commit_mirror_maker.main:main',
        ],
    },
    package_data={
        'pre_commit_mirror_maker': [
            'all/.pre-commit-hooks.yaml',
            'all/.version',
            'node/.npmignore',
            'node/.pre-commit-hooks.yaml',
            'node/*',
            'python/*',
            'ruby/*',
        ],
    },
)
