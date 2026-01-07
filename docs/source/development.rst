Setting up development environment
==================================

This document describes how to set up a development environment for building
and testing the documentation and running the test-suite locally.

This project is managed by uv.

A ``Makefile`` is provided for convenience to automate common development tasks.

Create a virtual environment and install the dev dependencies:

.. code-block:: bash

    # Using Makefile
    make install

    # Or directly with uv
    uv sync --group dev

This will both download dependencies to test and build the documentation.
Other possible dependency groups are ``test`` and ``docs``.

Running Tests and Linting
-------------------------

You can run all quality checks (lint, typecheck, and tests) using:

.. code-block:: bash

    make all

Individual checks:

.. code-block:: bash

    make lint       # Run ruff
    make typecheck  # Run mypy
    make test       # Run pytest

Building Documentation
----------------------

To build the HTML docs into "docs/build/html":

.. code-block:: bash

    # Using Makefile
    make docs

    # Or directly with uv
    uv run --group docs make html -C docs


