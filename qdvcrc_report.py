"""
qdvcrc_report.py

Formats and prints the final APA citation audit report. Imported by
check_refs.py.
"""


def print_report(missing_in_references, unused_references, style_violations, uses_comma_intext):
    """
    Prints the formatted three-section APA citation audit report to stdout.
    Returns nothing.

    Example:
        Input:
            missing_in_references = {"Nguyen, 2025"}
            unused_references = ["Patel, R. (2021). Unused reference."]
            style_violations = ["Jones 2024"]
            uses_comma_intext = True
        Output (printed):
            --- APA CITATION AUDIT REPORT ---

            1. Inline citations missing from the Reference list:
              - (Nguyen, 2025)

            2. References in the list with no corresponding inline citation:
              - Patel, R. (2021). Unused reference.

            3. Inline citations not matching the configured style (Smith, 2026):
              - (Jones 2024)
    """
    style_example = "(Smith, 2026)" if uses_comma_intext else "(Smith 2026)"

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

    print(f"\n3. Inline citations not matching the configured style {style_example}:")
    if style_violations:
        for ref in style_violations:
            print(f"  - ({ref})")
    else:
        print("  None! All inline citations consistently use the configured style.")
