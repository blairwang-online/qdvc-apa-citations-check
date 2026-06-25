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
REFERENCE_YEAR_PATTERN = re.compile(r'\(((?:19|20)\d{2})(?:,?\s*[^)]*)?\)')

# Matches a 4-digit year (optionally suffixed, e.g. "2023a") anywhere in text
YEAR_PATTERN = re.compile(r'\b(16\d{2}|17\d{2}|18\d{2}|19\d{2}|20\d{2})[a-z]?\b')


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
    authors = re.findall(r'\b[A-Z][a-zA-Z\-]+\b', name_part)
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
    ref_authors = re.findall(r'\b[A-Z][a-zA-Z\-]+\b', prefix)

    prepared_return = []
    for author in ref_authors:
        prepared_return.append((author, ref_year))

    return prepared_return


def extract_inline_citations(line, whitelist):
    """
    Given a stripped line of body/appendix text, returns the list of
    cleaned, individual inline citation strings found inside [] or (),
    split on ';' for multi-citation brackets, and filtered by whitelist.

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
            if clean_cite and clean_cite not in whitelist:
                cites.append(clean_cite)
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
    analysis:
      - raw_reference_list: every reference-list line, in order
      - references_by_key: {(author, year): [reference lines]}
      - raw_inline_citations: {raw inline citation text: [(author, year), ...]}
      - citations_by_key: {(author, year): [raw inline citation text, ...]}

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
            )
    """
    raw_reference_list = []
    references_by_key = {}
    raw_inline_citations = {}
    citations_by_key = {}

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
        else:
            for clean_cite in extract_inline_citations(stripped_line, whitelist):
                keys = extract_apa_keys_from_inline(clean_cite)
                for key in keys:
                    citations_by_key.setdefault(key, []).append(clean_cite)
                raw_inline_citations[clean_cite] = keys

    return raw_reference_list, references_by_key, raw_inline_citations, citations_by_key
