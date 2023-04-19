from setuptools import find_packages, setup
from version import __version__

with open("requirements.txt") as fp:
    install_requires = fp.readlines()

dependency_links = [
    # External repositories different from pypi
]

test_requires = [
    "pytest==7.1.2",
    "mock==4.0.3",
]

setup(
    name="splight-cli",
    version=__version__,
    author="Splight",
    author_email="factory@splight-ae.com",
    description="CLI tool to build and run Splight components",
    py_modules=["splight"],
    install_requires=install_requires,
    packages=find_packages(),
    package_data={
        "cli": [
            "component/templates/*",
            "component/templates/.splightignore",
            "datalake/dump_example.csv",
        ],
    },
    include_package_data=True,
    dependency_links=dependency_links,
    entry_points={
        "console_scripts": [
            "splight = cli.cli:app",
        ],
    },
    extras_require={
        "test": test_requires,
        "dev": test_requires
        + [
            "flake8==6.0.0",
            "ipython==8.12.0",
            "ipdb==0.13.13",
            "pre-commit==3.2.2",
            "black==23.3.0",
            "isort==5.12.0",
        ],
    },
)
