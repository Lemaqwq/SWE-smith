import re
import tree_sitter_rust as tsrs
import warnings

from swesmith.constants import TODO_REWRITE, CodeEntity, CodeProperty
from tree_sitter import Language, Parser, Query, QueryCursor

RUST_LANGUAGE = Language(tsrs.language())


class RustEntity(CodeEntity):
    def _analyze_properties(self):
        """Analyze Rust code properties."""
        node = self.node

        # Core entity types
        if node.type == "function_item":
            self._tags.add(CodeProperty.IS_FUNCTION)
        elif node.type in ["struct_item", "enum_item"]:
            self._tags.add(CodeProperty.IS_STRUCT)
        # Note: trait_item and impl_item are handled separately since they're more like interfaces/implementations

        # Control flow and operations analysis
        self._walk_for_properties(node)

    def _walk_for_properties(self, n):
        """Walk the AST and analyze properties."""
        self._check_control_flow(n)
        self._check_operations(n)
        self._check_expressions(n)

        # Check for attributes on the function itself
        self._check_function_attributes()

        for child in n.children:
            self._walk_for_properties(child)

    def _check_control_flow(self, n):
        """Check for control flow patterns."""
        # Loop constructs
        if n.type in ["for_expression", "while_expression", "loop_expression"]:
            self._tags.add(CodeProperty.HAS_LOOP)

        # Conditional constructs
        if n.type == "if_expression":
            self._tags.add(CodeProperty.HAS_IF)
            # Check if this if expression has an else clause
            for child in n.children:
                if child.type == "else_clause":
                    self._tags.add(CodeProperty.HAS_IF_ELSE)
                    break

        # Match expressions (similar to switch)
        if n.type == "match_expression":
            self._tags.add(CodeProperty.HAS_SWITCH)

        # Exception handling (Result/Option patterns and try blocks)
        if n.type in ["try_expression", "question_mark_expression"]:
            self._tags.add(CodeProperty.HAS_EXCEPTION)

    def _check_operations(self, n):
        """Check for various operations."""
        # Array/vector indexing
        if n.type == "index_expression":
            self._tags.add(CodeProperty.HAS_LIST_INDEXING)

        # Function calls
        if n.type == "call_expression":
            self._tags.add(CodeProperty.HAS_FUNCTION_CALL)

        # Return statements
        if n.type == "return_expression":
            self._tags.add(CodeProperty.HAS_RETURN)

        # Import statements (use declarations)
        if n.type in ["use_declaration", "extern_crate_declaration"]:
            self._tags.add(CodeProperty.HAS_IMPORT)

        # Assignment operations
        if n.type in [
            "assignment_expression",
            "let_declaration",
            "const_item",
            "static_item",
        ]:
            self._tags.add(CodeProperty.HAS_ASSIGNMENT)

        # Closures (Rust's lambda equivalent)
        if n.type == "closure_expression":
            self._tags.add(CodeProperty.HAS_LAMBDA)

        # Decorators (attributes in Rust)
        if n.type == "attribute_item":
            self._tags.add(CodeProperty.HAS_DECORATOR)

        # Wrapper constructs (unsafe blocks, etc.)
        if n.type in ["unsafe_block"]:
            self._tags.add(CodeProperty.HAS_WRAPPER)

        # Iterator patterns (similar to list comprehension)
        if n.type == "field_expression":
            # Check if this is a method call on an iterator
            for child in n.children:
                if child.type == "field_identifier" and hasattr(child, "text"):
                    field_text = (
                        child.text.decode("utf-8")
                        if isinstance(child.text, bytes)
                        else str(child.text)
                    )
                    if field_text in [
                        "map",
                        "filter",
                        "collect",
                        "fold",
                        "reduce",
                        "iter",
                        "into_iter",
                    ]:
                        self._tags.add(CodeProperty.HAS_LIST_COMPREHENSION)
                        break

        # Check for inheritance/trait implementations
        if n.type == "impl_item":
            # Check if this is implementing a trait (has_parent equivalent)
            for child in n.children:
                if child.type == "for" or (
                    hasattr(child, "text") and b"for" in child.text
                ):
                    self._tags.add(CodeProperty.HAS_PARENT)
                    break

    def _check_expressions(self, n):
        """Check expression patterns."""
        # Binary operations
        if n.type == "binary_expression":
            self._tags.add(CodeProperty.HAS_BINARY_OP)
            self._tags.add(CodeProperty.HAS_ARITHMETIC)

            # Check for boolean and comparison operators in children
            for child in n.children:
                if hasattr(child, "text"):
                    text = (
                        child.text.decode("utf-8")
                        if isinstance(child.text, bytes)
                        else str(child.text)
                    )
                    if text in ["&&", "||"]:
                        self._tags.add(CodeProperty.HAS_BOOL_OP)
                    # Check for comparison operators (off by one potential)
                    elif text in ["<", ">", "<=", ">="]:
                        self._tags.add(CodeProperty.HAS_OFF_BY_ONE)

        # Unary operations
        if n.type == "unary_expression":
            self._tags.add(CodeProperty.HAS_UNARY_OP)

    def _check_function_attributes(self):
        """Check for attributes (decorators) on the function."""
        # Look for attributes before the function
        possible_att = self.node.prev_named_sibling
        while possible_att and possible_att.type == "attribute_item":
            self._tags.add(CodeProperty.HAS_DECORATOR)
            possible_att = possible_att.prev_named_sibling

    def _check_file_level_imports(self, root_node):
        """Check for import statements at the file level."""

        def walk_for_imports(node):
            if node.type in ["use_declaration", "extern_crate_declaration"]:
                self._tags.add(CodeProperty.HAS_IMPORT)
                return
            for child in node.children:
                walk_for_imports(child)

        walk_for_imports(root_node)

    @property
    def complexity(self) -> int:
        """
        Calculate the complexity of a Rust function.
        Complexity starts at 1 and increases for each decision point.
        """

        def walk(node):
            score = 0
            # Decision points in Rust
            if node.type in [
                "if_expression",
                "match_expression",
                "for_expression",
                "while_expression",
                "loop_expression",
                "match_arm",  # Each match arm adds complexity
                "question_mark_expression",  # ? operator
                "try_expression",
            ]:
                score += 1

            # Boolean operators add complexity
            elif node.type == "binary_expression":
                for child in node.children:
                    if hasattr(child, "text"):
                        text = (
                            child.text.decode("utf-8")
                            if isinstance(child.text, bytes)
                            else str(child.text)
                        )
                        if text in ["&&", "||"]:
                            score += 1

            for child in node.children:
                score += walk(child)

            return score

        return 1 + walk(self.node)

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

            entities.append(_build_entity(node, lines, file_path))
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


def _build_entity(node, lines, file_path: str) -> RustEntity:
    """
    Turns a Tree-sitter node into a RustEntity object.
    """
    # start_point/end_point are (row, col) zero-based
    start_row, _ = node.start_point
    end_row, _ = node.end_point

    # slice out the raw lines
    snippet = lines[start_row : end_row + 1]

    # detect indent on first line
    first = snippet[0]
    m = re.match(r"^(?P<indent>[\t ]*)", first)
    indent_str = m.group("indent")
    # tabs count as size=1, else use count of spaces, fallback to 4
    indent_size = 1 if "\t" in indent_str else (len(indent_str) or 4)
    indent_level = len(indent_str) // indent_size

    # dedent each line
    dedented = []
    for line in snippet:
        if len(line) >= indent_level * indent_size:
            dedented.append(line[indent_level * indent_size :])
        else:
            dedented.append(line.lstrip("\t "))

    entity = RustEntity(
        file_path=file_path,
        indent_level=indent_level,
        indent_size=indent_size,
        line_start=start_row + 1,
        line_end=end_row + 1,
        node=node,
        src_code="\n".join(dedented),
    )

    # Check for imports at the file level
    root = node
    while root.parent:
        root = root.parent
    entity._check_file_level_imports(root)

    return entity
