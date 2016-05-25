<!--- -*- encoding: utf-8; grammar-ext: md; mode: markdown -*-
  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
  >>>>>>>>>>>>>>>> IMPORTANT: READ THIS BEFORE EDITING! <<<<<<<<<<<<<<<<
  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
  Please keep each sentence on its own unwrapped line.
  It looks like crap in a text editor, but it has no effect on rendering, and it allows much more useful diffs.
  Thank you! -->

Copyright © 2017 [Dropbox, Inc.](https://www.dropbox.com/)

Please see the accompanying [`LICENSE`](../LICENSE) and [`CREDITS`](../CREDITS) file(s) for rights and restrictions governing use of this software.
All rights not expressly waived or licensed are reserved.
If such a file did not accompany this software, then please contact the author before viewing or using this software in any capacity.

- [ ] `git checkout -b X.Y.Z-release`

- [ ] Set version in [`dropbox/api/primer/version.py`](dropbox/api/primer/version.py)

```diff
diff --git a/dropbox/api/primer/version.py b/dropbox/api/primer/version.py
index 0123456..fedcba9 100644
--- a/dropbox/api/primer/version.py
+++ b/dropbox/api/primer/version.py
@@ -25,5 +25,5 @@ from __future__ import (

 __all__ = ()

-__version__ = ( 0, 0, 0 )
-__release__ = 'v0.0.0'
+__version__ = ( X, Y, Z )
+__release__ = 'vX.Y.Z'
```

- [ ] Set version in [`README.rst`](README.rst) (`v0.0.0` → `vX.Y.Z`; [`https://pypi.python.org/pypi/dropbox-api-primer`](https://pypi.python.org/pypi/dropbox-api-primer) → [`https://pypi.python.org/pypi/dropbox-api-primer/X.Y.Z`](https://pypi.python.org/pypi/dropbox-api-primer/X.Y.Z);  [`https://img.shields.io/pypi/.../dropbox-api-primer.svg`](https://img.shields.io/pypi/.../dropbox-api-primer.svg) →  [`https://img.shields.io/pypi/.../dropbox-api-primer/X.Y.Z.svg`](https://img.shields.io/pypi/.../dropbox-api-primer/X.Y.Z.svg))

- [ ] `git commit --all --message 'Update version and release vX.Y.Z.'`

- [ ] `git tag --sign --force --message 'Release vX.Y.Z.' vX.Y.Z`

- [ ] `git push --tags`

- [ ] `./setup.py sdist upload`

- [ ] Upload `dropbox-api-primer.egg-info/PKG-INFO` to [`https://pypi.python.org/pypi?:action=submit_form&name=dropbox-api-primer&version=X.Y.Z`](https://pypi.python.org/pypi?:action=submit_form&name=dropbox-api-primer&version=X.Y.Z) (work-around)

- [ ] `git checkout master`

- [ ] `git branch --delete X.Y.Z-release`
