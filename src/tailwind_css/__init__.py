from __future__ import annotations

import typing

from .extension import TailwindCSS

if typing.TYPE_CHECKING:
    from biscuit.api import ExtensionsAPI


def setup(api: ExtensionsAPI) -> None:
    """Entrypoint for Biscuit to load the extension."""
    ext = TailwindCSS(api)
    api.register("tailwind_css", ext)
    ext.install()
