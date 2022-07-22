import os
from setuptools import setup, find_packages

with open('requirements.txt') as fp:
    install_requires = fp.readlines()

dependency_links = [
    # External repositories different from pypi
    "https://splight.jfrog.io/artifactory/api/pypi/splight-local/simple"
]
os.system("cat ~/.pypirc")

setup(
    name='splight-cli',
    version='0.1.7',
    author='Splight',
    author_email='factory@splight-ae.com',
    description='Splight developer CLI tool. Splight.',
    py_modules=['splightcli'],
    install_requires=install_requires,
    packages=find_packages(),
    package_data={'cli': ['component/templates/*', 'datalake/dump_example.csv']},
    include_package_data=True,
    dependency_links=dependency_links,
    entry_points={
        'console_scripts': [
            'splightcli = cli:cli',
        ],
    },
)
