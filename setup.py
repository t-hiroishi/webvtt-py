"""webvtt-py setuptools configuration."""

import re
import pathlib

from setuptools import setup, find_packages

version = (
    re.search(
        r'__version__ = \'(.*?)\'',
        pathlib.Path('webvtt/__init__.py').read_text()
        ).group(1)
    )

setup(
    name='webvtt-py',
    version=version,
    description='WebVTT reader, writer and segmenter',
    long_description=pathlib.Path('README.rst').read_text(),
    author='Alejandro Mendez',
    author_email='amendez23@gmail.com',
    url='https://github.com/glut23/webvtt-py',
    packages=find_packages('.', exclude=['tests']),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'webvtt=webvtt.cli:main'
        ]
    },
    license='MIT',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='webvtt captions',
)
