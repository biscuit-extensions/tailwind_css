from __future__ import annotations

import typing

from biscuit.extensions import Extension

if typing.TYPE_CHECKING:
    from biscuit.api import ExtensionsAPI


class TailwindCSS(Extension):
    """Intelligent Tailwind CSS class autocompletion, hover previews, and linting"""

    def __init__(self, api: ExtensionsAPI) -> None:
        super().__init__(api)
        self.api = api
        self.api.logger.info("Tailwind CSS IntelliSense extension initialised.")

    def get_classes_for_prefix(self, prefix: str) -> list[str]:
        """Return autocomplete suggestions for a given utility prefix."""
        known = [
            "flex", "flex-col", "flex-row", "items-center", "justify-between", "justify-center",
            "p-2", "p-4", "p-6", "m-2", "m-4", "text-sm", "text-base", "text-lg", "text-xl",
            "font-bold", "font-semibold", "bg-white", "bg-gray-100", "bg-blue-500", "bg-red-500",
            "rounded", "rounded-lg", "shadow", "shadow-md", "w-full", "h-full", "hidden", "block"
        ]
        return [c for c in known if c.startswith(prefix)]

    def get_color_for_class(self, class_name: str) -> str | None:
        palette = {
            "bg-blue-500": "#3b82f6",
            "bg-red-500": "#ef4444",
            "bg-green-500": "#22c55e",
            "bg-white": "#ffffff",
            "bg-black": "#000000",
            "text-white": "#ffffff",
            "text-black": "#000000"
        }
        return palette.get(class_name)

    def extract_classes(self, html: str) -> list[str]:
        import re
        matches = re.findall(r'(?:class|className)=["\']([^"\']+)["\']', html)
        result = []
        for match in matches:
            result.extend(match.split())
        return list(dict.fromkeys(result))

    def lint_conflicts(self, classes: list[str]) -> list[str]:
        warnings = []
        has_flex = "flex" in classes
        has_hidden = "hidden" in classes
        if has_flex and has_hidden:
            warnings.append("Conflicting display utilities: 'flex' and 'hidden'")
        return warnings

    def install(self) -> None:
        self.api.logger.info("Tailwind CSS IntelliSense extension installed.")
