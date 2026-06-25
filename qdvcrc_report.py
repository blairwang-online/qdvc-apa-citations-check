"""
qdvcrc_report.py

Formats and prints the final APA citation audit report. Imported by
check_refs.py.
"""


def print_report(missing_in_references, unused_references, style_violations,
                 order_violations, uses_comma_intext,
                 intext_separator_violations=None,
                 reference_separator_violations=None,
                 intext_separator="and", reflist_separator="and",
                 volume_issue_violations=None,
                 volume_issue_format="comma"):
    """
    Prints the formatted seven-section APA citation audit report to stdout.
    Returns nothing.

    Example:
        Input:
            missing_in_references = {"Nguyen, 2025"}
            unused_references = ["Patel, R. (2021). Unused reference."]
            style_violations = ["Jones 2024"]
            order_violations = ["Jones, A. (2024). Another study."]
            uses_comma_intext = True
            intext_separator_violations = ["Smith & Jones 2020"]
            reference_separator_violations = ["Brown C and Lee D (2019) ..."]
            intext_separator = "and"
            reflist_separator = "&"
            volume_issue_violations = ["Jones B (2019) Other. Journal (8:1)"]
            volume_issue_format = "comma"
        Output (printed):
            --- APA CITATION AUDIT REPORT ---

            1. Inline citations missing from the Reference list:
              - (Nguyen, 2025)

            2. References in the list with no corresponding inline citation:
              - Patel, R. (2021). Unused reference.

            3. Inline citations not matching the configured style (Smith, 2026):
              - (Jones 2024)

            4. References not in alphabetical order:
              - Jones, A. (2024). Another study.

            5. Inline citations not using the configured author separator ("and"):
              - (Smith & Jones 2020)

            6. References not using the configured author separator ("&"):
              - Brown C and Lee D (2019) ...

            7. References not using the configured volume/issue format ("comma"):
              - Jones B (2019) Other. Journal (8:1)
    """
    intext_separator_violations = intext_separator_violations or []
    reference_separator_violations = reference_separator_violations or []
    volume_issue_violations = volume_issue_violations or []
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

    print("\n4. References not in alphabetical order:")
    if order_violations:
        for ref in order_violations:
            print(f"  - {ref}")
    else:
        print("  None! The Reference list is in alphabetical order.")

    print(f"\n5. Inline citations not using the configured author separator "
          f"(\"{intext_separator}\"):")
    if intext_separator_violations:
        for ref in intext_separator_violations:
            print(f"  - ({ref})")
    else:
        print("  None! All inline citations consistently use the configured "
              "author separator.")

    print(f"\n6. References not using the configured author separator "
          f"(\"{reflist_separator}\"):")
    if reference_separator_violations:
        for ref in reference_separator_violations:
            print(f"  - {ref}")
    else:
        print("  None! All references consistently use the configured "
              "author separator.")

    print(f"\n7. References not using the configured volume/issue format "
          f"(\"{volume_issue_format}\"):")
    if volume_issue_violations:
        for ref in volume_issue_violations:
            print(f"  - {ref}")
    else:
        print("  None! All references consistently use the configured "
              "volume/issue format.")
