# -*- coding: utf-8 -*-
"""Installer for the jazkarta.easyformplugin.savecontent package."""

from setuptools import find_packages
from setuptools import setup
import sys


long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("CONTRIBUTORS.rst").read(),
        open("CHANGES.rst").read(),
    ]
)

setup(
    name="jazkarta.easyformplugin.savecontent",
    version="1.0a1",
    description="Adds adapter to collective.easyform to save data as DX content object.",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone CMS",
    author="Jazkarta",
    author_email="info@jazkarta.com",
    url="https://github.com/collective/jazkarta.easyformplugin.savecontent",
    project_urls={
        "PyPI": "https://pypi.python.org/pypi/jazkarta.easyformplugin.savecontent",
        "Source": "https://github.com/collective/jazkarta.easyformplugin.savecontent",
        "Tracker": "https://github.com/collective/jazkarta.easyformplugin.savecontent/issues",
        # 'Documentation': 'https://jazkarta.easyformplugin.savecontent.readthedocs.io/en/latest/',
    },
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["jazkarta", "jazkarta.easyformplugin"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*",
    install_requires=[
        "setuptools",
        "collective.easyform",
        "plone.restapi",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            "plone.testing>=5.0.0",
            "plone.app.contenttypes",
            "plone.app.robotframework[debug]",
            'vcrpy<4; python_version<"3"',
            "vcrpy",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = jazkarta.easyformplugin.savecontent.locales.update:update_locale
    """,
)
