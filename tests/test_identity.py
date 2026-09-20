import json
from pathlib import Path
from typing import Any

from scholar_search.identity import (
    CorpusSnapshotIdentity,
    get_corpus_identity,
    mint_or_accept_corpus_id,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "canonical"


def test_get_corpus_identity_from_various_inputs():
    """Verify get_corpus_identity accepts Path, str, bytes, list[dict], and list[Document]."""
    base_path = FIXTURES_DIR / "identity_base.json"
    
    # Path
    ident_path = get_corpus_identity(base_path)
    assert ident_path.corpus_id.startswith("COR-")
    
    # Str
    raw_str = base_path.read_text("utf-8")
    ident_str = get_corpus_identity(raw_str)
    assert ident_str.corpus_id == ident_path.corpus_id
    
    # Bytes
    raw_bytes = raw_str.encode("utf-8")
    ident_bytes = get_corpus_identity(raw_bytes)
    assert ident_bytes.corpus_id == ident_path.corpus_id
    
    # List of dicts
    raw_list = json.loads(raw_str)
    ident_dict = get_corpus_identity(raw_list)
    assert ident_dict.corpus_id == ident_path.corpus_id


def test_mint_or_accept_corpus_id():
    """Verify minting vs accepting existing COR- ID."""
    base_path = FIXTURES_DIR / "identity_base.json"
    raw_list = json.loads(base_path.read_text("utf-8"))
    
    # Minting
    minted_id = mint_or_accept_corpus_id(raw_list)
    assert minted_id.startswith("COR-")
    assert len(minted_id) == 36  # COR- + 32 chars
    
    # Accepting
    accepted_id = mint_or_accept_corpus_id("COR-12345678901234567890123456789012")
    assert accepted_id == "COR-12345678901234567890123456789012"


def test_identity_formatting_invariance():
    """Verify formatting changes don't alter the corpus ID or fingerprint."""
    base_path = FIXTURES_DIR / "identity_base.json"
    fmt_path = FIXTURES_DIR / "identity_formatting_variant.json"
    
    ident_base = get_corpus_identity(base_path)
    ident_fmt = get_corpus_identity(fmt_path)
    
    assert ident_base.corpus_id == ident_fmt.corpus_id
    assert ident_base.corpus_fingerprint == ident_fmt.corpus_fingerprint


def test_identity_semantic_sensitivity():
    """Verify semantic changes alter the corpus ID and fingerprint."""
    base_path = FIXTURES_DIR / "identity_base.json"
    sem_path = FIXTURES_DIR / "identity_semantic_variant.json"
    
    ident_base = get_corpus_identity(base_path)
    ident_sem = get_corpus_identity(sem_path)
    
    assert ident_base.corpus_id != ident_sem.corpus_id
    assert ident_base.corpus_fingerprint != ident_sem.corpus_fingerprint
