"""Tests for marketplace.catalog — loading authored artifacts from disk."""

from pathlib import Path

import pytest

from marketplace.catalog import CatalogItem, load_catalog


def _write_item(root: Path, kind_dir: str, item_id: str, metadata: str, body_file: str) -> None:
    item_dir = root / kind_dir / item_id
    item_dir.mkdir(parents=True)
    (item_dir / "metadata.yaml").write_text(metadata, encoding="utf-8")
    (item_dir / body_file).write_text("# Body\n", encoding="utf-8")


class TestLoadCatalog:
    def test_load_catalog_real_repo_returns_items_sorted_by_kind_and_name(self) -> None:
        items = load_catalog()
        assert items, "Expected the repo's own catalog to contain artifacts"
        keys = [(item.kind, item.name.lower()) for item in items]
        assert keys == sorted(keys), f"Catalog not sorted by (kind, name): {keys}"

    def test_load_catalog_full_metadata_populates_all_fields(self, fake_root: Path) -> None:
        _write_item(
            fake_root,
            "rules",
            "my-rule",
            "name: My Rule\ndescription: desc\ntags: [a, b]\nauthor: avi\n"
            'version: 2.1.0\nglobs: ["**/*.py"]\nalwaysApply: true\n',
            "rule.md",
        )
        items = load_catalog()
        assert len(items) == 1, f"Expected exactly one item, got {len(items)}"
        item = items[0]
        assert item.id == "my-rule", f"Wrong id: {item.id}"
        assert item.name == "My Rule", f"Wrong name: {item.name}"
        assert item.kind == "rule", f"Wrong kind: {item.kind}"
        assert item.tags == ["a", "b"], f"Wrong tags: {item.tags}"
        assert item.author == "avi", f"Wrong author: {item.author}"
        assert item.version == "2.1.0", f"Wrong version: {item.version}"
        assert item.globs == ["**/*.py"], f"Wrong globs: {item.globs}"
        assert item.always_apply is True, "alwaysApply should map to always_apply=True"
        assert item.content.startswith("# Body"), f"Wrong content: {item.content!r}"

    def test_load_catalog_missing_body_file_skips_item(self, fake_root: Path) -> None:
        item_dir = fake_root / "skills" / "broken"
        item_dir.mkdir(parents=True)
        (item_dir / "metadata.yaml").write_text("name: Broken\n", encoding="utf-8")
        assert load_catalog() == [], "Item without a body file must be skipped"

    def test_load_catalog_malformed_yaml_skips_item_silently(self, fake_root: Path) -> None:
        _write_item(fake_root, "skills", "bad-yaml", "name: [unclosed\n", "skill.md")
        _write_item(fake_root, "skills", "good", "name: Good\nversion: 1.0.0\n", "skill.md")
        items = load_catalog()
        assert [item.id for item in items] == ["good"], "Malformed item must be skipped silently"

    def test_load_catalog_empty_root_returns_empty_list(self, fake_root: Path) -> None:
        assert load_catalog() == [], "Empty marketplace root must yield an empty catalog"

    def test_load_catalog_minimal_metadata_applies_defaults(self, fake_root: Path) -> None:
        _write_item(fake_root, "plugins", "min", "name: Min\n", "plugin.md")
        item = load_catalog()[0]
        assert item.version == "1.0.0", f"Default version wrong: {item.version}"
        assert item.author == "unknown", f"Default author wrong: {item.author}"
        assert item.globs == [], f"Default globs wrong: {item.globs}"
        assert item.always_apply is False, "Default always_apply must be False"


class TestCatalogItemLabel:
    @pytest.mark.parametrize(
        ("kind", "icon"),
        [("skill", "🧠"), ("plugin", "🔌"), ("rule", "📏")],
    )
    def test_label_per_kind_uses_matching_icon(self, kind: str, icon: str) -> None:
        item = CatalogItem(id="x", name="X", description="", kind=kind)  # type: ignore[arg-type]
        assert item.label == f"{icon} X", f"Wrong label for {kind}: {item.label}"
