"""
qdvcrc_analysis.py

Functions that analyze the data parsed by qdvcrc_parsing.py: cross-matching
inline citations against the reference list, finding unused references, and
checking in-text style consistency. Imported by check_refs.py.
"""

from qdvcrc_parsing import YEAR_PATTERN


def matches_intext_style(cite_text, uses_comma_intext):
    """
    Checks whether a cleaned inline citation string (e.g. "Smith, 2026" or
    "Smith et al 2026") follows the given comma style. Citations with no
    detectable year are treated as not applicable (True).

    Example:
        Input:  "Jones 2024", True
        Output: False
    """
    year_match = YEAR_PATTERN.search(cite_text)
    if not year_match:
        return True

    text_before_year = cite_text[:year_match.start()].rstrip()
    has_comma_before_year = text_before_year.endswith(',')

    return has_comma_before_year == uses_comma_intext


def find_missing_and_used_references(raw_inline_citations, references_by_key):
    """
    Cross-references inline citations against the reference list.
    Returns:
      - missing_in_references: raw inline citation text with no matching
        reference-list entry
      - used_reference_entries: reference-list lines that were matched by
        at least one inline citation

    Example:
        Input:
            raw_inline_citations = {
                "Smith, 2026": [("Smith", "2026")],
                "Nguyen, 2025": [("Nguyen", "2025")],
            }
            references_by_key = {
                ("Smith", "2026"): ["Smith, J. (2026). A study of things."]
            }
        Output:
            (
                {"Nguyen, 2025"},
                {"Smith, J. (2026). A study of things."},
            )
    """
    missing_in_references = set()
    used_reference_entries = set()

    for raw_cite, keys in raw_inline_citations.items():
        if not keys:  # Bracket text wasn't a recognizable citation
            continue

        matched = False
        for key in keys:
            if key in references_by_key:
                matched = True
                used_reference_entries.update(references_by_key[key])

        if not matched:
            missing_in_references.add(raw_cite)

    return missing_in_references, used_reference_entries


def find_unused_references(raw_reference_list, used_reference_entries):
    """
    Returns reference-list lines that no inline citation matched.

    Example:
        Input:
            raw_reference_list = [
                "Smith, J. (2026). A study of things.",
                "Patel, R. (2021). Unused reference.",
            ]
            used_reference_entries = {"Smith, J. (2026). A study of things."}
        Output:
            ["Patel, R. (2021). Unused reference."]
    """
    return [ref for ref in raw_reference_list if ref not in used_reference_entries]


def find_style_violations(raw_inline_citations, uses_comma_intext):
    """
    Returns a sorted list of inline citations that don't conform to the
    given comma style.

    Example:
        Input:
            raw_inline_citations = {
                "Smith, 2026": [("Smith", "2026")],
                "Jones 2024": [("Jones", "2024")],
            }, True
        Output:
            ["Jones 2024"]
    """
    violations = [
        raw_cite
        for raw_cite, keys in raw_inline_citations.items()
        if keys and not matches_intext_style(raw_cite, uses_comma_intext)
    ]
    return sorted(violations)
