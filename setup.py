from setuptools import setup, find_packages
from version import __version__

with open('requirements.txt') as fp:
    install_requires = fp.readlines()

dependency_links = [
    # External repositories different from pypi
]

setup(
    name='splight-cli',
    version=__version__,
    author='Splight',
    author_email='factory@splight-ae.com',
    description='CLI tool to build and run Splight components',
    py_modules=['splight'],
    install_requires=install_requires,
    packages=find_packages(),
    package_data={
        'cli': [
            'component/templates/*',
            'datalake/dump_example.csv',
        ],
    },
    include_package_data=True,
    dependency_links=dependency_links,
    entry_points={
        'console_scripts': [
            'splight = cli:cli.app',
        ],
    },
)
