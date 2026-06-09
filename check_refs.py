import re

# Only if you need it...
whitelist = {}

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


# Example usage (replace 'document.txt' with your file)
check_citations('check_refs_document.txt')
