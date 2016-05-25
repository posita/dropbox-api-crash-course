#!/usr/bin/env python
# -*- encoding: utf-8; grammar-ext: py; mode: python -*-

# ========================================================================
"""
  Copyright |(c)| 2017 `Dropbox, Inc.`_

  .. |(c)| unicode:: u+a9
  .. _`Dropbox, Inc.`: https://www.dropbox.com/

  Please see the accompanying ``LICENSE`` and ``CREDITS`` file(s) for
  rights and restrictions governing use of this software. All rights not
  expressly waived or licensed are reserved. If such a file did not
  accompany this software, then please contact the author before viewing
  or using this software in any capacity.
"""
# ========================================================================

from __future__ import (
    absolute_import, division, print_function, unicode_literals,
)
from builtins import *  # noqa: F401,F403; pylint: disable=redefined-builtin,unused-wildcard-import,useless-suppression,wildcard-import
from future.builtins.disabled import *  # noqa: F401,F403; pylint: disable=redefined-builtin,unused-wildcard-import,useless-suppression,wildcard-import

# ---- Imports -----------------------------------------------------------

import logging
import unittest

import tests  # noqa: F401; pylint: disable=unused-import
# from tests.symmetries import mock

# ---- Constants ---------------------------------------------------------

__all__ = ()

_LOGGER = logging.getLogger(__name__)

# ---- Classes -----------------------------------------------------------

# ========================================================================
class AppTestCase(unittest.TestCase):

    longMessage = True

    # ---- Public hooks --------------------------------------------------

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_app(self):
        pass  # TODO: someday...

# ---- Initialization ----------------------------------------------------

if __name__ == '__main__':
    from unittest import main
    main()
