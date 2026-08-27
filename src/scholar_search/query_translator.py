"""
Query translation framework for scholar-search-kit.

This module provides utilities for translating generic Query objects
into provider-specific query formats, including Boolean query parsing,
field mapping, and syntax adaptation.
"""

import logging
import re
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from .models import Query

logger = logging.getLogger(__name__)


class BooleanOperator(str, Enum):
    """Boolean operators for query composition."""

    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class QueryField(str, Enum):
    """Standard query fields."""

    TITLE = "title"
    ABSTRACT = "abstract"
    FULL_TEXT = "full_text"
    AUTHOR = "author"
    YEAR = "year"
    VENUE = "venue"
    DOI = "doi"
    KEYWORD = "keyword"
    ANY = "any"  # Search all fields


class QueryToken:
    """Represents a token in a parsed query."""

    def __init__(
        self,
        value: str,
        field: QueryField | None = None,
        is_phrase: bool = False,
        is_operator: bool = False,
    ):
        self.value = value
        self.field = field or QueryField.ANY
        self.is_phrase = is_phrase
        self.is_operator = is_operator

    def __repr__(self) -> str:
        return (
            f"QueryToken({self.value!r}, field={self.field}, phrase={self.is_phrase})"
        )


class QueryParser:
    """Parser for Boolean query syntax."""

    FIELD_PATTERN = re.compile(r"(\w+):")
    PHRASE_PATTERN = re.compile(r'"([^"]*)"')
    OPERATOR_PATTERN = re.compile(r"\b(AND|OR|NOT)\b", re.IGNORECASE)
    PAREN_PATTERN = re.compile(r"[()]")

    def parse(self, query_text: str) -> list[QueryToken]:
        tokens = []
        remaining = query_text
        current_field = None

        while remaining.strip():
            remaining = remaining.strip()

            if remaining[0] in "()":
                paren = remaining[0]
                tokens.append(QueryToken(paren, is_operator=True))
                remaining = remaining[1:]
                continue

            field_match = self.FIELD_PATTERN.match(remaining)
            if field_match:
                field_name = field_match.group(1).lower()
                try:
                    current_field = QueryField(field_name)
                except ValueError:
                    logger.warning(f"Unknown field: {field_name}, using 'any'")
                    current_field = QueryField.ANY
                remaining = remaining[field_match.end() :]
                continue

            phrase_match = self.PHRASE_PATTERN.match(remaining)
            if phrase_match:
                phrase = phrase_match.group(1)
                tokens.append(QueryToken(phrase, field=current_field, is_phrase=True))
                remaining = remaining[phrase_match.end() :]
                current_field = None
                continue

            operator_match = self.OPERATOR_PATTERN.match(remaining)
            if operator_match:
                operator = operator_match.group(1).upper()
                tokens.append(QueryToken(operator, is_operator=True))
                remaining = remaining[operator_match.end() :]
                continue

            word_match = re.match(r"([^\s()]+)", remaining)
            if word_match:
                word = word_match.group(1)
                tokens.append(QueryToken(word, field=current_field, is_phrase=False))
                remaining = remaining[word_match.end() :]
                current_field = None
                continue

            break
        return tokens

    def validate(self, tokens: list[QueryToken]) -> bool:
        if not tokens:
            return False

        paren_count = 0
        for token in tokens:
            if token.value == "(":
                paren_count += 1
            elif token.value == ")":
                paren_count -= 1
            if paren_count < 0:
                return False

        if paren_count != 0:
            logger.warning("Unbalanced parentheses in query")
            return False
        return True


class BaseQueryTranslator(ABC):
    """Abstract base class for provider-specific query translators."""

    def __init__(self) -> None:
        self.parser = QueryParser()

    @abstractmethod
    def translate(self, query: Query) -> Any:
        pass

    def escape_special_chars(self, text: str, special_chars: str = "") -> str:
        if not special_chars:
            return text
        escaped = text
        for char in special_chars:
            escaped = escaped.replace(char, f"\\{char}")
        return escaped


class BooleanQueryTranslator(BaseQueryTranslator):
    """Advanced query translator with Boolean operator support."""

    def __init__(
        self,
        field_map: dict[QueryField, str],
        operator_map: dict[str, str] | None = None,
        special_chars: str = "",
    ):
        super().__init__()
        self.field_map = field_map
        self.operator_map = operator_map or {
            "AND": "AND",
            "OR": "OR",
            "NOT": "NOT",
        }
        self.special_chars = special_chars

    def translate(self, query: Query) -> str:
        tokens = self.parser.parse(query.text)
        if not self.parser.validate(tokens):
            return query.text

        query_parts = []
        for token in tokens:
            if token.is_operator:
                if token.value in self.operator_map:
                    query_parts.append(self.operator_map[token.value])
                else:
                    query_parts.append(token.value)
            else:
                field = self.field_map.get(
                    token.field, self.field_map.get(QueryField.ANY, "")
                )
                term = self.escape_special_chars(token.value, self.special_chars)

                # Format: "field:term" or just "term" if no field
                prefix = f"{field}:" if field else ""

                if token.is_phrase:
                    query_parts.append(f'{prefix}"{term}"')
                else:
                    query_parts.append(f"{prefix}{term}")

        return " ".join(query_parts)
