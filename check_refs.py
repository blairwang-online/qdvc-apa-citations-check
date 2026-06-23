"""
check_refs.py

Audits a research paper (plain text) for APA citation consistency:
  1. Inline citations with no matching reference-list entry
  2. Reference-list entries with no matching inline citation
  3. Inline citations that don't follow the configured comma style

Parsing, analysis, and reporting logic live in the qdvcrc_* modules
alongside this file (qdvcrc_parsing.py, qdvcrc_analysis.py, qdvcrc_report.py).
"""

from qdvcrc_parsing import read_document, parse_document
from qdvcrc_analysis import (
    find_missing_and_used_references,
    find_unused_references,
    find_style_violations,
)
from qdvcrc_report import print_report

# --- Configuration ----------------------------------------------------------

# Controls the expected in-text citation style:
#   True  -> comma style:    (Smith, 2026)
#   False -> no-comma style: (Smith 2026)
USES_COMMA_INTEXT = False

# Raw inline citation strings in this set are ignored entirely
# (e.g. for non-citation bracketed content you don't want flagged).
whitelist = {}


# --- Orchestration -----------------------------------------------------------

def check_citations(file_path):
    """
    Runs the full APA citation audit on the given file and prints a report.
    Returns nothing.

    Example:
        Input:  "paper.txt" (a file containing body text with (Author, Year)
                 citations and a References section)
        Output (printed): the three-section APA CITATION AUDIT REPORT
    """
    lines = read_document(file_path)
    if lines is None:
        return

    raw_reference_list, references_by_key, raw_inline_citations, citations_by_key = (
        parse_document(lines, whitelist)
    )

    missing_in_references, used_reference_entries = find_missing_and_used_references(
        raw_inline_citations, references_by_key
    )
    unused_references = find_unused_references(raw_reference_list, used_reference_entries)
    style_violations = find_style_violations(raw_inline_citations, USES_COMMA_INTEXT)

    print_report(missing_in_references, unused_references, style_violations, USES_COMMA_INTEXT)


# Example usage (replace 'check_refs_document.txt' with your file)
check_citations('check_refs_document.txt')
