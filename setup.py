import codecs
import os.path
from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

setup(
    name='netbox-plugin-reloader',
    version=get_version('netbox_plugin_reloader/version.py'),
    description='Dynamically reload NetBox plugins without server restart',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Kani999/netbox-plugin-reloader',
    author="Jan Krupa",
    license='Apache 2',
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.10',
    classifiers=[
        'Intended Audience :: Developers',
        'Framework :: Django',
        'Framework :: Django :: 5.0',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
    ],
    keywords=['netbox', 'netbox-plugin'],
)