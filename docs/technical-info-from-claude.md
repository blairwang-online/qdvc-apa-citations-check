# Technical info provided by Claude

**check_refs — APA Citation Checker**

Audits a research paper (plain text) for APA citation consistency:
1. Inline citations with no matching reference-list entry
2. Reference-list entries with no matching inline citation
3. Inline citations that don't follow the configured comma style

## File Overview

### `check_refs.py` (main file)

| Function | Description |
|---|---|
| `check_citations(file_path)` | Runs the full APA citation audit on the given file and prints a report. |

Also defines the configuration constants:
- `USES_COMMA_INTEXT` — controls the expected in-text citation style: `True` for comma style `(Smith, 2026)`, `False` for no-comma style `(Smith 2026)`.
- `whitelist` — raw inline citation strings in this set are ignored entirely (e.g. for non-citation bracketed content you don't want flagged).

### `qdvcrc_parsing.py`

Low-level helpers for reading a document and extracting citation and reference data from it.

| Function | Description |
|---|---|
| `extract_apa_keys_from_inline(cite_text)` | Extracts (Author, Year) keys from a raw inline citation string. Handles multiple authors, 'et al.', '&', and 'and'. |
| `extract_reference_keys(line)` | Given a stripped reference-list line, returns the (Author, Year) keys found in it, based on the year in parentheses and the author names preceding it. |
| `extract_inline_citations(line, whitelist)` | Given a stripped line of body/appendix text, returns the list of cleaned, individual inline citation strings found inside `[]` or `()`, split on `;` for multi-citation brackets, and filtered by whitelist. |
| `read_document(file_path)` | Reads a file into a list of lines, or returns `None` on failure. |
| `parse_document(lines, whitelist)` | Walks the document, tracking which section (text/references/appendix) each line belongs to, and builds the core data structures used for analysis (`raw_reference_list`, `references_by_key`, `raw_inline_citations`, `citations_by_key`). |

### `qdvcrc_analysis.py`

Functions that analyze the data parsed by `qdvcrc_parsing.py`: cross-matching inline citations against the reference list, finding unused references, and checking in-text style consistency.

| Function | Description |
|---|---|
| `matches_intext_style(cite_text, uses_comma_intext)` | Checks whether a cleaned inline citation string (e.g. "Smith, 2026" or "Smith et al 2026") follows the given comma style. Citations with no detectable year are treated as not applicable (`True`). |
| `find_missing_and_used_references(raw_inline_citations, references_by_key)` | Cross-references inline citations against the reference list. Returns inline citation text with no matching reference-list entry, and reference-list lines that were matched by at least one inline citation. |
| `find_unused_references(raw_reference_list, used_reference_entries)` | Returns reference-list lines that no inline citation matched. |
| `find_style_violations(raw_inline_citations, uses_comma_intext)` | Returns a sorted list of inline citations that don't conform to the given comma style. |

### `qdvcrc_report.py`

Formats and prints the final APA citation audit report.

| Function | Description |
|---|---|
| `print_report(missing_in_references, unused_references, style_violations, uses_comma_intext)` | Prints the formatted three-section APA citation audit report to stdout. Returns nothing. |

## Maintenance Notes

- **All four files must stay in the same directory.** `check_refs.py` imports directly from `qdvcrc_parsing`, `qdvcrc_analysis`, and `qdvcrc_report` by module name (no package structure), so they need to be co-located to run.
- **Configuration lives in `check_refs.py`, not the `qdvcrc_*` modules.** `USES_COMMA_INTEXT` and `whitelist` are defined in the main file and passed into the helper functions as parameters (e.g. `find_style_violations(raw_inline_citations, USES_COMMA_INTEXT)`). This avoids a circular import back into the main file — if you add new configuration, follow the same pattern rather than importing it into a `qdvcrc_*` module.
- **Citation/reference matching is name+year based, not exact-text based.** Both inline citations and reference entries are reduced to `(Author, Year)` key tuples before comparison, so the checker is tolerant of minor formatting differences but can also produce false matches if two different authors share a surname and publication year.
