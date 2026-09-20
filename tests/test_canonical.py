import json
from pathlib import Path

from scholar_search.canonical import canonical_fingerprint, canonical_json
from scholar_search.importers import JSONImporter

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "canonical"

def test_canonical_json_formatting_invariance():
    """Verify that formatting differences do not change canonical output."""
    base_path = FIXTURES_DIR / "identity_base.json"
    fmt_path = FIXTURES_DIR / "identity_formatting_variant.json"
    
    # Load as raw dicts
    base_docs = json.loads(base_path.read_text("utf-8"))
    fmt_docs = json.loads(fmt_path.read_text("utf-8"))
    
    base_canon = canonical_json(base_docs)
    fmt_canon = canonical_json(fmt_docs)
    
    assert base_canon == fmt_canon, "Canonical bytes differ for formatting variant"

def test_canonical_fingerprint_matches_sha256_file():
    """Verify fingerprint matches pre-calculated .sha256 file."""
    base_path = FIXTURES_DIR / "identity_base.json"
    sha_path = FIXTURES_DIR / "identity_base.json.sha256"
    
    base_docs = json.loads(base_path.read_text("utf-8"))
    fp = canonical_fingerprint(base_docs)
    expected_fp = sha_path.read_text("utf-8").strip()
    
    assert fp == expected_fp, f"Expected {expected_fp}, got {fp}"

def test_canonical_semantic_sensitivity():
    """Verify that semantic differences result in different fingerprints."""
    base_path = FIXTURES_DIR / "identity_base.json"
    sem_path = FIXTURES_DIR / "identity_semantic_variant.json"
    
    base_docs = json.loads(base_path.read_text("utf-8"))
    sem_docs = json.loads(sem_path.read_text("utf-8"))
    
    fp_base = canonical_fingerprint(base_docs)
    fp_sem = canonical_fingerprint(sem_docs)
    
    assert fp_base != fp_sem, "Fingerprints should differ for semantic variants"
