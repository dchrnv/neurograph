"""
neurograph — Python Library

High-performance semantic knowledge graph system built on neurograph-core (Rust FFI).

Version: 0.1.0
License: AGPL-3.0-or-later (dual licensing available)
"""

__version__ = "0.1.0"
__author__ = "NeuroGraph Team"
__license__ = "AGPL-3.0-or-later"

# Public API exports
from neurograph.exceptions import (
    BootstrapError,
    ConfigError,
    NeurographError,
    QueryError,
    RuntimeError,
)
from neurograph.query import QueryContext, QueryResult
from neurograph.runtime import Config, Runtime
from neurograph.runtime_storage import (
    RuntimeCDNAStorage,
    RuntimeConnectionStorage,
    RuntimeGridStorage,
    RuntimeTokenStorage,
)
from neurograph.types import EmbeddingFormat, FeedbackType

__all__ = [
    # Core
    "Runtime",
    "Config",
    # Query
    "QueryResult",
    "QueryContext",
    # Exceptions
    "NeurographError",
    "RuntimeError",
    "QueryError",
    "BootstrapError",
    "ConfigError",
    # Types
    "FeedbackType",
    "EmbeddingFormat",
    # Runtime Storage
    "RuntimeTokenStorage",
    "RuntimeConnectionStorage",
    "RuntimeGridStorage",
    "RuntimeCDNAStorage",
]
