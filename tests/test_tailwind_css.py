from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tailwind_css import setup
from src.tailwind_css.extension import TailwindCSS


class TestTailwindCSSExtension:
    def test_extension_setup_and_registration(self, mock_api) -> None:
        setup(mock_api)
        assert "tailwind_css" in mock_api.registered_extensions
        ext = mock_api.registered_extensions["tailwind_css"]
        assert isinstance(ext, TailwindCSS)

        commands = mock_api.commands.commands
        assert "tailwind.check_conflicts" in commands
        assert "tailwind.sort_classes" in commands
        assert "tailwind.highlight_colors" in commands

        assert len(mock_api.statusbar.buttons) == 1
        assert "Tailwind CSS" in mock_api.statusbar.buttons[0].text
        assert mock_api.statusbar.buttons[0].visible is True

    def test_manifest_metadata_and_dependencies(self) -> None:
        import toml
        manifest_path = Path(__file__).parent.parent / "extension.toml"
        assert manifest_path.exists()
        manifest = toml.load(manifest_path)

        assert manifest["extension"]["author"] == "tomlin7"
        assert manifest["extension"]["version"] == "0.2.0"
        assert manifest["dependencies"]["tools"] == ["node"]
        cmd_ids = [cmd["id"] for cmd in manifest["contributes"]["commands"]]
        assert "tailwind.check_conflicts" in cmd_ids
        assert "tailwind.sort_classes" in cmd_ids

    def test_hex_color_matcher(self, mock_api) -> None:
        ext = TailwindCSS(mock_api)
        assert ext.get_color_for_class("bg-blue-500") == "#3b82f6"
        assert ext.get_color_for_class("text-emerald-400") == "#34d399"
        assert ext.get_color_for_class("border-red-600") == "#dc2626"
        assert ext.get_color_for_class("bg-black") == "#000000"
        assert ext.get_color_for_class("text-white") == "#ffffff"
        assert ext.resolve_class_color("bg-purple-700") == "#7e22ce"
        # Non-color utility returns None
        assert ext.get_color_for_class("flex") is None
        assert ext.get_color_for_class("p-4") is None

    def test_extract_classes(self, mock_api) -> None:
        ext = TailwindCSS(mock_api)
        markup = '<div class="flex items-center p-4 text-sm" id="main"><span className="p-4 font-bold">Text</span></div>'
        classes = ext.extract_classes(markup)
        assert classes == ["flex", "items-center", "p-4", "text-sm", "font-bold"]

    def test_conflict_detection(self, mock_api) -> None:
        ext = TailwindCSS(mock_api)

        # Display conflict
        conflicts_display = ext.detect_conflicts(["flex", "hidden", "items-center"])
        assert len(conflicts_display) == 1
        assert "display" in conflicts_display[0]

        # Padding conflict (p-2 vs p-4)
        conflicts_padding = ext.detect_conflicts(["p-2", "p-4", "text-sm"])
        assert len(conflicts_padding) == 1
        assert "p spacing" in conflicts_padding[0]

        # Font size conflict (text-sm vs text-xl)
        conflicts_font = ext.detect_conflicts(["text-sm", "text-xl"])
        assert len(conflicts_font) == 1
        assert "font size" in conflicts_font[0]

        # Multiple background colors
        conflicts_bg = ext.detect_conflicts(["bg-blue-500", "bg-red-500"])
        assert len(conflicts_bg) == 1
        assert "background color" in conflicts_bg[0]

        # Clean classes without conflict
        clean = ext.detect_conflicts(["flex", "items-center", "p-4", "text-sm", "bg-white"])
        assert len(clean) == 0

    def test_suggest_classes_autocompletion(self, mock_api) -> None:
        ext = TailwindCSS(mock_api)
        flex_matches = ext.suggest_classes("flex")
        assert "flex" in flex_matches
        assert "flex-col" in flex_matches
        assert "flex-row" in flex_matches

        pad_matches = ext.get_classes_for_prefix("p-")
        assert "p-2" in pad_matches
        assert "p-4" in pad_matches
        assert "p-8" in pad_matches

        bg_matches = ext.suggest_classes("bg-blue-")
        assert "bg-blue-500" in bg_matches

    def test_sort_classes(self, mock_api) -> None:
        ext = TailwindCSS(mock_api)
        unsorted = ["p-4", "bg-blue-500", "flex", "text-lg", "rounded-md", "items-center"]
        sorted_cls = ext.sort_classes(unsorted)
        # Layout/flex first, then spacing, text, bg, border
        assert sorted_cls.index("flex") < sorted_cls.index("items-center")
        assert sorted_cls.index("items-center") < sorted_cls.index("p-4")
        assert sorted_cls.index("p-4") < sorted_cls.index("text-lg")
        assert sorted_cls.index("text-lg") < sorted_cls.index("bg-blue-500")
        assert sorted_cls.index("bg-blue-500") < sorted_cls.index("rounded-md")

    def test_check_conflicts_command_with_editor(self, mock_api) -> None:
        ext = TailwindCSS(mock_api)
        mock_text = MagicMock()
        mock_text.get.return_value = '<div class="p-2 p-4 flex hidden"></div>'
        mock_api.editors.active_editor = MagicMock(text=mock_text)

        warnings = ext.check_conflicts()
        assert len(warnings) == 2
        mock_api.notifications.warning.assert_called_once()

    def test_check_conflicts_no_editor(self, mock_api) -> None:
        ext = TailwindCSS(mock_api)
        mock_api.editors.active_editor = None
        warnings = ext.check_conflicts()
        assert warnings == []
        mock_api.notifications.warning.assert_called_once()

    def test_sort_classes_in_document(self, mock_api) -> None:
        ext = TailwindCSS(mock_api)
        mock_text = MagicMock()
        mock_text.get.return_value = '<div class="bg-blue-500 flex p-4"></div>'
        mock_api.editors.active_editor = MagicMock(text=mock_text)

        res = ext.sort_classes_in_document()
        assert res is True
        mock_text.delete.assert_called_once_with("1.0", "end")
        mock_text.insert.assert_called_once()
        inserted_code = mock_text.insert.call_args[0][1]
        assert 'class="flex p-4 bg-blue-500"' in inserted_code

    def test_highlight_color_utilities(self, mock_api) -> None:
        ext = TailwindCSS(mock_api)
        mock_text = MagicMock()
        mock_text.get.return_value = '<div class="bg-blue-500 text-white"></div>'
        mock_api.editors.active_editor = MagicMock(text=mock_text)

        count = ext.highlight_color_utilities()
        assert count == 2
        mock_text.tag_config.assert_called()
        mock_text.tag_add.assert_called()

    def test_app_instance_compatibility(self, app_instance) -> None:
        ext = TailwindCSS(app_instance.api)
        assert ext.get_color_for_class("bg-blue-500") == "#3b82f6"
