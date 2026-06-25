"""
qdvcrc_parsing.py

Low-level helpers for reading a document and extracting citation and
reference data from it. Imported by check_refs.py.
"""

import re

# Section header detection (compiled once, reused on every parse)
REFERENCE_START_PATTERN = re.compile(
    r'^#*\s*(?:\d+(?:\.\d+)*\s*\.?\s*)?references', re.IGNORECASE
)
APPENDIX_START_PATTERN = re.compile(
    r'^#*\s*(?:\d+(?:\.\d+)*\s*\.?\s*)?appendix', re.IGNORECASE
)

# Pulls everything inside [] or () from a line of body text
INLINE_BRACKET_PATTERN = r'\[(.*?)\]|\((.*?)\)'

# Matches a reference-list entry's year, allowing trailing month/day info,
# e.g. "(2023, 23 May)" or "(2023)" -> captures "2023"
REFERENCE_YEAR_PATTERN = re.compile(r'\(((?:16|17|18|19|20)\d{2})(?:,?\s*[^)]*)?\)')

# Matches a 4-digit year (optionally suffixed, e.g. "2023a") anywhere in text
YEAR_PATTERN = re.compile(r'\b(16\d{2}|17\d{2}|18\d{2}|19\d{2}|20\d{2})[a-z]?\b')

# Matches an author surname: an uppercase initial letter (ASCII or accented,
# e.g. the "Ä" in "Mähring") followed by one or more further letters, with
# optional hyphenated parts (e.g. "Pries-Heje"). Requiring 2+ letters keeps
# single-letter initials (the "M" in "Mähring M") from being read as surnames.
AUTHOR_NAME_PATTERN = re.compile(
    r'\b[A-ZÀ-ÖØ-Þ][^\W\d_\s\-]+(?:-[^\W\d_\s]+)*'
)

# Matches a parenthesis containing only a year (optionally letter-suffixed),
# e.g. "(2024)" or "(2024a)" -> captures "2024". Used to detect narrative
# citations such as "Liesenfeld and Dingemanse (2024)", where the author
# names sit in the running prose rather than inside the brackets.
NARRATIVE_YEAR_PATTERN = re.compile(
    r'\(((?:16|17|18|19|20)\d{2})[a-z]?\)'
)

# Matches the contiguous run of author tokens immediately preceding a
# narrative year parenthesis: capitalized names (ASCII or accented) joined by
# spaces, commas, "and", "&", "et", or "al." The run is anchored to the end of
# the pre-parenthesis text, so lowercase lead-in words ("according to", "by")
# stop the match and aren't mistaken for authors.
_NARRATIVE_NAME = r'[A-ZÀ-ÖØ-Þ][\w.\'-]*'
_NARRATIVE_CONNECTOR = r'(?:and|&|et|al\.?)'
NARRATIVE_AUTHORS_PATTERN = re.compile(
    r'((?:' + _NARRATIVE_NAME + r'|' + _NARRATIVE_CONNECTOR + r')'
    r'(?:[\s,]+(?:' + _NARRATIVE_NAME + r'|' + _NARRATIVE_CONNECTOR + r'))*)\s*$'
)


def extract_apa_keys_from_inline(cite_text):
    """
    Extracts (Author, Year) keys from a raw inline citation string.
    Handles multiple authors, 'et al.', '&', and 'and'.

    Example:
        Input:  "Smith & Jones, 2026"
        Output: [("Smith", "2026"), ("Jones", "2026")]
    """
    year_match = YEAR_PATTERN.search(cite_text)
    if not year_match:
        return []
    year = year_match.group(1)

    # Remove the year, parentheses, commas to isolate author names
    name_part = YEAR_PATTERN.sub('', cite_text)
    name_part = re.sub(r'[\(\),]', '', name_part).strip()

    # Extract all individual capitalized words (last names), excluding
    # common conjunctions and 'et al'
    authors = AUTHOR_NAME_PATTERN.findall(name_part)
    authors = [a for a in authors if a.lower() not in ['and', 'et', 'al']]

    return [(author, year) for author in authors]


def extract_reference_keys(line):
    """
    Given a stripped reference-list line, returns the (Author, Year) keys
    found in it, based on the year in parentheses and the author names
    preceding it.

    Example:
        Input:  "Smith, J. (2026). A study of things. Journal of Things."
        Output: [("Smith", "2026")]
    """
    ref_year_match = REFERENCE_YEAR_PATTERN.search(line)
    if not ref_year_match:
        return []

    ref_year = ref_year_match.group(1)
    prefix = line.split(ref_year_match.group(0))[0]
    ref_authors = AUTHOR_NAME_PATTERN.findall(prefix)

    prepared_return = []
    for author in ref_authors:
        prepared_return.append((author, ref_year))

    return prepared_return


def get_reference_author_prefix(line):
    """
    Returns the author portion of a reference-list line: the text before the
    year parenthesis. Returns an empty string if no year is found. Used to
    inspect author separators without matching "and"/"&" that appear later in
    the entry's title or publisher.

    Example:
        Input:  "Smith A & Jones B (2020) Crime and punishment. Pub, City"
        Output: "Smith A & Jones B "
    """
    ref_year_match = REFERENCE_YEAR_PATTERN.search(line)
    if not ref_year_match:
        return ''
    return line.split(ref_year_match.group(0))[0]


def get_reference_post_year(line):
    """
    Returns the portion of a reference-list line after the year parenthesis
    (title, journal, volume/issue, etc.), or an empty string if no year is
    found. Used to inspect the journal volume/issue format without the
    author-year region interfering.

    Example:
        Input:  "Smith A (2020) A study. Journal of Things, 16(2):100-110"
        Output: " A study. Journal of Things, 16(2):100-110"
    """
    ref_year_match = REFERENCE_YEAR_PATTERN.search(line)
    if not ref_year_match:
        return ''
    return line[ref_year_match.end():]


def extract_narrative_citations(line):
    """
    Finds narrative (in-prose) citations, where author names appear in the
    running text and only the year is parenthesized, e.g.
    "Liesenfeld and Dingemanse (2024)". Returns a list of synthesized citation
    strings of the form "<authors> <year>" that downstream key extraction can
    consume the same way as a bracketed citation.

    The authors are taken from the contiguous run of capitalized name tokens
    immediately preceding the year parenthesis, so lowercase lead-in words
    ("according to", "by") are not mistaken for authors. A parenthesis with no
    such preceding name run (e.g. "the Treaty was signed (2019)") yields
    nothing.

    Example:
        Input:  "As shown by Liesenfeld and Dingemanse (2024), this holds."
        Output: ["Liesenfeld and Dingemanse 2024"]
    """
    narrative_cites = []
    for match in NARRATIVE_YEAR_PATTERN.finditer(line):
        year = match.group(1)
        preceding_text = line[:match.start()].rstrip()
        authors_match = NARRATIVE_AUTHORS_PATTERN.search(preceding_text)
        if not authors_match:
            continue
        authors = authors_match.group(1).strip()
        narrative_cites.append(f"{authors} {year}")
    return narrative_cites


def extract_inline_citations(line, whitelist):
    """
    Given a stripped line of body/appendix text, returns the list of
    cleaned, individual inline citation strings found in the line, filtered
    by whitelist. Two forms are recognized:

      - Bracketed citations inside [] or (), split on ';' for multi-citation
        brackets, e.g. "(Smith, 2026; Jones 2024)".
      - Narrative citations, where the authors are in the prose and only the
        year is parenthesized, e.g. "Liesenfeld and Dingemanse (2024)". These
        are returned as synthesized "<authors> <year>" strings.

    A parenthesis that contains only a year is treated as the year half of a
    narrative citation rather than a bracketed citation, so it is not emitted
    as a bare "2024" cite.

    Example:
        Input:  "This is shown elsewhere (Smith, 2026; Jones 2024).", {}
        Output: ["Smith, 2026", "Jones 2024"]
    """
    cites = []
    for match in re.findall(INLINE_BRACKET_PATTERN, line):
        raw_cite = next((m for m in match if m), None)
        if not raw_cite:
            continue
        for cite in raw_cite.split(';'):
            clean_cite = cite.strip()
            # A year-only parenthesis is the year half of a narrative citation
            # (handled below), not a bracketed citation in its own right.
            if NARRATIVE_YEAR_PATTERN.fullmatch(f"({clean_cite})"):
                continue
            if clean_cite and clean_cite not in whitelist:
                cites.append(clean_cite)

    for narrative_cite in extract_narrative_citations(line):
        if narrative_cite not in whitelist:
            cites.append(narrative_cite)

    return cites


def read_document(file_path):
    """
    Reads a file into a list of lines, or returns None on failure.

    Example:
        Input:  "paper.txt" (file contains "Line one\\nLine two\\n")
        Output: ["Line one\\n", "Line two\\n"]
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.readlines()
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None


def parse_document(lines, whitelist):
    """
    Walks the document, tracking which section (text/references/appendix)
    each line belongs to, and builds the core data structures used for
    analysis. Body-text and appendix lines are both scanned for inline
    citations; only reference-list lines populate the reference data:
      - raw_reference_list: every reference-list line, in order
      - references_by_key: {(author, year): [reference lines]}
      - raw_inline_citations: {raw inline citation text: [(author, year), ...]}
      - citations_by_key: {(author, year): [raw inline citation text, ...]}
      - narrative_citations: {raw inline citation text} for the subset that are
        narrative (in-prose) citations, e.g. "Liesenfeld and Dingemanse 2024".
        These are excluded from the comma-style check, which only applies to
        parenthetical citations.

    Example:
        Input:
            [
                "Body text (Smith, 2026).\\n",
                "References\\n",
                "Smith, J. (2026). A study of things.\\n",
            ], {}
        Output:
            (
                ["Smith, J. (2026). A study of things."],
                {("Smith", "2026"): ["Smith, J. (2026). A study of things."]},
                {"Smith, 2026": [("Smith", "2026")]},
                {("Smith", "2026"): ["Smith, 2026"]},
                set(),
            )
    """
    raw_reference_list = []
    references_by_key = {}
    raw_inline_citations = {}
    citations_by_key = {}
    narrative_citations = set()

    current_section = "text"

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue

        if REFERENCE_START_PATTERN.match(stripped_line):
            current_section = "references"
            continue

        if APPENDIX_START_PATTERN.match(stripped_line):
            current_section = "appendix"
            continue

        if current_section == "references":
            raw_reference_list.append(stripped_line)
            for key in extract_reference_keys(stripped_line):
                references_by_key.setdefault(key, []).append(stripped_line)
        elif current_section in ("text", "appendix"):
            # Body text and appendix material are both scanned for inline
            # citations and matched against the reference list the same way.
            line_narrative = set(extract_narrative_citations(stripped_line))
            narrative_citations.update(line_narrative)
            for clean_cite in extract_inline_citations(stripped_line, whitelist):
                keys = extract_apa_keys_from_inline(clean_cite)
                for key in keys:
                    citations_by_key.setdefault(key, []).append(clean_cite)
                raw_inline_citations[clean_cite] = keys

    return (
        raw_reference_list,
        references_by_key,
        raw_inline_citations,
        citations_by_key,
        narrative_citations,
    )
