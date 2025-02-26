import codecs
import os.path
import re
from setuptools import find_packages, setup

# Read version from version.py without importing the package
def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")

def get_name(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__title__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find name string.")

def get_description(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__description__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find description string.")

setup(
    name=get_name("plugin_reloader/version.py"),
    version=get_version("plugin_reloader/version.py"),
    description=get_description("plugin_reloader/version.py"),
    long_description=read("README.md") if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    author="Jan Krupa",
    author_email="jan.krupa@cesnet.cz",
    url="https://github.com/kani999/netbox-plugin-reloader",
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.10',
    keywords=['netbox', 'netbox-plugin'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Framework :: Django',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Networking',
    ],
)

