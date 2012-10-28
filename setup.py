import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import orgviz


def allfiles(directory):
    files = []
    nondir = lambda x: not os.path.isdir(x)
    extendfiles = lambda _, d, fs: \
        files.extend(filter(nondir, (os.path.join(d, f) for f in fs)))
    os.path.walk(directory, extendfiles, None)
    return files


setup(
    name='orgviz',
    version=orgviz.__version__,
    packages=['orgviz', 'orgviz.tests', 'orgviz.utils'],
    package_data={
        'orgviz': (
            [os.path.join('templates', '*.html')]
            + [f[len('orgviz' + os.path.sep):] for f in
               allfiles(os.path.join('orgviz', 'static'))]
        ),
    },
    author=orgviz.__author__,
    author_email='aka.tkf@gmail.com',
    url='https://github.com/tkf/orgviz',
    license=orgviz.__license__,
    description='view org-mode files from different directions',
    long_description=orgviz.__doc__,
    keywords='org, org-mode, Emacs',
    classifiers=[
        "Development Status :: 3 - Alpha",
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # see: http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    entry_points={
        'console_scripts': [
            'orgviz = orgviz.cli:main',
        ],
    },
    install_requires=[
        'argparse',
        'flask',
        'orgparse',
    ],
)
