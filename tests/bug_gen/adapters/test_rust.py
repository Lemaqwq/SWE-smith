import pytest
import re
import warnings

from swesmith.bug_gen.adapters.rust import (
    get_entities_from_file_rs,
)
from swesmith.constants import CodeProperty


@pytest.fixture
def entities(test_file_rust):
    entities = []
    get_entities_from_file_rs(entities, test_file_rust)
    return entities


def test_get_entities_from_file_rs_count(entities):
    assert len(entities) == 19


def test_get_entities_from_file_rs_max(test_file_rust):
    entities = []
    get_entities_from_file_rs(entities, test_file_rust, 3)
    assert len(entities) == 3


def test_get_entities_from_file_rs_unreadable():
    with pytest.raises(IOError):
        get_entities_from_file_rs([], "non-existent-file")


def test_get_entities_from_file_rs_no_functions(tmp_path):
    no_functions_file = tmp_path / "no_functions.rs"
    no_functions_file.write_text("// there are no functions here")
    entities = []
    get_entities_from_file_rs(entities, no_functions_file)
    assert len(entities) == 0


def test_get_entities_from_file_rs_malformed(tmp_path):
    malformed_file = tmp_path / "malformed.rs"
    malformed_file.write_text("(malformed")
    entities = []
    with warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter("always")
        get_entities_from_file_rs(entities, malformed_file)
        assert any(
            [
                re.search(r"Error encountered parsing .*malformed.rs", str(w.message))
                for w in ws
            ]
        )


def test_get_entities_from_file_rs_test_function_ignored(tmp_path):
    test_function_file = tmp_path / "test_function.rs"
    test_function_file.write_text(
        """
#[test]
#[should_panic]
fn test_true() {
    assert!(true);
}
        """
    )
    entities = []
    get_entities_from_file_rs(entities, test_function_file)
    assert len(entities) == 0


def test_get_entities_from_file_rs_names(entities):
    names = [e.name for e in entities]
    expected_names = [
        "parse",
        "name",
        "value",
        "http_only",
        "secure",
        "same_site_lax",
        "same_site_strict",
        "path",
        "domain",
        "max_age",
        "expires",
        "fmt",
        "extract_response_cookie_headers",
        "extract_response_cookies",
        "fmt",
        "fmt",
        "add_cookie_str",
        "set_cookies",
        "cookies",
    ]
    assert names == expected_names


def test_get_entities_from_file_rs_line_ranges(entities):
    start_end = [(e.line_start, e.line_end) for e in entities]
    expected_ranges = [
        (37, 43),
        (46, 48),
        (51, 53),
        (56, 58),
        (61, 63),
        (66, 68),
        (71, 73),
        (76, 78),
        (81, 83),
        (86, 91),
        (94, 99),
        (103, 105),
        (108, 112),
        (114, 121),
        (127, 129),
        (133, 135),
        (158, 164),
        (168, 173),
        (175, 190),
    ]
    assert start_end == expected_ranges


def test_get_entities_from_file_rs_extensions(entities):
    assert all([e.ext == "rs" for e in entities]), (
        "All entities should have the extension 'rs'"
    )


def test_get_entities_from_file_rs_file_paths(entities, test_file_rust):
    assert all([e.file_path == test_file_rust for e in entities]), (
        "All entities should have the correct file path"
    )


def test_get_entities_from_file_rs_signatures(entities):
    signatures = [e.signature for e in entities]
    expected_signatures = [
        "fn parse(value: &'a HeaderValue) -> Result<Cookie<'a>, CookieParseError>",
        "pub fn name(&self) -> &str",
        "pub fn value(&self) -> &str",
        "pub fn http_only(&self) -> bool",
        "pub fn secure(&self) -> bool",
        "pub fn same_site_lax(&self) -> bool",
        "pub fn same_site_strict(&self) -> bool",
        "pub fn path(&self) -> Option<&str>",
        "pub fn domain(&self) -> Option<&str>",
        "pub fn max_age(&self) -> Option<std::time::Duration>",
        "pub fn expires(&self) -> Option<SystemTime>",
        "fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result",
        "pub(crate) fn extract_response_cookie_headers<'a>(headers: &'a hyper::HeaderMap) -> impl Iterator<Item = &'a HeaderValue> + 'a",
        "pub(crate) fn extract_response_cookies<'a>(headers: &'a hyper::HeaderMap) -> impl Iterator<Item = Result<Cookie<'a>, CookieParseError>> + 'a",
        "fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result",
        "fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result",
        "pub fn add_cookie_str(&self, cookie: &str, url: &url::Url)",
        "fn set_cookies(&self, cookie_headers: &mut dyn Iterator<Item = &HeaderValue>, url: &url::Url)",
        "fn cookies(&self, url: &url::Url) -> Option<HeaderValue>",
    ]
    assert signatures == expected_signatures


def test_get_entities_from_file_rs_stubs(entities):
    stubs = [e.stub for e in entities]
    expected_stubs = [
        "fn parse(value: &'a HeaderValue) -> Result<Cookie<'a>, CookieParseError> {\n    // TODO: Implement this function\n}",
        "pub fn name(&self) -> &str {\n    // TODO: Implement this function\n}",
        "pub fn value(&self) -> &str {\n    // TODO: Implement this function\n}",
        "pub fn http_only(&self) -> bool {\n    // TODO: Implement this function\n}",
        "pub fn secure(&self) -> bool {\n    // TODO: Implement this function\n}",
        "pub fn same_site_lax(&self) -> bool {\n    // TODO: Implement this function\n}",
        "pub fn same_site_strict(&self) -> bool {\n    // TODO: Implement this function\n}",
        "pub fn path(&self) -> Option<&str> {\n    // TODO: Implement this function\n}",
        "pub fn domain(&self) -> Option<&str> {\n    // TODO: Implement this function\n}",
        "pub fn max_age(&self) -> Option<std::time::Duration> {\n    // TODO: Implement this function\n}",
        "pub fn expires(&self) -> Option<SystemTime> {\n    // TODO: Implement this function\n}",
        "fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {\n    // TODO: Implement this function\n}",
        "pub(crate) fn extract_response_cookie_headers<'a>(headers: &'a hyper::HeaderMap) -> impl Iterator<Item = &'a HeaderValue> + 'a {\n    // TODO: Implement this function\n}",
        "pub(crate) fn extract_response_cookies<'a>(headers: &'a hyper::HeaderMap) -> impl Iterator<Item = Result<Cookie<'a>, CookieParseError>> + 'a {\n    // TODO: Implement this function\n}",
        "fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {\n    // TODO: Implement this function\n}",
        "fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {\n    // TODO: Implement this function\n}",
        "pub fn add_cookie_str(&self, cookie: &str, url: &url::Url) {\n    // TODO: Implement this function\n}",
        "fn set_cookies(&self, cookie_headers: &mut dyn Iterator<Item = &HeaderValue>, url: &url::Url) {\n    // TODO: Implement this function\n}",
        "fn cookies(&self, url: &url::Url) -> Option<HeaderValue> {\n    // TODO: Implement this function\n}",
    ]
    assert stubs == expected_stubs


def test_rust_entity_is_function_property(entities):
    """Test that all entities are correctly identified as functions."""
    for entity in entities:
        assert CodeProperty.IS_FUNCTION in entity._tags
        assert entity.is_function is True


def test_rust_entity_struct_detection(tmp_path):
    """Test detection of Rust structs and enums."""
    struct_file = tmp_path / "test_struct.rs"
    struct_file.write_text("""
struct Person {
    name: String,
    age: u32,
}

enum Status {
    Active,
    Inactive,
    Pending,
}

fn process_person(person: Person) -> Status {
    if person.age > 18 {
        Status::Active
    } else {
        Status::Pending
    }
}
""")

    entities = []
    get_entities_from_file_rs(entities, struct_file)

    # Should only get the function, not the struct/enum
    assert len(entities) == 1
    function_entity = entities[0]
    assert function_entity.name == "process_person"
    assert CodeProperty.IS_FUNCTION in function_entity._tags
    assert CodeProperty.IS_STRUCT not in function_entity._tags


def test_rust_entity_control_flow_properties(tmp_path):
    """Test detection of control flow constructs."""
    control_flow_file = tmp_path / "control_flow.rs"
    control_flow_file.write_text("""
fn test_control_flow(x: i32, items: Vec<i32>) -> Result<i32, String> {
    let mut result = 0;
    
    // If statement
    if x > 0 {
        // For loop
        for item in items.iter() {
            result += item;
        }
    } else {
        // While loop
        let mut counter = 0;
        while counter < 10 {
            result += counter;
            counter += 1;
        }
    }
    
    // Match expression
    match result {
        0 => Err("Zero result".to_string()),
        _ => Ok(result),
    }
}
""")

    entities = []
    get_entities_from_file_rs(entities, control_flow_file)

    assert len(entities) == 1
    entity = entities[0]

    # Check control flow properties
    assert CodeProperty.HAS_IF in entity._tags
    assert CodeProperty.HAS_IF_ELSE in entity._tags
    assert CodeProperty.HAS_LOOP in entity._tags
    assert CodeProperty.HAS_SWITCH in entity._tags


def test_rust_entity_operation_properties(tmp_path):
    """Test detection of various operations."""
    operations_file = tmp_path / "operations.rs"
    operations_file.write_text("""
use std::collections::HashMap;

fn test_operations(arr: &[i32]) -> Vec<i32> {
    let mut map: HashMap<i32, i32> = HashMap::new();
    let mut result = Vec::new();
    
    // Assignment
    let x = 5;
    
    // Function call
    println!("Processing array");
    
    // Array indexing
    if arr.len() > 0 {
        result.push(arr[0]);
    }
    
    // Iterator methods (list comprehension equivalent)
    let filtered: Vec<i32> = arr.iter()
        .filter(|&&x| x > 0)
        .map(|&x| x * 2)
        .collect();
    
    // Closure (lambda)
    let transformer = |n: i32| n + 1;
    
    // Return statement
    return filtered;
}
""")

    entities = []
    get_entities_from_file_rs(entities, operations_file)

    assert len(entities) == 1
    entity = entities[0]

    # Check operation properties
    assert CodeProperty.HAS_IMPORT in entity._tags
    assert CodeProperty.HAS_ASSIGNMENT in entity._tags
    assert CodeProperty.HAS_FUNCTION_CALL in entity._tags
    assert CodeProperty.HAS_LIST_INDEXING in entity._tags
    assert CodeProperty.HAS_LIST_COMPREHENSION in entity._tags
    assert CodeProperty.HAS_LAMBDA in entity._tags
    assert CodeProperty.HAS_RETURN in entity._tags


def test_rust_entity_expression_properties(tmp_path):
    """Test detection of expression patterns."""
    expressions_file = tmp_path / "expressions.rs"
    expressions_file.write_text("""
fn test_expressions(x: i32, y: i32, flag: bool) -> bool {
    // Binary operations with comparison (off by one potential)
    let comparison = x > y && y <= 10;
    
    // Boolean operations
    let boolean_result = flag || comparison;
    
    // Unary operations
    let negated = !flag;
    let negative = -x;
    
    // Arithmetic operations
    let sum = x + y * 2;
    
    boolean_result && (sum >= 0)
}
""")

    entities = []
    get_entities_from_file_rs(entities, expressions_file)

    assert len(entities) == 1
    entity = entities[0]

    # Check expression properties
    assert CodeProperty.HAS_BINARY_OP in entity._tags
    assert CodeProperty.HAS_BOOL_OP in entity._tags
    assert CodeProperty.HAS_UNARY_OP in entity._tags
    assert CodeProperty.HAS_ARITHMETIC in entity._tags
    assert CodeProperty.HAS_OFF_BY_ONE in entity._tags


def test_rust_entity_exception_handling(tmp_path):
    """Test detection of exception handling patterns."""
    exception_file = tmp_path / "exception_handling.rs"
    exception_file.write_text("""
fn test_exception_handling(input: &str) -> Result<i32, String> {
    let parsed = input.parse::<i32>()?;
    
    let result = try {
        parsed * 2
    };
    
    Ok(result)
}
""")

    entities = []
    get_entities_from_file_rs(entities, exception_file)

    assert len(entities) == 1
    entity = entities[0]

    # Check exception handling
    assert CodeProperty.HAS_EXCEPTION in entity._tags


def test_rust_entity_wrapper_constructs(tmp_path):
    """Test detection of wrapper constructs."""
    wrapper_file = tmp_path / "wrapper_constructs.rs"
    wrapper_file.write_text("""
fn test_unsafe_operations(ptr: *mut i32) -> i32 {
    unsafe {
        *ptr = 42;
        *ptr
    }
}
""")

    entities = []
    get_entities_from_file_rs(entities, wrapper_file)

    assert len(entities) == 1
    entity = entities[0]

    # Check wrapper constructs
    assert CodeProperty.HAS_WRAPPER in entity._tags


def test_rust_entity_attributes(tmp_path):
    """Test detection of attributes (decorators)."""
    attributes_file = tmp_path / "attributes.rs"
    attributes_file.write_text("""
#[derive(Debug, Clone)]
#[allow(dead_code)]
fn test_with_attributes() -> i32 {
    42
}
""")

    entities = []
    get_entities_from_file_rs(entities, attributes_file)

    assert len(entities) == 1
    entity = entities[0]

    # Check attributes
    assert CodeProperty.HAS_DECORATOR in entity._tags


def test_rust_entity_complexity_calculation(tmp_path):
    """Test complexity calculation for Rust functions."""
    complex_file = tmp_path / "complex_function.rs"
    complex_file.write_text("""
fn complex_function(x: i32, y: i32) -> Result<i32, String> {
    if x > 0 {
        for i in 0..x {
            if i % 2 == 0 {
                match i {
                    0 => continue,
                    2 => break,
                    _ => {},
                }
            }
        }
    } else if x < 0 {
        while y > 0 {
            y -= 1;
        }
    }
    
    Ok(x + y)
}
""")

    entities = []
    get_entities_from_file_rs(entities, complex_file)

    assert len(entities) == 1
    entity = entities[0]

    # Complexity should be greater than 1 due to multiple decision points
    assert entity.complexity > 5  # Should have multiple decision points


@pytest.mark.parametrize(
    "rust_construct,expected_properties",
    [
        ("if x > 0 { 1 } else { 0 }", [CodeProperty.HAS_IF, CodeProperty.HAS_IF_ELSE]),
        ('for i in 0..10 { println!("{}", i); }', [CodeProperty.HAS_LOOP]),
        ("while x > 0 { x -= 1; }", [CodeProperty.HAS_LOOP]),
        ("loop { break; }", [CodeProperty.HAS_LOOP]),
        ("match x { 0 => true, _ => false }", [CodeProperty.HAS_SWITCH]),
        ("let closure = |x| x + 1;", [CodeProperty.HAS_LAMBDA]),
        ("arr[0]", [CodeProperty.HAS_LIST_INDEXING]),
        ("x + y", [CodeProperty.HAS_BINARY_OP, CodeProperty.HAS_ARITHMETIC]),
        ("x && y", [CodeProperty.HAS_BINARY_OP, CodeProperty.HAS_BOOL_OP]),
        ("!flag", [CodeProperty.HAS_UNARY_OP]),
        ("x >= 10", [CodeProperty.HAS_BINARY_OP, CodeProperty.HAS_OFF_BY_ONE]),
    ],
)
def test_rust_entity_specific_constructs(tmp_path, rust_construct, expected_properties):
    """Parametrized test for specific Rust constructs."""
    test_file = tmp_path / "test_construct.rs"
    test_file.write_text(f"""
fn test_function() -> i32 {{
    let arr = [1, 2, 3];
    let x = 5;
    let y = 10;
    let flag = true;
    
    {rust_construct};
    42
}}
""")

    entities = []
    get_entities_from_file_rs(entities, test_file)

    assert len(entities) == 1
    entity = entities[0]

    for prop in expected_properties:
        assert prop in entity._tags, (
            f"Expected property {prop.value} not found for construct: {rust_construct}"
        )
