# Technical info provided by Claude

**check_refs — APA Citation Checker** 

Audits a research paper (plain text) for APA citation consistency:
1. Inline citations with no matching reference-list entry
2. Reference-list entries with no matching inline citation
3. Inline citations that don't follow the configured comma style
4. Reference-list entries that aren't in alphabetical order

## File Overview

### `check_refs.py` (main file)

| Function | Description | Example Input | Example Output |
|---|---|---|---|
| `check_citations(file_path)` | Runs the full APA citation audit on the given file and prints a report. | `"paper.txt"` (a file containing body text with (Author, Year) citations and a References section) | *(printed)* the three-section APA CITATION AUDIT REPORT |

Also defines the configuration constants:
- `USES_COMMA_INTEXT` — controls the expected in-text citation style: `True` for comma style `(Smith, 2026)`, `False` for no-comma style `(Smith 2026)`.
- `whitelist` — raw inline citation strings in this set are ignored entirely (e.g. for non-citation bracketed content you don't want flagged).

### `qdvcrc_parsing.py`

Low-level helpers for reading a document and extracting citation and reference data from it.

| Function | Description | Example Input | Example Output |
|---|---|---|---|
| `extract_apa_keys_from_inline(cite_text)` | Extracts (Author, Year) keys from a raw inline citation string. Handles multiple authors, 'et al.', '&', and 'and'. | `"Smith & Jones, 2026"` | `[("Smith", "2026"), ("Jones", "2026")]` |
| `extract_reference_keys(line)` | Given a stripped reference-list line, returns the (Author, Year) keys found in it, based on the year in parentheses and the author names preceding it. | `"Smith, J. (2026). A study of things. Journal of Things."` | `[("Smith", "2026")]` |
| `extract_inline_citations(line, whitelist)` | Given a stripped line of body/appendix text, returns cleaned inline citation strings, filtered by whitelist. Recognizes both bracketed citations inside `[]` or `()` (split on `;`) and narrative citations where only the year is parenthesized (returned as synthesized `"<authors> <year>"` strings). | `"This is shown elsewhere (Smith, 2026; Jones 2024)."`, `{}` | `["Smith, 2026", "Jones 2024"]` |
| `extract_narrative_citations(line)` | Finds narrative (in-prose) citations where author names are in the running text and only the year is parenthesized, returning synthesized `"<authors> <year>"` strings. Authors come from the contiguous run of capitalized name tokens immediately before the year parenthesis. | `"As shown by Liesenfeld and Dingemanse (2024), this holds."` | `["Liesenfeld and Dingemanse 2024"]` |
| `read_document(file_path)` | Reads a file into a list of lines, or returns `None` on failure. | `"paper.txt"` (file contains `"Line one\nLine two\n"`) | `["Line one\n", "Line two\n"]` |
| `parse_document(lines, whitelist)` | Walks the document, tracking which section (text/references/appendix) each line belongs to, and builds the core data structures used for analysis. Body-text and appendix lines are both scanned for inline citations; only reference-list lines populate the reference data. Returns a fifth value, a set of the inline citation strings that are narrative citations (excluded from the style check). | `["Body text (Smith, 2026).\n", "References\n", "Smith, J. (2026). A study of things.\n"]`, `{}` | `(["Smith, J. (2026). A study of things."], {("Smith", "2026"): ["Smith, J. (2026). A study of things."]}, {"Smith, 2026": [("Smith", "2026")]}, {("Smith", "2026"): ["Smith, 2026"]}, set())` |

### `qdvcrc_analysis.py`

Functions that analyze the data parsed by `qdvcrc_parsing.py`: cross-matching inline citations against the reference list, finding unused references, and checking in-text style consistency.

| Function | Description | Example Input | Example Output |
|---|---|---|---|
| `matches_intext_style(cite_text, uses_comma_intext)` | Checks whether a cleaned inline citation string follows the given comma style. Citations with no detectable year are treated as not applicable (`True`). | `"Jones 2024"`, `True` | `False` |
| `find_missing_and_used_references(raw_inline_citations, references_by_key)` | Cross-references inline citations against the reference list. Returns inline citation text with no matching reference-list entry, and reference-list lines matched by at least one inline citation. | `raw_inline_citations = {"Smith, 2026": [("Smith","2026")], "Nguyen, 2025": [("Nguyen","2025")]}`<br>`references_by_key = {("Smith","2026"): ["Smith, J. (2026). A study of things."]}` | `({"Nguyen, 2025"}, {"Smith, J. (2026). A study of things."})` |
| `find_unused_references(raw_reference_list, used_reference_entries)` | Returns reference-list lines that no inline citation matched. | `raw_reference_list = ["Smith, J. (2026). A study of things.", "Patel, R. (2021). Unused reference."]`<br>`used_reference_entries = {"Smith, J. (2026). A study of things."}` | `["Patel, R. (2021). Unused reference."]` |
| `find_style_violations(raw_inline_citations, uses_comma_intext, narrative_citations=None)` | Returns a sorted list of inline citations that don't conform to the given comma style. Narrative citations passed in `narrative_citations` are excluded, since the comma convention only applies to parenthetical citations. | `raw_inline_citations = {"Smith, 2026": [("Smith","2026")], "Jones 2024": [("Jones","2024")]}`, `True` | `["Jones 2024"]` |
| `fold_to_ascii(text)` | Reduces a string to a lowercase ASCII form for alphabetical comparison, folding accented and other non-ASCII Latin letters to their base letters (e.g. "Öqvist" -> "oqvist", "Bjørnsson" -> "bjornsson"). Characters with no ASCII equivalent are dropped. | `"Öqvist"` | `"oqvist"` |
| `get_reference_sort_key(line)` | Returns the ASCII-folded, lowercased author-name portion of a reference-list line, used to check alphabetical ordering. APA reference entries start with the first author's surname before the first comma. Accented letters are folded to their base letters so they sort as expected. | `"Smith, J. (2026). A study of things."` | `"smith"` |
| `find_reference_order_violations(raw_reference_list)` | Returns the reference-list lines that are out of alphabetical order relative to the entry immediately before them, based on each entry's leading author surname (the text before the first comma). | `raw_reference_list = ["Smith, J. (2026). A study of things.", "Jones, A. (2024). Another study."]` | `["Jones, A. (2024). Another study."]` |

### `qdvcrc_report.py`

Formats and prints the final APA citation audit report.

| Function | Description | Example Input | Example Output |
|---|---|---|---|
| `print_report(missing_in_references, unused_references, style_violations, order_violations, uses_comma_intext)` | Prints the formatted four-section APA citation audit report to stdout. Returns nothing. | `missing_in_references = {"Nguyen, 2025"}`<br>`unused_references = ["Patel, R. (2021). Unused reference."]`<br>`style_violations = ["Jones 2024"]`<br>`order_violations = ["Jones, A. (2024). Another study."]`<br>`uses_comma_intext = True` | *(printed)*<br>`--- APA CITATION AUDIT REPORT ---`<br>`1. ... missing: - (Nguyen, 2025)`<br>`2. ... unused: - Patel, R. (2021). Unused reference.`<br>`3. ... style: - (Jones 2024)`<br>`4. ... order: - Jones, A. (2024). Another study.` |

## Maintenance Notes

- **All four files must stay in the same directory.** `check_refs.py` imports directly from `qdvcrc_parsing`, `qdvcrc_analysis`, and `qdvcrc_report` by module name (no package structure), so they need to be co-located to run.
- **Configuration lives in `check_refs.py`, not the `qdvcrc_*` modules.** `USES_COMMA_INTEXT` and `whitelist` are defined in the main file and passed into the helper functions as parameters (e.g. `find_style_violations(raw_inline_citations, USES_COMMA_INTEXT)`). This avoids a circular import back into the main file — if you add new configuration, follow the same pattern rather than importing it into a `qdvcrc_*` module.
- **Citation/reference matching is name+year based, not exact-text based.** Both inline citations and reference entries are reduced to `(Author, Year)` key tuples before comparison, so the checker is tolerant of minor formatting differences but can also produce false matches if two different authors share a surname and publication year.
- **Alphabetical-order checking compares each entry only to the one immediately before it**, using the surname before the first comma as the sort key. It flags the entry that breaks the sequence, not every entry that's technically misplaced — so a single line moved out of place will produce one violation, but it won't independently verify the full list is sorted from scratch. The sort key is ASCII-folded via `fold_to_ascii`, so accented surnames (e.g. `Öqvist`, `Bjørnsson`) sort by their base letters rather than by raw code point. This folds away the distinction between accented and base letters; it does not implement locale-specific collation (e.g. Swedish, where `å`/`ä`/`ö` sort after `z`).
- **Year detection spans the 1600s through the 2000s.** Both `YEAR_PATTERN` (inline) and `REFERENCE_YEAR_PATTERN` (reference list) match four-digit years beginning `16`, `17`, `18`, `19`, or `20`, so historical works (e.g. `Hobbes T (1651) Leviathan ...`) are handled. Keep the two patterns' century ranges in sync if you extend them.
- **Appendix material is checked just like body text.** After an `Appendix` heading, lines stay in citation-scanning mode, so inline citations in an appendix are matched against the reference list the same way body-text citations are. The `text` and `appendix` sections share an explicit branch in `parse_document`; only the `references` section feeds the reference data. A reference list that appears *after* an appendix heading is still parsed correctly, because the section flips again when the `References` heading is reached.
- **Author surnames may contain accented letters.** Surname extraction uses `AUTHOR_NAME_PATTERN`, a Unicode-aware regex that accepts an uppercase initial (ASCII or accented, e.g. the `Ä` in `Mähring`) followed by further letters, including hyphenated parts (e.g. `Pries-Heje`). It still requires at least two letters, so single-letter initials (`M` in `Mähring M`) are not treated as surnames. If you need to support scripts beyond the Latin-1 accented range (`À-ÖØ-Þ`), widen the leading character class.
- **Narrative (in-prose) citations are supported.** A citation like `Liesenfeld and Dingemanse (2024)`, where the authors are in the running text and only the year is parenthesized, is detected by `extract_narrative_citations` and matched against the reference list the same way as a bracketed citation. The authors are read from the contiguous run of capitalized name tokens immediately before the year parenthesis, so lowercase lead-in words ("according to", "by") are not mistaken for authors. The trade-off: a capitalized common noun sitting directly before a year parenthesis (e.g. `the Treaty (2019)`) can be misread as an author. Narrative citations are also excluded from the comma-style check, since the comma convention only applies to fully parenthetical citations — `parse_document` returns them as a fifth value (a set) that `check_refs.py` threads into `find_style_violations`.
