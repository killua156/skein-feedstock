"""Move skein off `distutils.version` and onto `packaging.version`.

`distutils` was removed from the standard library in Python 3.12, but skein
0.8.2 still does `from distutils.version import LooseVersion` in
`skein/utils.py`, so `import skein` fails outright on 3.12+.  The sole use is a
grpcio < 1.18 fork-support workaround.

Upstream tracks this as jcrist/skein#256 ("Transition away from distutils to
packaging.version") and proposes exactly this change, so we make it here rather
than invent our own.

This recipe installs the published wheel (the sdist ships neither the generated
protobuf stubs nor the prebuilt skein.jar), so there is no source tree for
`source.patches` to apply to -- the installed module is edited instead.  Both
substitutions are asserted so a future version bump fails loudly here rather
than silently shipping an unpatched package.
"""

import os
import sys

REPLACEMENTS = [
    (
        "from distutils.version import LooseVersion",
        "from packaging.version import Version as LooseVersion",
    ),
    (
        "if LooseVersion(GRPC_VERSION) < '1.18.0':",
        "if LooseVersion(GRPC_VERSION) < LooseVersion('1.18.0'):",
    ),
]

path = os.path.join(os.environ["SP_DIR"], "skein", "utils.py")

with open(path, encoding="utf-8") as f:
    source = f.read()

for old, new in REPLACEMENTS:
    if old not in source:
        sys.exit(
            "patch_distutils.py: expected to find the following in %s but did "
            "not, so skein may have changed upstream:\n  %s" % (path, old)
        )
    source = source.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(source)

print("patch_distutils.py: rewrote %s to use packaging.version" % path)
