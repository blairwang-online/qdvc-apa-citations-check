"""
qdvcrc_analysis.py

Functions that analyze the data parsed by qdvcrc_parsing.py: cross-matching
inline citations against the reference list, finding unused references, and
checking in-text style consistency. Imported by check_refs.py.
"""

import re
import unicodedata

from qdvcrc_parsing import YEAR_PATTERN, get_reference_author_prefix

# Detects the two author-separator forms used between names in a citation or
# reference entry. The word "and" is matched only as a whole word, so it does
# not fire inside surnames like "Anderson" or "Brand".
AND_SEPARATOR_PATTERN = re.compile(r'(?<![\w&])and(?![\w])', re.IGNORECASE)
AMPERSAND_SEPARATOR_PATTERN = re.compile(r'&')

# Maps a configured separator value to the pattern that detects the *other*
# (disallowed) separator, so a violation is flagged only when the wrong token
# is actually present (comma-separated or single-author entries are left
# alone).
_WRONG_SEPARATOR_PATTERN = {
    'and': AMPERSAND_SEPARATOR_PATTERN,
    '&': AND_SEPARATOR_PATTERN,
}

# Latin letters that have no canonical Unicode decomposition into a base
# letter plus a combining mark, so NFKD normalization alone can't reduce them
# to ASCII. They are mapped to their conventional base form(s) explicitly so
# that alphabetical-order checking treats e.g. "ø" like "o" and "ß" like "ss".
_FOLD_SPECIAL_CHARS = str.maketrans({
    'ø': 'o', 'Ø': 'o',
    'ł': 'l', 'Ł': 'l',
    'ð': 'd', 'Ð': 'd', 'đ': 'd', 'Đ': 'd',
    'ß': 'ss',
    'þ': 'th', 'Þ': 'th',
    'æ': 'ae', 'Æ': 'ae',
    'œ': 'oe', 'Œ': 'oe',
    'ı': 'i',
    'ħ': 'h', 'Ħ': 'h',
})


def fold_to_ascii(text):
    """
    Reduces a string to a lowercase ASCII form for alphabetical comparison,
    folding accented and other non-ASCII Latin letters to their base letters
    (e.g. "Öqvist" -> "oqvist", "Bjørnsson" -> "bjornsson"). Characters with
    no ASCII equivalent are dropped.

    Example:
        Input:  "Öqvist"
        Output: "oqvist"
    """
    text = text.translate(_FOLD_SPECIAL_CHARS)
    decomposed = unicodedata.normalize('NFKD', text)
    ascii_text = decomposed.encode('ascii', 'ignore').decode('ascii')
    return ascii_text.lower()


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


def find_style_violations(raw_inline_citations, uses_comma_intext,
                          narrative_citations=None):
    """
    Returns a sorted list of inline citations that don't conform to the
    given comma style. Narrative (in-prose) citations such as
    "Liesenfeld and Dingemanse 2024" are excluded, because the comma-style
    convention only applies to fully parenthetical citations; a narrative
    citation never has a comma before its parenthesized year regardless of
    the configured style.

    Example:
        Input:
            raw_inline_citations = {
                "Smith, 2026": [("Smith", "2026")],
                "Jones 2024": [("Jones", "2024")],
            }, True
        Output:
            ["Jones 2024"]
    """
    narrative_citations = narrative_citations or set()
    violations = [
        raw_cite
        for raw_cite, keys in raw_inline_citations.items()
        if keys
        and raw_cite not in narrative_citations
        and not matches_intext_style(raw_cite, uses_comma_intext)
    ]
    return sorted(violations)


def get_reference_sort_key(line):
    """
    Returns the ASCII-folded, lowercased author-name portion of a
    reference-list line, used to check alphabetical ordering. APA reference
    entries start with the first author's surname before the first comma.
    Accented and other non-ASCII Latin letters are folded to their base
    letters (e.g. "Öqvist" -> "oqvist") so they sort as expected.

    Example:
        Input:  "Smith, J. (2026). A study of things."
        Output: "smith"
    """
    author_part = line.split(',')[0].strip()
    return fold_to_ascii(author_part)


def find_reference_order_violations(raw_reference_list):
    """
    Returns the reference-list lines that are out of alphabetical order
    relative to the entry immediately before them, based on each entry's
    leading author surname (the text before the first comma).

    Example:
        Input:
            raw_reference_list = [
                "Smith, J. (2026). A study of things.",
                "Jones, A. (2024). Another study.",
            ]
        Output:
            ["Jones, A. (2024). Another study."]
    """
    violations = []
    for i in range(1, len(raw_reference_list)):
        previous_key = get_reference_sort_key(raw_reference_list[i - 1])
        current_key = get_reference_sort_key(raw_reference_list[i])
        if current_key < previous_key:
            violations.append(raw_reference_list[i])

    return violations


def find_intext_separator_violations(raw_inline_citations, intext_separator):
    """
    Returns a sorted list of inline citations that join authors with the
    wrong separator, given the configured in-text separator ("and" or "&").
    A citation is flagged only when it actually contains the disallowed
    token; single-author and comma-only citations (which contain neither
    "and" nor "&") are never flagged.

    Example:
        Input:
            raw_inline_citations = {
                "Smith & Jones 2020": [("Smith","2020"), ("Jones","2020")],
                "Brown and Lee 2019": [("Brown","2019"), ("Lee","2019")],
            }, "and"
        Output:
            ["Smith & Jones 2020"]
    """
    wrong_pattern = _WRONG_SEPARATOR_PATTERN.get(intext_separator)
    if wrong_pattern is None:
        return []

    violations = [
        raw_cite
        for raw_cite, keys in raw_inline_citations.items()
        if keys and wrong_pattern.search(raw_cite)
    ]
    return sorted(violations)


def find_reference_separator_violations(raw_reference_list, reflist_separator):
    """
    Returns the reference-list lines that join authors with the wrong
    separator, given the configured reference-list separator ("and" or "&").
    A line is flagged only when it actually contains the disallowed token;
    single-author and comma-only entries are never flagged.

    Example:
        Input:
            raw_reference_list = [
                "Smith A & Jones B (2020) Work one. Pub, City",
                "Brown C and Lee D (2019) Work two. Pub, City",
            ], "&"
        Output:
            ["Brown C and Lee D (2019) Work two. Pub, City"]
    """
    wrong_pattern = _WRONG_SEPARATOR_PATTERN.get(reflist_separator)
    if wrong_pattern is None:
        return []

    return [
        ref for ref in raw_reference_list
        if wrong_pattern.search(get_reference_author_prefix(ref))
    ]
