from abc import ABC
from swesmith.bug_gen.procedural.base import ProceduralModifier


class RustProceduralModifier(ProceduralModifier, ABC):
    """Base class for Go-specific procedural modifications."""
