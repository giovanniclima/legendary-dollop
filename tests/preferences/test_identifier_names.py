"""Focused tests for the plain identifier-name readability check."""

from __future__ import annotations

import ast

from preferences.preferences import (
    CHECKS,
    abbreviated_name,
    compressed_identifier_words,
    identifier_words,
)


def name_complaints(source: str) -> list[str]:
    """Run only the identifier readability check over parsed source."""
    complaints: list[str] = []
    for node in ast.walk(ast.parse(source)):
        message = abbreviated_name(node)
        if message:
            complaints.append(message)
    return complaints


def test_identifier_words_split_snake_case_camel_case_and_acronyms() -> None:
    """Tokenization keeps acronym metadata so CamelCase technical names can be exempted."""
    assert identifier_words("_parseHTTPResponse_v2") == [
        ("parse", False),
        ("http", True),
        ("response", False),
        ("v", False),
        ("2", False),
    ]


def test_compressed_identifier_words_prefers_clear_signals() -> None:
    """Vowel-stripped words and stacked short consonant tokens are flagged."""
    assert compressed_identifier_words("chk_fp_sz") == ["chk"]
    assert compressed_identifier_words("fp_sz") == ["fp", "sz"]
    assert compressed_identifier_words("check_file_size") == []


def test_compressed_identifier_words_avoids_common_false_positives() -> None:
    """Technical initialisms, acronym chunks, digits, y-vowel words, and one short token stay allowed."""
    assert compressed_identifier_words("parse_http_response") == []
    assert compressed_identifier_words("HSMClient") == []
    assert compressed_identifier_words("sha256_digest") == []
    assert compressed_identifier_words("sync_cache") == []
    assert compressed_identifier_words("fp_value") == []


def test_abbreviated_name_checks_functions_async_functions_and_classes() -> None:
    """All requested declaration kinds report actionable messages."""
    assert name_complaints("def chk_fp_sz():\n    pass\n") == [
        "'chk_fp_sz': spell out compressed identifier token(s): chk"
    ]
    assert name_complaints("async def parse_cfg():\n    pass\n") == [
        "'parse_cfg': spell out compressed identifier token(s): cfg"
    ]
    assert name_complaints("class ChkResult:\n    pass\n") == [
        "'ChkResult': spell out compressed identifier token(s): chk"
    ]


def test_abbreviated_name_ignores_other_nodes_and_readable_names() -> None:
    """Assignments and readable declaration names are outside the narrow heuristic."""
    assignment = ast.parse("cfg = 1\n").body[0]
    assert abbreviated_name(assignment) is None
    assert name_complaints("def check_file_size():\n    pass\n") == []
    assert name_complaints("class XMLParser:\n    pass\n") == []
    assert name_complaints("def load_mcp_config():\n    pass\n") == []


def test_abbreviated_name_is_registered() -> None:
    """The existing registry drives the check during a normal preferences walk."""
    assert CHECKS["abbreviated_name"] is abbreviated_name
