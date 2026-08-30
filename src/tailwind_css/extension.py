from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

from biscuit.extensions import Extension

if TYPE_CHECKING:
    from biscuit.api import ExtensionsAPI


# Standard Tailwind CSS color palette
TAILWIND_COLORS: dict[str, dict[str, str]] = {
    "slate": {
        "50": "#f8fafc", "100": "#f1f5f9", "200": "#e2e8f0", "300": "#cbd5e1",
        "400": "#94a3b8", "500": "#64748b", "600": "#475569", "700": "#334155",
        "800": "#1e293b", "900": "#0f172a", "950": "#020617",
    },
    "gray": {
        "50": "#f9fafb", "100": "#f3f4f6", "200": "#e5e7eb", "300": "#d1d5db",
        "400": "#9ca3af", "500": "#6b7280", "600": "#4b5563", "700": "#374151",
        "800": "#1f2937", "900": "#111827", "950": "#030712",
    },
    "zinc": {
        "50": "#fafafa", "100": "#f4f4f5", "200": "#e4e4e7", "300": "#d4d4d8",
        "400": "#a1a1aa", "500": "#71717a", "600": "#52525b", "700": "#3f3f46",
        "800": "#27272a", "900": "#18181b", "950": "#09090b",
    },
    "red": {
        "50": "#fef2f2", "100": "#fee2e2", "200": "#fecaca", "300": "#fca5a5",
        "400": "#f87171", "500": "#ef4444", "600": "#dc2626", "700": "#b91c1c",
        "800": "#991b1b", "900": "#7f1d1d", "950": "#450a0a",
    },
    "orange": {
        "50": "#fff7ed", "100": "#ffedd5", "200": "#fed7aa", "300": "#fdba74",
        "400": "#fb923c", "500": "#f97316", "600": "#ea580c", "700": "#c2410c",
        "800": "#9a3412", "900": "#7c2d12", "950": "#431407",
    },
    "amber": {
        "50": "#fffbeb", "100": "#fef3c7", "200": "#fde68a", "300": "#fcd34d",
        "400": "#fbbf24", "500": "#f59e0b", "600": "#d97706", "700": "#b45309",
        "800": "#92400e", "900": "#78350f", "950": "#451a03",
    },
    "yellow": {
        "50": "#fefce8", "100": "#fef9c3", "200": "#fef08a", "300": "#fde047",
        "400": "#facc15", "500": "#eab308", "600": "#ca8a04", "700": "#a16207",
        "800": "#854d0e", "900": "#713f12", "950": "#422006",
    },
    "green": {
        "50": "#f0fdf4", "100": "#dcfce7", "200": "#bbf7d0", "300": "#86efac",
        "400": "#4ade80", "500": "#22c55e", "600": "#16a34a", "700": "#15803d",
        "800": "#166534", "900": "#14532d", "950": "#052e16",
    },
    "emerald": {
        "50": "#ecfdf5", "100": "#d1fae5", "200": "#a7f3d0", "300": "#6ee7b7",
        "400": "#34d399", "500": "#10b981", "600": "#059669", "700": "#047857",
        "800": "#065f46", "900": "#064e3b", "950": "#022c22",
    },
    "teal": {
        "50": "#f0fdfa", "100": "#ccfbf1", "200": "#99f6e4", "300": "#5eead4",
        "400": "#2dd4bf", "500": "#14b8a6", "600": "#0d9488", "700": "#0f766e",
        "800": "#115e59", "900": "#134e4a", "950": "#042f2e",
    },
    "cyan": {
        "50": "#ecfeff", "100": "#cffafe", "200": "#a5f3fc", "300": "#67e8f9",
        "400": "#22d3ee", "500": "#06b6d4", "600": "#0891b2", "700": "#0e7490",
        "800": "#155e75", "900": "#164e63", "950": "#083344",
    },
    "sky": {
        "50": "#f0f9ff", "100": "#e0f2fe", "200": "#bae6fd", "300": "#7dd3fc",
        "400": "#38bdf8", "500": "#0ea5e9", "600": "#0284c7", "700": "#0369a1",
        "800": "#075985", "900": "#0c4a6e", "950": "#082f49",
    },
    "blue": {
        "50": "#eff6ff", "100": "#dbeafe", "200": "#bfdbfe", "300": "#93c5fd",
        "400": "#60a5fa", "500": "#3b82f6", "600": "#2563eb", "700": "#1d4ed8",
        "800": "#1e40af", "900": "#1e3a8a", "950": "#172554",
    },
    "indigo": {
        "50": "#eef2ff", "100": "#e0e7ff", "200": "#c7d2fe", "300": "#a5b4fc",
        "400": "#818cf8", "500": "#6366f1", "600": "#4f46e5", "700": "#4338ca",
        "800": "#3730a3", "900": "#312e81", "950": "#1e1b4b",
    },
    "violet": {
        "50": "#f5f3ff", "100": "#ede9fe", "200": "#ddd6fe", "300": "#c4b5fd",
        "400": "#a78bfa", "500": "#8b5cf6", "600": "#7c3aed", "700": "#6d28d9",
        "800": "#5b21b6", "900": "#4c1d95", "950": "#2e1065",
    },
    "purple": {
        "50": "#faf5ff", "100": "#f3e8ff", "200": "#e9d5ff", "300": "#d8b4fe",
        "400": "#c084fc", "500": "#a855f7", "600": "#9333ea", "700": "#7e22ce",
        "800": "#6b21a8", "900": "#581c87", "950": "#3b0764",
    },
    "fuchsia": {
        "50": "#fdf4ff", "100": "#fae8ff", "200": "#f5d0fe", "300": "#f0abfc",
        "400": "#e879f9", "500": "#d946ef", "600": "#c026d3", "700": "#a21caf",
        "800": "#86198f", "900": "#701a75", "950": "#4a044e",
    },
    "pink": {
        "50": "#fdf2f8", "100": "#fce7f3", "200": "#fbcfe8", "300": "#f9a8d4",
        "400": "#f472b6", "500": "#ec4899", "600": "#db2777", "700": "#be185d",
        "800": "#9d174d", "900": "#831843", "950": "#500724",
    },
    "rose": {
        "50": "#fff1f2", "100": "#ffe4e6", "200": "#fecdd3", "300": "#fda4af",
        "400": "#fb7185", "500": "#f43f5e", "600": "#e11d48", "700": "#be123c",
        "800": "#9f1239", "900": "#881337", "950": "#4c0519",
    },
}

SPECIAL_COLORS: dict[str, str] = {
    "black": "#000000",
    "white": "#ffffff",
    "transparent": "transparent",
    "current": "currentColor",
}

COLOR_PREFIXES = (
    "bg-", "text-", "border-", "ring-", "ring-offset-",
    "outline-", "divide-", "accent-", "fill-", "stroke-",
)

BASE_UTILITY_CLASSES = [
    # Layout
    "container", "block", "inline-block", "inline", "flex", "inline-flex",
    "table", "inline-table", "grid", "inline-grid", "contents", "list-item", "hidden",
    # Positioning
    "static", "fixed", "absolute", "relative", "sticky",
    "top-0", "top-auto", "top-full", "right-0", "bottom-0", "left-0", "inset-0", "inset-x-0", "inset-y-0",
    # Flexbox & Grid
    "flex-row", "flex-row-reverse", "flex-col", "flex-col-reverse",
    "flex-wrap", "flex-wrap-reverse", "flex-nowrap",
    "items-start", "items-end", "items-center", "items-baseline", "items-stretch",
    "justify-start", "justify-end", "justify-center", "justify-between", "justify-around", "justify-evenly",
    "grid-cols-1", "grid-cols-2", "grid-cols-3", "grid-cols-4", "grid-cols-6", "grid-cols-12",
    "gap-1", "gap-2", "gap-3", "gap-4", "gap-6", "gap-8",
    # Spacing
    "p-0", "p-1", "p-2", "p-3", "p-4", "p-5", "p-6", "p-8", "p-10", "p-12",
    "px-0", "px-1", "px-2", "px-3", "px-4", "px-6", "px-8",
    "py-0", "py-1", "py-2", "py-3", "py-4", "py-6", "py-8",
    "pt-0", "pt-1", "pt-2", "pt-4", "pb-0", "pb-1", "pb-2", "pb-4",
    "pl-0", "pl-1", "pl-2", "pl-4", "pr-0", "pr-1", "pr-2", "pr-4",
    "m-0", "m-1", "m-2", "m-3", "m-4", "m-6", "m-8", "m-auto",
    "mx-0", "mx-1", "mx-2", "mx-4", "mx-auto", "my-0", "my-1", "my-2", "my-4", "my-auto",
    # Sizing
    "w-0", "w-1", "w-2", "w-4", "w-6", "w-8", "w-12", "w-16", "w-24", "w-32", "w-48", "w-64",
    "w-auto", "w-1/2", "w-1/3", "w-2/3", "w-1/4", "w-3/4", "w-full", "w-screen", "w-min", "w-max", "w-fit",
    "h-0", "h-1", "h-2", "h-4", "h-6", "h-8", "h-12", "h-16", "h-24", "h-32", "h-48", "h-64",
    "h-auto", "h-full", "h-screen", "h-min", "h-max", "h-fit",
    # Typography
    "font-sans", "font-serif", "font-mono",
    "text-xs", "text-sm", "text-base", "text-lg", "text-xl", "text-2xl", "text-3xl", "text-4xl", "text-5xl",
    "font-thin", "font-extralight", "font-light", "font-normal", "font-medium", "font-semibold", "font-bold", "font-extrabold", "font-black",
    "text-left", "text-center", "text-right", "text-justify",
    "underline", "line-through", "no-underline", "uppercase", "lowercase", "capitalize", "truncate",
    # Borders & Effects
    "rounded-none", "rounded-sm", "rounded", "rounded-md", "rounded-lg", "rounded-xl", "rounded-2xl", "rounded-full",
    "border", "border-0", "border-2", "border-4", "border-8",
    "shadow-sm", "shadow", "shadow-md", "shadow-lg", "shadow-xl", "shadow-2xl", "shadow-none",
    "opacity-0", "opacity-25", "opacity-50", "opacity-75", "opacity-100",
    "cursor-pointer", "cursor-default", "cursor-not-allowed",
    "transition", "transition-all", "duration-150", "duration-300", "ease-in-out",
]


class TailwindCSS(Extension):
    """Tailwind CSS utility class intelligence, autocompletion provider, and hex color highlighter."""

    def __init__(self, api: ExtensionsAPI) -> None:
        super().__init__(api)
        self.api = api
        self.status_button = None
        self._all_classes_cache: list[str] | None = None

        self.install()
        self.api.logger.info("Tailwind CSS IntelliSense extension initialised.")

    def install(self) -> None:
        """Register commands and UI controls."""
        if hasattr(self.api, "commands") and self.api.commands:
            self.api.commands.register_command("tailwind.check_conflicts", self.check_conflicts)
            self.api.commands.register_command("tailwind.sort_classes", self.sort_classes_in_document)
            self.api.commands.register_command("tailwind.highlight_colors", self.highlight_color_utilities)

        if hasattr(self.api, "statusbar") and self.api.statusbar:
            if not self.status_button:
                self.status_button = self.api.statusbar.add_button(
                    text="Tailwind CSS",
                    icon="wind",
                    callback=self.check_conflicts,
                    description="Tailwind CSS IntelliSense",
                )
                if hasattr(self.status_button, "show"):
                    self.status_button.show()

        self.api.logger.info("Tailwind CSS IntelliSense extension installed.")

    def get_color_for_class(self, class_name: str) -> str | None:
        """Resolve a Tailwind utility class to its corresponding hex color code."""
        # Exact match specials
        for pfx in COLOR_PREFIXES:
            if class_name.startswith(pfx):
                color_part = class_name[len(pfx):]
                if color_part in SPECIAL_COLORS:
                    return SPECIAL_COLORS[color_part]
                if "-" in color_part:
                    name, shade = color_part.rsplit("-", 1)
                    if name in TAILWIND_COLORS and shade in TAILWIND_COLORS[name]:
                        return TAILWIND_COLORS[name][shade]

        return None

    def resolve_class_color(self, class_name: str) -> str | None:
        return self.get_color_for_class(class_name)

    def _get_all_classes(self) -> list[str]:
        """Generate and cache the full list of Tailwind CSS classes."""
        if self._all_classes_cache is not None:
            return self._all_classes_cache

        classes = list(BASE_UTILITY_CLASSES)
        for pfx in ("bg-", "text-", "border-", "ring-"):
            for spec_name in SPECIAL_COLORS:
                classes.append(f"{pfx}{spec_name}")
            for color_name, shades in TAILWIND_COLORS.items():
                for shade in shades:
                    classes.append(f"{pfx}{color_name}-{shade}")

        self._all_classes_cache = sorted(set(classes))
        return self._all_classes_cache

    def suggest_classes(self, prefix: str, limit: int = 50) -> list[str]:
        """Return autocomplete suggestions for a given utility class prefix."""
        all_cls = self._get_all_classes()
        if not prefix:
            return all_cls[:limit]

        matches = [c for c in all_cls if c.startswith(prefix)]
        return matches[:limit]

    def get_classes_for_prefix(self, prefix: str) -> list[str]:
        return self.suggest_classes(prefix, limit=100)

    def extract_classes(self, html: str) -> list[str]:
        """Extract all unique utility classes from HTML/JSX markup."""
        pattern = re.compile(r'(?:class|className)\s*=\s*["\']([^"\']+)["\']')
        matches = pattern.findall(html)
        result: list[str] = []
        for match in matches:
            for token in match.split():
                if token not in result:
                    result.append(token)
        return result

    def detect_conflicts(self, classes: list[str]) -> list[str]:
        """Identify conflicting Tailwind CSS utility classes."""
        warnings: list[str] = []

        # 1. Display conflict
        display_utilities = {"flex", "inline-flex", "block", "inline-block", "inline", "hidden", "grid", "inline-grid"}
        found_displays = [c for c in classes if c in display_utilities]
        if len(found_displays) > 1:
            warnings.append(
                f"Conflicting display utilities: {', '.join(repr(c) for c in found_displays)}"
            )

        # 2. Position conflict
        position_utilities = {"static", "fixed", "absolute", "relative", "sticky"}
        found_positions = [c for c in classes if c in position_utilities]
        if len(found_positions) > 1:
            warnings.append(
                f"Conflicting position utilities: {', '.join(repr(c) for c in found_positions)}"
            )

        # 3. Spacing conflicts (padding & margin on same axis)
        axis_patterns = {
            "p": re.compile(r"^p-\d+$"),
            "px": re.compile(r"^px-\d+$"),
            "py": re.compile(r"^py-\d+$"),
            "pt": re.compile(r"^pt-\d+$"),
            "pb": re.compile(r"^pb-\d+$"),
            "pl": re.compile(r"^pl-\d+$"),
            "pr": re.compile(r"^pr-\d+$"),
            "m": re.compile(r"^m-\d+$"),
            "mx": re.compile(r"^mx-\d+$"),
            "my": re.compile(r"^my-\d+$"),
            "mt": re.compile(r"^mt-\d+$"),
            "mb": re.compile(r"^mb-\d+$"),
            "ml": re.compile(r"^ml-\d+$"),
            "mr": re.compile(r"^mr-\d+$"),
        }

        for axis_name, regex in axis_patterns.items():
            matches = [c for c in classes if regex.match(c)]
            if len(matches) > 1:
                warnings.append(
                    f"Conflicting {axis_name} spacing utilities: {', '.join(repr(c) for c in matches)}"
                )

        # 4. Font size conflicts
        font_sizes = {
            "text-xs", "text-sm", "text-base", "text-lg", "text-xl",
            "text-2xl", "text-3xl", "text-4xl", "text-5xl", "text-6xl", "text-7xl", "text-8xl", "text-9xl",
        }
        found_sizes = [c for c in classes if c in font_sizes]
        if len(found_sizes) > 1:
            warnings.append(
                f"Conflicting font size utilities: {', '.join(repr(c) for c in found_sizes)}"
            )

        # 5. Font weight conflicts
        font_weights = {
            "font-thin", "font-extralight", "font-light", "font-normal",
            "font-medium", "font-semibold", "font-bold", "font-extrabold", "font-black",
        }
        found_weights = [c for c in classes if c in font_weights]
        if len(found_weights) > 1:
            warnings.append(
                f"Conflicting font weight utilities: {', '.join(repr(c) for c in found_weights)}"
            )

        # 6. Background color conflicts
        bg_colors = [c for c in classes if c.startswith("bg-") and self.get_color_for_class(c)]
        if len(bg_colors) > 1:
            warnings.append(
                f"Conflicting background color utilities: {', '.join(repr(c) for c in bg_colors)}"
            )

        return warnings

    def lint_conflicts(self, classes: list[str]) -> list[str]:
        return self.detect_conflicts(classes)

    def sort_classes(self, classes: list[str]) -> list[str]:
        """Sort classes according to recommended Tailwind ordering."""
        def category_order(cls: str) -> tuple[int, str]:
            if cls in {"block", "inline-block", "inline", "flex", "grid", "hidden", "static", "fixed", "absolute", "relative", "sticky"}:
                return (0, cls)
            if any(cls.startswith(pfx) for pfx in ("flex-", "grid-", "items-", "justify-", "gap-")):
                return (1, cls)
            if any(cls.startswith(pfx) for pfx in ("p-", "px-", "py-", "pt-", "pb-", "pl-", "pr-", "m-", "mx-", "my-", "mt-", "mb-", "ml-", "mr-")):
                return (2, cls)
            if any(cls.startswith(pfx) for pfx in ("w-", "h-", "min-w-", "max-w-", "min-h-", "max-h-")):
                return (3, cls)
            if any(cls.startswith(pfx) for pfx in ("text-", "font-", "leading-", "tracking-", "underline", "truncate")):
                return (4, cls)
            if cls.startswith("bg-"):
                return (5, cls)
            if any(cls.startswith(pfx) for pfx in ("border-", "rounded-", "ring-")):
                return (6, cls)
            if any(cls.startswith(pfx) for pfx in ("shadow-", "opacity-")):
                return (7, cls)
            if any(cls.startswith(pfx) for pfx in ("transition", "duration-", "ease-", "cursor-")):
                return (8, cls)
            return (9, cls)

        return sorted(classes, key=category_order)

    def _get_active_text_widget(self) -> Any:
        if not hasattr(self.api, "editors") or not self.api.editors:
            return None
        active = getattr(self.api.editors, "active_editor", None)
        if not active:
            return None
        return getattr(active, "text", None) or getattr(getattr(active, "content", None), "text", None)

    def check_conflicts(self) -> list[str]:
        """Biscuit Command: Check active editor document for Tailwind class conflicts."""
        text_widget = self._get_active_text_widget()
        if not text_widget:
            if hasattr(self.api, "notifications") and self.api.notifications:
                self.api.notifications.warning("Tailwind: No active document open.")
            return []

        content = text_widget.get("1.0", "end-1c")
        # Extract per element
        attr_regex = re.compile(r'(?:class|className)\s*=\s*["\']([^"\']+)["\']')
        all_warnings: list[str] = []
        for match in attr_regex.finditer(content):
            cls_list = match.group(1).split()
            conflicts = self.detect_conflicts(cls_list)
            all_warnings.extend(conflicts)

        if hasattr(self.api, "notifications") and self.api.notifications:
            if all_warnings:
                self.api.notifications.warning(f"Tailwind: Found {len(all_warnings)} class conflicts.")
            else:
                self.api.notifications.info("Tailwind: No class conflicts found.")

        return all_warnings

    def sort_classes_in_document(self) -> bool:
        """Biscuit Command: Sort all Tailwind classes in the active document."""
        text_widget = self._get_active_text_widget()
        if not text_widget:
            return False

        content = text_widget.get("1.0", "end-1c")
        attr_regex = re.compile(r'((?:class|className)\s*=\s*["\'])([^"\']+)(["\'])')

        def replacer(match: re.Match) -> str:
            prefix = match.group(1)
            classes = match.group(2).split()
            suffix = match.group(3)
            sorted_cls = self.sort_classes(classes)
            return f"{prefix}{' '.join(sorted_cls)}{suffix}"

        new_content = attr_regex.sub(replacer, content)
        if new_content != content:
            text_widget.delete("1.0", "end")
            text_widget.insert("1.0", new_content)
            if hasattr(self.api, "notifications") and self.api.notifications:
                self.api.notifications.info("Tailwind: Sorted classes in document.")
            return True
        return False

    def highlight_color_utilities(self) -> int:
        """Biscuit Command: Highlight color utility classes in editor with their actual hex colors."""
        text_widget = self._get_active_text_widget()
        if not text_widget:
            return 0

        content = text_widget.get("1.0", "end-1c")
        attr_regex = re.compile(r'(?:class|className)\s*=\s*["\']([^"\']+)["\']')
        highlighted_count = 0

        for match in attr_regex.finditer(content):
            attr_start = match.start(1)
            tokens = match.group(1).split()
            current_offset = attr_start
            for token in tokens:
                hex_color = self.get_color_for_class(token)
                if hex_color and hex_color != "transparent" and hex_color != "currentColor":
                    token_start_idx = content.find(token, current_offset)
                    if token_start_idx != -1:
                        # Convert character offset to line.col in Tkinter format
                        line = content[:token_start_idx].count("\n") + 1
                        last_newline = content[:token_start_idx].rfind("\n")
                        col = token_start_idx if last_newline == -1 else token_start_idx - last_newline - 1
                        end_col = col + len(token)

                        tag_name = f"tw_color_{hex_color.replace('#', '')}"
                        try:
                            if hasattr(text_widget, "tag_config"):
                                text_widget.tag_config(tag_name, background=hex_color)
                            if hasattr(text_widget, "tag_add"):
                                text_widget.tag_add(tag_name, f"{line}.{col}", f"{line}.{end_col}")
                            highlighted_count += 1
                        except Exception:
                            pass
                        current_offset = token_start_idx + len(token)

        return highlighted_count
