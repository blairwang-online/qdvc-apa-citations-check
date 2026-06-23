# Conversation with Google AI mode

## 1. User request

python script to check a document for citation errors

## 2. LLM response

This Python script checks a .txt document for common citation errors (like dangling in-text citations with no matching entry in the reference list, or unused references at the end of the document). It works by using Regular Expressions (Regex) to extract inline citations and comparing them to the references section. [1, 2] 

### Python Script

```python
import re

def check_citations(file_path):
    # Regex patterns (Adjust based on your document's citation style)
    # Inline citation example: [1], [Smith, 2023], or (Jones et al., 2021)
    inline_pattern = r'\[(.*?)\]|\((.*?)\)'
    
    # Matches the reference section (assumes a section starting with 'References')
    reference_start_pattern = re.compile(r'^#*\s*references', re.IGNORECASE)
    
    inline_citations = set()
    references_list = set()
    in_reference_section = False

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return

    # 1. Parse document to separate inline citations from reference lists
    for line in lines:
        stripped_line = line.strip()
        
        # Check if we reached the reference section
        if reference_start_pattern.match(stripped_line):
            in_reference_section = True
            continue

        if in_reference_section:
            # Add to references if it's not a blank line
            if stripped_line:
                references_list.add(stripped_line)
        else:
            # Extract inline citations from the text
            matches = re.findall(inline_pattern, stripped_line)
            for match in matches:
                # Get non-empty match (since we have multiple capturing groups in Regex)
                cite = next((m for m in match if m), None)
                if cite:
                    inline_citations.add(cite.strip())

    # 2. Analyze
    missing_in_references = inline_citations - references_list
    unused_references = references_list - inline_citations

    # 3. Report Results
    print("--- CITATION AUDIT REPORT ---")
    
    print("\n1. Inline citations missing from the Reference list:")
    if missing_in_references:
        for ref in missing_in_references:
            print(f"  - {ref}")
    else:
        print("  None! All inline citations have a matching reference.")

    print("\n2. References in the list with no corresponding inline citation:")
    if unused_references:
        for ref in unused_references:
            print(f"  - {ref}")
    else:
        print("  None! All references are actively cited.")

# Example usage (replace 'document.txt' with your file)
check_citations('document.txt')
```

### How it works:

1. Separates Text: It looks for a header named "References" to split your text into body paragraphs (where your inline citations live) and the reference list.
2. Extracts Citations: It uses regular expressions to find all text in parentheses () or brackets [] as your in-text citations.
3. Compares Sets: It calculates the mathematical difference between your sets of citations to identify discrepancies. [1, 3] 

### Limitations & Next Steps:

* Style Constraints: This script assumes you use bracketed numbers (e.g., [1]) or author-year (e.g., (Smith, 2023)). If you use superscripts or footnotes, you may need to tweak the inline_pattern variable. [3] 
* Complex Documents: If your document is a .docx file, you should convert it to text first using a library like docx2txt. [1] 
* Advanced Verification: For verifying the accuracy of the academic claims, you can utilize external APIs and GitHub tools like [refchecker](https://github.com/markrussinovich/refchecker) to cross-reference metadata with CrossRef. [4, 5, 6] 

### References

- [1] [https://levelup.gitconnected.com](https://levelup.gitconnected.com/count-citations-in-a-word-document-with-python-and-regular-expressions-d068218c50b9)
- [2] [https://www.econtentpro.com](https://www.econtentpro.com/blog/common-citation-errors/53)
- [3] [https://www.youtube.com](https://www.youtube.com/watch?v=b0v8z3d1GvY&t=4)
- [4] [https://github.com](https://github.com/benchflow-ai/skillsbench/blob/main/tasks/citation-check/environment/skills/citation-management/SKILL.md)
- [5] [https://github.com](https://github.com/markrussinovich/refchecker)
- [6] [https://github.com](https://github.com/markrussinovich/refchecker)

## 3. User request

The Python script is very good, please modify it so that it can handle refs separated by semicolon e.g. (Smith, 2026; Jones, 2021; James, 1999). Also make it whitelist the following exact strings: "see Section 2", "as promised".

## 4. LLM response

Here is the updated script. It now splits multiple citations separated by semicolons inside the same brackets or parentheses, cleans up any leading or trailing spaces, and skips your specified whitelist strings.

### Updated Python Script

```python
import re

def check_citations(file_path):
    # Regex patterns 
    # Inline citation example: [Smith, 2023], (Jones, 2021), or (Smith, 2026; Jones, 2021)
    inline_pattern = r'\[(.*?)\]|\((.*?)\)'
    
    # Matches the reference section (assumes a section starting with 'References')
    reference_start_pattern = re.compile(r'^#*\s*references', re.IGNORECASE)
    
    # Whitelist of exact strings to ignore during the check
    whitelist = {"see Section 2", "as promised"}
    
    inline_citations = set()
    references_list = set()
    in_reference_section = False

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return

    # 1. Parse document to separate inline citations from reference lists
    for line in lines:
        stripped_line = line.strip()
        
        # Check if we reached the reference section
        if reference_start_pattern.match(stripped_line):
            in_reference_section = True
            continue

        if in_reference_section:
            # Add to references if it's not a blank line
            if stripped_line:
                references_list.add(stripped_line)
        else:
            # Extract inline citations from the text
            matches = re.findall(inline_pattern, stripped_line)
            for match in matches:
                # Get non-empty match from regex capturing groups
                raw_cite = next((m for m in match if m), None)
                if raw_cite:
                    # Split citations by semicolon to handle multiple entries
                    individual_cites = raw_cite.split(';')
                    for cite in individual_cites:
                        clean_cite = cite.strip()
                        # Only add if it's not empty and not in the whitelist
                        if clean_cite and clean_cite not in whitelist:
                            inline_citations.add(clean_cite)

    # 2. Analyze
    missing_in_references = inline_citations - references_list
    unused_references = references_list - inline_citations

    # 3. Report Results
    print("--- CITATION AUDIT REPORT ---")
    
    print("\n1. Inline citations missing from the Reference list:")
    if missing_in_references:
        for ref in missing_in_references:
            print(f"  - {ref}")
    else:
        print("  None! All inline citations have a matching reference.")

    print("\n2. References in the list with no corresponding inline citation:")
    if unused_references:
        for ref in unused_references:
            print(f"  - {ref}")
    else:
        print("  None! All references are actively cited.")

# Example usage
check_citations('document.txt')
```

### What Changed:

* Semicolon Splitting: The script now uses .split(';') on every extracted bracket/parentheses match. A string like (Smith, 2026; Jones, 2021) becomes two individual elements: Smith, 2026 and Jones, 2021.
* String Cleaning: Each split item automatically has .strip() applied to remove the spaces after the semicolon.
* Whitelist Filtering: The whitelist set contains your exact exceptions. The script checks if clean_cite not in whitelist: before validating it against the reference list.

If you would like to proceed, I can help you extend this by making the whitelist case-insensitive or allowing it to match partial phrases using regex. Would you like to add either of those features?

## 5. User request

modify the script to allow references heading to start with a number e.g. "7. References"

## 6. LLM response

Here is the updated script. The regular expression has been modified to detect the reference section even if it is preceded by numbers, periods, spaces, or Markdown headers (e.g., 7. References, 7 References, or ### 7.1 References).

### Updated Python Script

```python
import re

def check_citations(file_path):
    # Regex patterns 
    # Inline citation example: [Smith, 2023], (Jones, 2021), or (Smith, 2026; Jones, 2021)
    inline_pattern = r'\[(.*?)\]|\((.*?)\)'
    
    # Matches reference section starting with optional Markdown (#), numbers, dots, and spaces
    # Examples matched: "7. References", "7 References", "### 7.1 References", "References"
    reference_start_pattern = re.compile(r'^#*\s*(?:\d+(?:\.\d+)*\s*\.?\s*)?references', re.IGNORECASE)
    
    # Whitelist of exact strings to ignore during the check
    whitelist = {"see Section 2", "as promised"}
    
    inline_citations = set()
    references_list = set()
    in_reference_section = False

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return

    # 1. Parse document to separate inline citations from reference lists
    for line in lines:
        stripped_line = line.strip()
        
        # Check if we reached the reference section
        if reference_start_pattern.match(stripped_line):
            in_reference_section = True
            continue

        if in_reference_section:
            # Add to references if it's not a blank line
            if stripped_line:
                references_list.add(stripped_line)
        else:
            # Extract inline citations from the text
            matches = re.findall(inline_pattern, stripped_line)
            for match in matches:
                # Get non-empty match from regex capturing groups
                raw_cite = next((m for m in match if m), None)
                if raw_cite:
                    # Split citations by semicolon to handle multiple entries
                    individual_cites = raw_cite.split(';')
                    for cite in individual_cites:
                        clean_cite = cite.strip()
                        # Only add if it's not empty and not in the whitelist
                        if clean_cite and clean_cite not in whitelist:
                            inline_citations.add(clean_cite)

    # 2. Analyze
    missing_in_references = inline_citations - references_list
    unused_references = references_list - inline_citations

    # 3. Report Results
    print("--- CITATION AUDIT REPORT ---")
    
    print("\n1. Inline citations missing from the Reference list:")
    if missing_in_references:
        for ref in missing_in_references:
            print(f"  - {ref}")
    else:
        print("  None! All inline citations have a matching reference.")

    print("\n2. References in the list with no corresponding inline citation:")
    if unused_references:
        for ref in unused_references:
            print(f"  - {ref}")
    else:
        print("  None! All references are actively cited.")

# Example usage
check_citations('document.txt')
```

### What Changed:

* Flexible Heading Regex: The reference_start_pattern was updated to r'^#*\s*(?:\d+(?:\.\d+)*\s*\.?\s*)?references'.
* Breakdown of the new Regex:
* ^#*\s* handles optional Markdown header syntax and leading spaces.
   * (?:\d+(?:\.\d+)*\s*\.?\s*)? optionally matches integers or decimals (like 7 or 7.1), an optional trailing full stop, and any trailing whitespace.
   * references looks for the word "references" case-insensitively.

Would you like to modify how the Reference list entries are parsed next? For example, we could make it strip out leading numbers or bullet points (like [1], 1., or *) from the bibliography items so they match your in-text tags perfectly.

## 7. User request

modify the script to allow for an Appendix section after the References section. Treat the Appendix section as normal manuscript text

## 8. LLM response

Here is the updated script. It now looks for an Appendix heading (with or without numbers, just like the References heading) to signal the end of the bibliography. Once it hits the Appendix, it switches back to scanning for inline citations. [1] 

### Updated Python Script

```python
import re

def check_citations(file_path):
    # Regex patterns 
    # Inline citation example: [Smith, 2023], (Jones, 2021), or (Smith, 2026; Jones, 2021)
    inline_pattern = r'\[(.*?)\]|\((.*?)\)'
    
    # Matches reference section starting with optional Markdown (#), numbers, dots, and spaces
    # Examples matched: "7. References", "7 References", "### 7.1 References", "References"
    reference_start_pattern = re.compile(r'^#*\s*(?:\d+(?:\.\d+)*\s*\.?\s*)?references', re.IGNORECASE)
    
    # Matches appendix section starting with optional Markdown (#), numbers, dots, and spaces
    # Examples matched: "8. Appendix", "Appendix A", "### Appendix"
    appendix_start_pattern = re.compile(r'^#*\s*(?:\d+(?:\.\d+)*\s*\.?\s*)?appendix', re.IGNORECASE)
    
    # Whitelist of exact strings to ignore during the check
    whitelist = {"see Section 2", "as promised"}
    
    inline_citations = set()
    references_list = set()
    
    # State tracking: "text", "references", or "appendix"
    current_section = "text"

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return

    # 1. Parse document based on sections
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue
        
        # Check if we reached the reference section
        if reference_start_pattern.match(stripped_line):
            current_section = "references"
            continue
            
        # Check if we reached the appendix section
        if appendix_start_pattern.match(stripped_line):
            current_section = "appendix"
            continue

        # Process the line based on the current active section
        if current_section == "references":
            # Collect the bibliography entries
            references_list.add(stripped_line)
        else:
            # Both "text" and "appendix" sections look for inline citations
            matches = re.findall(inline_pattern, stripped_line)
            for match in matches:
                # Get non-empty match from regex capturing groups
                raw_cite = next((m for m in match if m), None)
                if raw_cite:
                    # Split citations by semicolon to handle multiple entries
                    individual_cites = raw_cite.split(';')
                    for cite in individual_cites:
                        clean_cite = cite.strip()
                        # Only add if it's not empty and not in the whitelist
                        if clean_cite and clean_cite not in whitelist:
                            inline_citations.add(clean_cite)

    # 2. Analyze
    missing_in_references = inline_citations - references_list
    unused_references = references_list - inline_citations

    # 3. Report Results
    print("--- CITATION AUDIT REPORT ---")
    
    print("\n1. Inline citations missing from the Reference list:")
    if missing_in_references:
        for ref in missing_in_references:
            print(f"  - {ref}")
    else:
        print("  None! All inline citations have a matching reference.")

    print("\n2. References in the list with no corresponding inline citation:")
    if unused_references:
        for ref in unused_references:
            print(f"  - {ref}")
    else:
        print("  None! All references are actively cited.")

# Example usage
check_citations('document.txt')
```

### What Changed:

* Section State Tracking: Replaced the boolean in_reference_section with a string variable called current_section. It starts as "text", shifts to "references", and shifts to "appendix" when it detects the respective headers.
* Appendix Identification: Added appendix_start_pattern using a similar flexible regex to the reference tracker. It will catch headers like 8. Appendix, Appendix A, or ### Appendix.
* Dual-Section Scanning: The script evaluates if current_section == "references": to add lines to your bibliography. The else: block catches everything else, meaning both the main body text and the appendix are scanned for parenthetical citations.

Do you want to adjust how the script handles cross-references inside the appendix (like (see Appendix A)) so they do not flag as missing citations?

### References

[1] [https://tex.stackexchange.com](https://tex.stackexchange.com/questions/21317/appendix-without-sections)

## 9. User request

It doesn't seem to be able to handle APA referencing, all APA in-line references are flagged as missing from References list

## 10. LLM response

The issue occurs because APA inline citations look different from APA reference list entries, causing a direct string match to fail.
For example, an inline citation looks like (Smith & Jones, 2020), but the reference list entry starts with a full citation like Smith, J., & Jones, M. (2020). Journal Article Title....
To fix this, we need to extract the key tracking elements (the authors and the year) from both the text and the reference list, and then match them programmatically.
Here is the updated script designed specifically to accurately match APA-style citations.

### Updated Python Script

```python
import re

def extract_apa_keys_from_inline(cite_text):
    """
    Extracts (Author, Year) keys from a raw inline citation string.
    Handles multiple authors, 'et al.', '&', and 'and'.
    """
    # Regex to pull a 4-digit year from the end of the citation token
    year_match = re.search(r'\b(19\d{2}|20\d{2})[a-z]?\b', cite_text)
    if not year_match:
        return []
    year = year_match.group(1)
    
    # Remove the year, parentheses, commas to isolate author names
    name_part = re.sub(r'\b(19\d{2}|20\d{2})[a-z]?\b', '', cite_text)
    name_part = re.sub(r'[\(\),]', '', name_part).strip()
    
    # Extract all individual capitalized words (last names)
    # Excludes common conjunctions and 'et al'
    authors = re.findall(r'\b[A-Z][a-zA-Z\-]+\b', name_part)
    authors = [a for a in authors if a.lower() not in ['and', 'et', 'al']]
    
    # Return keys for matching: e.g., [("Smith", "2020"), ("Jones", "2020")]
    return [(author, year) for author in authors]

def check_citations(file_path):
    # Extracts everything inside brackets or parentheses
    inline_pattern = r'\[(.*?)\]|\((.*?)\)'
    
    # Section header detection
    reference_start_pattern = re.compile(r'^#*\s*(?:\d+(?:\.\d+)*\s*\.?\s*)?references', re.IGNORECASE)
    appendix_start_pattern = re.compile(r'^#*\s*(?:\d+(?:\.\d+)*\s*\.?\s*)?appendix', re.IGNORECASE)
    
    whitelist = {"see Section 2", "as promised"}
    
    # Store raw entries for the final report
    raw_inline_citations = {}
    raw_reference_list = []
    
    # Tracking maps for core data structures
    # Keys will look like: ("Smith", "2020")
    citations_by_key = {} 
    references_by_key = {}

    current_section = "text"

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return

    # 1. Parse document based on sections
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue
        
        if reference_start_pattern.match(stripped_line):
            current_section = "references"
            continue
            
        if appendix_start_pattern.match(stripped_line):
            current_section = "appendix"
            continue

        # Process Reference Section
        if current_section == "references":
            raw_reference_list.append(stripped_line)
            
            # Extract keys from the reference list entry (e.g., "Smith, J. (2020)")
            # Find the year inside parentheses in the bibliography line
            ref_year_match = re.search(r'\((19\d{2}|20\d{2})[a-z]?\)', stripped_line)
            if ref_year_match:
                ref_year = ref_year_match.group(1)
                # Find all authors preceding the year
                prefix = stripped_line.split(ref_year_match.group(0))[0]
                ref_authors = re.findall(r'\b[A-Z][a-zA-Z\-]+\b', prefix)
                
                for author in ref_authors:
                    key = (author, ref_year)
                    if key not in references_by_key:
                        references_by_key[key] = []
                    references_by_key[key].append(stripped_line)

        # Process Main Body Text & Appendix
        else:
            matches = re.findall(inline_pattern, stripped_line)
            for match in matches:
                raw_cite = next((m for m in match if m), None)
                if raw_cite:
                    individual_cites = raw_cite.split(';')
                    for cite in individual_cites:
                        clean_cite = cite.strip()
                        if clean_cite and clean_cite not in whitelist:
                            # Map the raw text to its broken-down author/year keys
                            keys = extract_apa_keys_from_inline(clean_cite)
                            for key in keys:
                                if key not in citations_by_key:
                                    citations_by_key[key] = []
                                citations_by_key[key].append(clean_cite)
                            
                            # Keep track of all unique raw inline text
                            raw_inline_citations[clean_cite] = keys

    # 2. Analyze using fuzzy key-matching logic
    missing_in_references = set()
    used_reference_entries = set()

    # Check which inline citations lack a matching reference key
    for raw_cite, keys in raw_inline_citations.items():
        if not keys: # Skip if the bracket context contains no valid citation formatting
            continue
        
        # An inline citation is validated if ANY of its author-year tokens match a reference entry
        matched = False
        for key in keys:
            if key in references_by_key:
                matched = True
                for ref_entry in references_by_key[key]:
                    used_reference_entries.add(ref_entry)
        
        if not matched:
            missing_in_references.add(raw_cite)

    # Determine unused reference lines
    unused_references = [ref for ref in raw_reference_list if ref not in used_reference_entries]

    # 3. Report Results
    print("--- APA CITATION AUDIT REPORT ---")
    
    print("\n1. Inline citations missing from the Reference list:")
    if missing_in_references:
        for ref in sorted(missing_in_references):
            print(f"  - ({ref})")
    else:
        print("  None! All inline citations match a valid bibliography entry.")

    print("\n2. References in the list with no corresponding inline citation:")
    if unused_references:
        for ref in sorted(unused_references):
            print(f"  - {ref}")
    else:
        print("  None! All references are actively cited in your text.")

# Example usage
check_citations('document.txt')
```

### How this resolves the APA issue:

   1. Key Extraction Instead of String Matching: It stops expecting the literal text (Smith & Jones, 2020) to equal the full text string Smith, J., & Jones, M. (2020)....
   2. Fuzzy In-Text Parsing: The extract_apa_keys_from_inline() helper looks inside your text parentheses, isolates the 4-digit year, strips out clutter (&, and, et al.), and yields tracking tokens like ("Smith", "2020") and ("Jones", "2020").
   3. Fuzzy Reference Parsing: When looking at the reference list, it finds the APA year marker—(2020)—and maps all preceding capitalised last names to that same tracking token.
   4. Successful Cross-Validation: If the script finds at least one matching Author + Year pairing between your inline note and your final reference entries, it accepts it as a successful citation match.

Would you like to fine-tune this further to support narrative citations where the author's name is outside the parentheses, such as Smith (2020) argued that...?

## 11. User request

Please make it handle the following reference:

In-line: (Smith & Jones, 2023)

References section: Smith, J., & Jones, M. (2023, 23 May). Badgers win Quidditch game. New Cork Times.

## 12. LLM response

Here is the updated script. It resolves this specific issue by modernising the reference list processor to extract only the 4-digit year from the beginning of complex date blocks like (2023, 23 May).

### Updated Python Script

```python
import re

def extract_apa_keys_from_inline(cite_text):
    """
    Extracts (Author, Year) keys from a raw inline citation string.
    Handles multiple authors, 'et al.', '&', and 'and'.
    """
    # Regex to pull a 4-digit year from the end of the citation token
    year_match = re.search(r'\b(19\d{2}|20\d{2})[a-z]?\b', cite_text)
    if not year_match:
        return []
    year = year_match.group(1)
    
    # Remove the year, parentheses, commas to isolate author names
    name_part = re.sub(r'\b(19\d{2}|20\d{2})[a-z]?\b', '', cite_text)
    name_part = re.sub(r'[\(\),]', '', name_part).strip()
    
    # Extract all individual capitalized words (last names)
    # Excludes common conjunctions and 'et al'
    authors = re.findall(r'\b[A-Z][a-zA-Z\-]+\b', name_part)
    authors = [a for a in authors if a.lower() not in ['and', 'et', 'al']]
    
    # Return keys for matching: e.g., [("Smith", "2023"), ("Jones", "2023")]
    return [(author, year) for author in authors]

def check_citations(file_path):
    # Extracts everything inside brackets or parentheses
    inline_pattern = r'\[(.*?)\]|\((.*?)\)'
    
    # Section header detection
    reference_start_pattern = re.compile(r'^#*\s*(?:\d+(?:\.\d+)*\s*\.?\s*)?references', re.IGNORECASE)
    appendix_start_pattern = re.compile(r'^#*\s*(?:\d+(?:\.\d+)*\s*\.?\s*)?appendix', re.IGNORECASE)
    
    whitelist = {"see Section 2", "as promised"}
    
    # Store raw entries for the final report
    raw_inline_citations = {}
    raw_reference_list = []
    
    # Tracking maps for core data structures
    citations_by_key = {} 
    references_by_key = {}

    current_section = "text"

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return

    # 1. Parse document based on sections
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue
        
        if reference_start_pattern.match(stripped_line):
            current_section = "references"
            continue
            
        if appendix_start_pattern.match(stripped_line):
            current_section = "appendix"
            continue

        # Process Reference Section
        if current_section == "references":
            raw_reference_list.append(stripped_line)
            
            # Matches the year inside parentheses, allowing for trailing months/days
            # e.g., matches "(2023, 23 May)" or "(2023)" and extracts "2023"
            ref_year_match = re.search(r'\(((?:19|20)\d{2})(?:,?\s*[^)]*)?\)', stripped_line)
            if ref_year_match:
                ref_year = ref_year_match.group(1)
                
                # Find all authors preceding the matched year block
                # Uses the full matched string (e.g., "(2023, 23 May)") to split the line
                prefix = stripped_line.split(ref_year_match.group(0))[0]
                ref_authors = re.findall(r'\b[A-Z][a-zA-Z\-]+\b', prefix)
                
                for author in ref_authors:
                    key = (author, ref_year)
                    if key not in references_by_key:
                        references_by_key[key] = []
                    references_by_key[key].append(stripped_line)

        # Process Main Body Text & Appendix
        else:
            matches = re.findall(inline_pattern, stripped_line)
            for match in matches:
                raw_cite = next((m for m in match if m), None)
                if raw_cite:
                    individual_cites = raw_cite.split(';')
                    for cite in individual_cites:
                        clean_cite = cite.strip()
                        if clean_cite and clean_cite not in whitelist:
                            # Map the raw text to its broken-down author/year keys
                            keys = extract_apa_keys_from_inline(clean_cite)
                            for key in keys:
                                if key not in citations_by_key:
                                    citations_by_key[key] = []
                                citations_by_key[key].append(clean_cite)
                            
                            # Keep track of all unique raw inline text
                            raw_inline_citations[clean_cite] = keys

    # 2. Analyze using fuzzy key-matching logic
    missing_in_references = set()
    used_reference_entries = set()

    # Check which inline citations lack a matching reference key
    for raw_cite, keys in raw_inline_citations.items():
        if not keys: # Skip if the bracket context contains no valid citation formatting
            continue
        
        matched = False
        for key in keys:
            if key in references_by_key:
                matched = True
                for ref_entry in references_by_key[key]:
                    used_reference_entries.add(ref_entry)
        
        if not matched:
            missing_in_references.add(raw_cite)

    # Determine unused reference lines
    unused_references = [ref for ref in raw_reference_list if ref not in used_reference_entries]

    # 3. Report Results
    print("--- APA CITATION AUDIT REPORT ---")
    
    print("\n1. Inline citations missing from the Reference list:")
    if missing_in_references:
        for ref in sorted(missing_in_references):
            print(f"  - ({ref})")
    else:
        print("  None! All inline citations match a valid bibliography entry.")

    print("\n2. References in the list with no corresponding inline citation:")
    if unused_references:
        for ref in sorted(unused_references):
            print(f"  - {ref}")
    else:
        print("  None! All references are actively cited in your text.")

# Example usage
check_citations('document.txt')
```

### What Changed:

* Advanced Year Matching: The original regex looked strictly for closed 4-digit numeric brackets like (2023). The updated line re.search(r'\(((?:19|20)\d{2})(?:,?\s*[^)]*)?\)', stripped_line) safely targets the first four numbers within the parenthesis block, treating , 23 May as non-capturing noise.
* Isolating Author Prefixes: It dynamically splits the bibliography entry at the exact point of the updated date-parenthesis string. This guarantees that initials or text coming after the date (like Badgers win...) aren't accidentally mistaken for author surnames.

Would you like to test this script on corporate or organizational authors (e.g., (World Health Organization, 2024)) so they aren't incorrectly split up into separate individual names?

