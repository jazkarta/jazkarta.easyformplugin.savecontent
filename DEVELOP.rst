Using the development buildout
==============================

Create a virtualenv in the package::

    $ virtualenv --clear .

Install zc.buildout with pip::

    $ ./bin/pip install zc.buildout

Run buildout::

    $ ./bin/buildout

Start Plone in foreground:

    $ ./bin/instance fg


Running tests
-------------

    $ ./bin/test
