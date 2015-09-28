#######################################################################
# Jinja2 pyblosxom renderer.
#
# Massively inspired by Sebastian Spaeth's Jinja2 renderer (and even
# borrows some code) but mostly reimplemented by Chris Webber.
#
# Copyright (c) 2010-2011 Sebastian Spaeth, Christopher Allan Webber
#
# PyBlosxom (and this jinja2 plugin) distributed under the MIT
# license.  See the file LICENSE for distribution details.
#######################################################################


try:
    from distribute import setup, find_packages
    print "Using distribute...."
except ImportError:
    from setuptools import setup, find_packages
    print "Using setuptools...."

setup(
    name="jinjablosxom",
    author="Christopher Allan Webber",
    license="MIT")
