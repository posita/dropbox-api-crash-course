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

try:
    from unittest import mock  # pylint: disable=no-name-in-module,unused-import,useless-suppression
except ImportError:
    import mock  # noqa: F401; pylint: disable=import-error,unused-import,useless-suppression
