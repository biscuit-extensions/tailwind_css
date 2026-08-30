from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tailwind_css import setup
from src.tailwind_css.extension import TailwindCSS


class TestTailwindCSSExtension:
    def test_extension_setup(self, app_instance) -> None:
        setup(app_instance.api)
        ext = TailwindCSS(app_instance.api)
        completions = ext.get_classes_for_prefix("flex")
        assert "flex" in completions
        assert "flex-col" in completions
        assert ext.get_color_for_class("bg-blue-500") == "#3b82f6"
        extracted = ext.extract_classes('<div class="flex items-center p-4"></div>')
        assert extracted == ["flex", "items-center", "p-4"]
        warnings = ext.lint_conflicts(["flex", "hidden"])
        assert len(warnings) == 1
