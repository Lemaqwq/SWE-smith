import pytest
from swesmith.bug_gen.adapters.typescript import get_entities_from_file_ts


@pytest.fixture
def entities(test_file_ts):
    entities = []
    get_entities_from_file_ts(entities, str(test_file_ts))
    return entities


def test_get_entities_from_file_ts_count(entities):
    """Test that we find all entities in buffer.ts."""
    assert len(entities) == 30


def test_get_entities_from_file_ts_max(test_file_ts):
    """Test that max_entities parameter limits the number of results."""
    entities = []
    get_entities_from_file_ts(entities, str(test_file_ts), 3)
    assert len(entities) == 3


def test_get_entities_from_file_ts_names(entities):
    """Test that key method names are present (no class entity expected)."""
    names = [e.name for e in entities]
    assert "constructor" in names
    assert "append" in names
    assert "get" in names
    assert "_allocQueue" in names
    assert "queue" in names


def test_get_entities_from_file_ts_line_ranges(entities):
    """Test that at least one method has a plausible line range."""
    # At least one method should be small
    method = next(e for e in entities if e.name == "constructor")
    assert method.line_end - method.line_start < 20


def test_get_entities_from_file_ts_extensions(entities):
    """Test that all entities have the correct file extension."""
    assert all(e.ext == "ts" for e in entities)


def test_get_entities_from_file_ts_file_paths(entities, test_file_ts):
    """Test that all entities have the correct file path."""
    assert all(e.file_path == str(test_file_ts) for e in entities)


def test_get_entities_from_file_ts_signatures(entities):
    """Test that signatures are non-empty and plausible for key entities."""
    method = next(e for e in entities if e.name == "constructor")
    assert method.signature.startswith("constructor(")
    for e in entities:
        assert e.signature.strip(), f"Entity {e.name} should have a non-empty signature"


def test_get_entities_from_file_ts_stubs(entities):
    """Test that all entities have a non-empty stub."""
    for e in entities:
        assert e.stub.strip(), f"Entity {e.name} should have a non-empty stub"
        assert "TODO" in e.stub


def test_get_entities_from_file_ts_complexity(entities):
    """Test that complexity is always >= 1 for all methods."""
    assert [e.complexity for e in entities] == [
        2,
        2,
        2,
        2,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        5,
        2,
        2,
        8,
        12,
        1,
        3,
        3,
        1,
        5,
        5,
        2,
        4,
        2,
        2,
        2,
        3,
        3,
    ]


def test_get_entities_from_file_ts_exact(entities):
    """Test that the extracted entities match the expected list exactly."""
    expected = [
        (
            "constructor",
            "constructor(map: SourceMap | null, indentChar: string)",
            36,
            45,
        ),
        ("_allocQueue", "_allocQueue()", 70, 84),
        (
            "_pushQueue",
            "_pushQueue(\n  char: number,\n  repeat: number,\n  line: number | undefined,\n  column: number | undefined,\n  filename: string | undefined,\n)",
            86,
            105,
        ),
        ("_popQueue", "_popQueue(): QueueItem", 107, 112),
        ("get", "get()", 118, 155),
        ("__mergedMap", "get __mergedMap()", 131, 133),
        ("map", "get map()", 135, 139),
        ("map", "set map(value)", 140, 142),
        ("rawMappings", "get rawMappings()", 144, 148),
        ("rawMappings", "set rawMappings(value)", 149, 151),
        ("append", "append(str: string, maybeNewline: boolean): void", 161, 165),
        ("appendChar", "appendChar(char: number): void", 167, 170),
        ("queue", "queue(char: number): void", 175, 196),
        ("queueIndentation", "queueIndentation(repeat: number): void", 201, 204),
        ("_flush", "_flush(): void", 206, 214),
        (
            "_appendChar",
            "_appendChar(\n  char: number,\n  repeat: number,\n  sourcePos: InternalSourcePos,\n): void",
            216,
            256,
        ),
        (
            "_append",
            "_append(\n  str: string,\n  sourcePos: InternalSourcePos,\n  maybeNewline: boolean,\n): void",
            258,
            322,
        ),
        (
            "_mark",
            "_mark(\n  line: number | undefined,\n  column: number | undefined,\n  identifierName: string | undefined,\n  identifierNamePos: Pos | undefined,\n  filename: string | undefined,\n): void",
            324,
            339,
        ),
        ("removeTrailingNewline", "removeTrailingNewline(): void", 341, 349),
        ("removeLastSemicolon", "removeLastSemicolon(): void", 351, 359),
        ("getLastChar", "getLastChar(): number", 361, 364),
        ("getNewlineCount", "getNewlineCount(): number", 370, 383),
        ("endsWithCharAndNewline", "endsWithCharAndNewline(): number", 388, 403),
        ("hasContent", "hasContent(): boolean", 405, 407),
        ("exactSource", "exactSource(loc: Loc | undefined, cb: () => void)", 432, 454),
        (
            "source",
            'source(prop: "start" | "end", loc: Loc | undefined): void',
            461,
            467,
        ),
        (
            "sourceWithOffset",
            'sourceWithOffset(\n  prop: "start" | "end",\n  loc: Loc | undefined,\n  columnOffset: number,\n): void',
            469,
            477,
        ),
        (
            "_normalizePosition",
            '_normalizePosition(prop: "start" | "end", loc: Loc, columnOffset: number)',
            479,
            489,
        ),
        ("getCurrentColumn", "getCurrentColumn(): number", 491, 506),
        ("getCurrentLine", "getCurrentLine(): number", 508, 519),
    ]
    actual = [(e.name, e.signature, e.line_start, e.line_end) for e in entities]
    assert actual == expected
