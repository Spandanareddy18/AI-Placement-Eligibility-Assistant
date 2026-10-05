import re


# ==========================================
# EXTRACT CGPA
# ==========================================

def extract_cgpa(text):

    patterns = [
        r"Minimum\s+CGPA\s*[:\-]?\s*(\d+(?:\.\d+)?)",
        r"minimum\s+(?:CGPA|cgpa)\s*(?:of|:|-)?\s*(\d+(?:\.\d+)?)",
        r"CGPA\s*(?:of|:|-)?\s*(\d+(?:\.\d+)?)\s*(?:or above|and above|\+)?"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return float(match.group(1))

    return None


# ==========================================
# EXTRACT BRANCHES
# ==========================================

def extract_branches(text):

    match = re.search(
        r"Eligible\s+Branches\s*[:\-]?\s*(.*?)(?=\s+\d+\.\s|\s+Academic\s+Year|\s+Backlogs|\s+Location|$)",
        text,
        re.IGNORECASE
    )

    if not match:
        return []

    branch_text = match.group(1).strip()

    branches = [
        branch.strip().upper()
        for branch in branch_text.split(",")
        if branch.strip()
    ]

    return branches


# ==========================================
# EXTRACT BACKLOG REQUIREMENT
# ==========================================

def extract_backlog_requirement(text):

    lower_text = text.lower()

    if "no active backlogs" in lower_text:
        return 0

    if "no backlogs" in lower_text:
        return 0

    patterns = [
        r"maximum\s+backlogs?\s*[:\-]?\s*(\d+)",
        r"backlogs?\s*[:\-]?\s*(\d+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return int(match.group(1))

    return None


# ==========================================
# EXTRACT ACADEMIC YEAR
# ==========================================

def extract_year_requirement(text):

    match = re.search(
        r"Academic\s+Year\s*[:\-]?\s*(.*?)(?=\s+\d+\.\s|\s+Backlogs|\s+Location|$)",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    return None


# ==========================================
# CHECK BRANCH
# ==========================================

def check_branch(
    student_branch,
    allowed_branches
):

    if not allowed_branches:
        return None

    student_branch = student_branch.strip().upper()

    return student_branch in allowed_branches


# ==========================================
# CHECK YEAR
# ==========================================

def check_year(
    student_year,
    requirement
):

    if not requirement:
        return None

    requirement = requirement.lower()
    student_year = student_year.lower()

    if (
        "final-year" in requirement
        or "final year" in requirement
        or "4th year" in requirement
    ):
        return student_year == "4th year"

    if (
        "3rd year" in requirement
        and "4th year" in requirement
    ):
        return student_year in [
            "3rd year",
            "4th year"
        ]

    if "3rd year" in requirement:
        return student_year == "3rd year"

    return None


# ==========================================
# MAIN ELIGIBILITY FUNCTION
# ==========================================

def check_eligibility(
    student_cgpa,
    student_branch,
    student_year,
    student_backlogs,
    placement_text
):

    required_cgpa = extract_cgpa(
        placement_text
    )

    allowed_branches = extract_branches(
        placement_text
    )

    required_backlogs = extract_backlog_requirement(
        placement_text
    )

    year_requirement = extract_year_requirement(
        placement_text
    )


    # ------------------------------------------
    # CGPA CHECK
    # ------------------------------------------

    if required_cgpa is not None:

        cgpa_status = (
            student_cgpa >= required_cgpa
        )

    else:

        cgpa_status = None


    # ------------------------------------------
    # BRANCH CHECK
    # ------------------------------------------

    branch_status = check_branch(
        student_branch,
        allowed_branches
    )


    # ------------------------------------------
    # BACKLOG CHECK
    # ------------------------------------------

    if required_backlogs is not None:

        backlog_status = (
            student_backlogs <= required_backlogs
        )

    else:

        backlog_status = None


    # ------------------------------------------
    # YEAR CHECK
    # ------------------------------------------

    year_status = check_year(
        student_year,
        year_requirement
    )


    # ------------------------------------------
    # OVERALL RESULT
    # ------------------------------------------

    checks = [
        cgpa_status,
        branch_status,
        backlog_status,
        year_status
    ]

    known_checks = [
        check
        for check in checks
        if check is not None
    ]


    if known_checks and all(known_checks):

        overall = True

    elif any(
        check is False
        for check in known_checks
    ):

        overall = False

    else:

        overall = None


    # ==========================================
    # VERY IMPORTANT:
    # RETURN A DICTIONARY
    # ==========================================

    return {
        "required_cgpa": required_cgpa,
        "allowed_branches": allowed_branches,
        "required_backlogs": required_backlogs,
        "year_requirement": year_requirement,
        "cgpa_status": cgpa_status,
        "branch_status": branch_status,
        "backlog_status": backlog_status,
        "year_status": year_status,
        "overall": overall
    }