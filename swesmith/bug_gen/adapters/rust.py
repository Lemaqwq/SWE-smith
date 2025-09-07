import re
import tree_sitter_rust as tsrs
import warnings

from swesmith.constants import TODO_REWRITE, CodeEntity
from tree_sitter import Language, Parser, Query, QueryCursor
from .utils import build_entity

RUST_LANGUAGE = Language(tsrs.language())


class RustEntity(CodeEntity):
    @property
    def name(self) -> str:
        func_query = Query(RUST_LANGUAGE, "(function_item name: (identifier) @name)")
        func_name = self._extract_text_from_first_match(func_query, self.node, "name")
        if func_name:
            return func_name
        return ""

    @property
    def signature(self) -> str:
        body_query = Query(RUST_LANGUAGE, "(function_item body: (block) @body)")
        matches = QueryCursor(body_query).matches(self.node)
        if matches:
            body_node = matches[0][1]["body"][0]
            body_start_byte = body_node.start_byte - self.node.start_byte
            signature = self.node.text[:body_start_byte].strip().decode("utf-8")
            signature = re.sub(r"\(\s+", "(", signature).strip()
            signature = re.sub(r",\s+\)", ")", signature).strip()
            signature = re.sub(r"\s+", " ", signature).strip()
            return signature
        return ""

    @property
    def stub(self) -> str:
        return f"{self.signature} {{\n    // {TODO_REWRITE}\n}}"

    @staticmethod
    def _extract_text_from_first_match(query, node, capture_name: str) -> str | None:
        """Extract text from tree-sitter query matches with None fallback."""
        matches = QueryCursor(query).matches(node)
        return matches[0][1][capture_name][0].text.decode("utf-8") if matches else None


def get_entities_from_file_rs(
    entities: list[RustEntity],
    file_path: str,
    max_entities: int = -1,
) -> None:
    """
    Parse a .rs file and return up to max_entities top-level funcs and types.
    If max_entities < 0, collects them all.
    """
    parser = Parser(RUST_LANGUAGE)

    file_content = open(file_path, "r", encoding="utf8").read()
    tree = parser.parse(bytes(file_content, "utf8"))
    root = tree.root_node
    lines = file_content.splitlines()

    def walk(node) -> None:
        # stop if we've hit the limit
        if 0 <= max_entities == len(entities):
            return

        if node.type == "ERROR":
            warnings.warn(f"Error encountered parsing {file_path}")
            return

        if node.type == "function_item":
            if _has_test_attribute(node):
                return

            entities.append(build_entity(node, lines, file_path, RustEntity))
            if 0 <= max_entities == len(entities):
                return

        for child in node.children:
            walk(child)

    walk(root)


def _has_test_attribute(node) -> bool:
    possible_att = node.prev_named_sibling
    while possible_att and possible_att.type == "attribute_item":
        if possible_att.text == b"#[test]":
            return True
        possible_att = possible_att.prev_named_sibling
    return False
