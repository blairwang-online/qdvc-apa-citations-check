"""
check_refs.py

Audits a research paper (plain text) for APA citation consistency:
  1. Inline citations with no matching reference-list entry
  2. Reference-list entries with no matching inline citation
  3. Inline citations that don't follow the configured comma style
  4. Reference-list entries that aren't in alphabetical order
  5. Inline citations using the wrong author separator ("and" vs "&")
  6. Reference-list entries using the wrong author separator ("and" vs "&")
  7. Reference-list entries using the wrong journal volume/issue format

Style settings are read from config.yml (see DEFAULT_CONFIG for the keys and
their defaults). Parsing, analysis, and reporting logic live in the qdvcrc_*
modules alongside this file (qdvcrc_parsing.py, qdvcrc_analysis.py,
qdvcrc_report.py).
"""

import os

import yaml

from qdvcrc_parsing import read_document, parse_document
from qdvcrc_analysis import (
    find_missing_and_used_references,
    find_unused_references,
    find_style_violations,
    find_reference_order_violations,
    find_intext_separator_violations,
    find_reference_separator_violations,
    find_volume_issue_violations,
)
from qdvcrc_report import print_report

# --- Configuration ----------------------------------------------------------

# Default style settings, used for any key missing from (or absent) config.yml.
#   uses_comma_intext           -> True for (Smith, 2026), False for (Smith 2026)
#   intext_author_separator     -> "and" or "&" before the final in-text author
#   reflist_author_separator    -> "and" or "&" before the final reference author
#   reflist_volume_issue_format -> "comma" for "Journal, 16(2)",
#                                  "parenthetical" for "Journal (16:2)"
DEFAULT_CONFIG = {
    'uses_comma_intext': False,
    'intext_author_separator': 'and',
    'reflist_author_separator': '&',
    'reflist_volume_issue_format': 'comma',
}

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yml')

# Raw inline citation strings in this set are ignored entirely
# (e.g. for non-citation bracketed content you don't want flagged).
whitelist = {}


def load_config(config_path=CONFIG_PATH):
    """
    Reads style settings from a YAML config file, falling back to
    DEFAULT_CONFIG for any key that is missing or for a file that can't be
    read. Returns a dict with all keys in DEFAULT_CONFIG present.

    Example:
        Input:  "config.yml" (containing 'uses_comma_intext: true')
        Output: {"uses_comma_intext": True, "intext_author_separator": "and",
                 "reflist_author_separator": "&",
                 "reflist_volume_issue_format": "comma"}
    """
    config = dict(DEFAULT_CONFIG)
    try:
        with open(config_path, 'r', encoding='utf-8') as config_file:
            loaded = yaml.safe_load(config_file) or {}
    except FileNotFoundError:
        print(f"Note: {config_path} not found; using default settings.")
        return config

    if isinstance(loaded, dict):
        for key in DEFAULT_CONFIG:
            if key in loaded and loaded[key] is not None:
                config[key] = loaded[key]
    return config


# --- Orchestration -----------------------------------------------------------

def check_citations(file_path, config=None):
    """
    Runs the full APA citation audit on the given file and prints a report.
    Settings come from the given config dict (or config.yml if not provided).
    Returns nothing.

    Example:
        Input:  "paper.txt" (a file containing body text with (Author, Year)
                 citations and a References section)
        Output (printed): the seven-section APA CITATION AUDIT REPORT
    """
    if config is None:
        config = load_config()

    uses_comma_intext = config['uses_comma_intext']
    intext_author_separator = config['intext_author_separator']
    reflist_author_separator = config['reflist_author_separator']
    reflist_volume_issue_format = config['reflist_volume_issue_format']

    lines = read_document(file_path)
    if lines is None:
        return

    (
        raw_reference_list,
        references_by_key,
        raw_inline_citations,
        citations_by_key,
        narrative_citations,
    ) = parse_document(lines, whitelist)

    missing_in_references, used_reference_entries = find_missing_and_used_references(
        raw_inline_citations, references_by_key
    )
    unused_references = find_unused_references(raw_reference_list, used_reference_entries)
    style_violations = find_style_violations(
        raw_inline_citations, uses_comma_intext, narrative_citations
    )
    order_violations = find_reference_order_violations(raw_reference_list)
    intext_separator_violations = find_intext_separator_violations(
        raw_inline_citations, intext_author_separator
    )
    reference_separator_violations = find_reference_separator_violations(
        raw_reference_list, reflist_author_separator
    )
    volume_issue_violations = find_volume_issue_violations(
        raw_reference_list, reflist_volume_issue_format
    )

    print_report(
        missing_in_references,
        unused_references,
        style_violations,
        order_violations,
        uses_comma_intext,
        intext_separator_violations,
        reference_separator_violations,
        intext_author_separator,
        reflist_author_separator,
        volume_issue_violations,
        reflist_volume_issue_format,
    )


# Example usage (replace 'check_refs_document.txt' with your file)
check_citations('check_refs_document.txt')
