import streamlit as st
import ollama
import os

from rag import (
    search_company_documents,
    company_pdf_exists,
    get_company_text
)

from eligibility import check_eligibility


# ---------------------------------------
# PAGE SETTINGS
# ---------------------------------------

st.set_page_config(
    page_title="AI-Based Placement Eligibility Assistant",
    page_icon="🎓",
    layout="centered"
)


# ---------------------------------------
# TITLE
# ---------------------------------------

st.title(
    "🎓 AI-Based Placement Eligibility Assistant"
)

st.write(
    "Check your placement eligibility using company placement documents."
)


# ---------------------------------------
# FIND PDF COMPANIES
# ---------------------------------------

pdf_files = [
    file
    for file in os.listdir("data")
    if file.lower().endswith(".pdf")
]

companies = [
    os.path.splitext(file)[0].title()
    for file in pdf_files
]


if not companies:

    st.error(
        "No placement PDFs found in the data folder."
    )

    st.stop()


# ---------------------------------------
# COMPANY SELECTION
# ---------------------------------------

st.header("🏢 Select Company")

selected_company = st.selectbox(
    "Choose the company",
    sorted(companies)
)


# ---------------------------------------
# STUDENT DETAILS
# ---------------------------------------

st.header("👩‍🎓 Student Details")


cgpa = st.number_input(
    "CGPA",
    min_value=0.0,
    max_value=10.0,
    value=8.0,
    step=0.1
)


branch = st.selectbox(
    "Branch",
    [
        "CSE",
        "IT",
        "ECE",
        "EEE",
        "Mechanical",
        "Civil"
    ]
)


year = st.selectbox(
    "Year",
    [
        "1st Year",
        "2nd Year",
        "3rd Year",
        "4th Year"
    ]
)


backlogs = st.number_input(
    "Number of Backlogs",
    min_value=0,
    value=0,
    step=1
)


# ---------------------------------------
# ELIGIBILITY CHECK
# ---------------------------------------

st.header("✅ Eligibility Check")


if st.button("Check My Eligibility"):

    company_text = get_company_text(
        selected_company
    )


    if not company_text:

        st.error(
            f"No placement document found for {selected_company}."
        )

    else:

        result = check_eligibility(
            cgpa,
            branch,
            year,
            backlogs,
            company_text
        )


        st.subheader(
            f"📊 {selected_company} Eligibility"
        )


        # --------------------------------
        # CGPA
        # --------------------------------

        st.write("### CGPA")

        if result["required_cgpa"] is not None:

            st.write(
                f"Required: {result['required_cgpa']}"
            )

            st.write(
                f"Your CGPA: {cgpa}"
            )

            if result["cgpa_status"]:
                st.success("✅ CGPA requirement satisfied")
            else:
                st.error("❌ CGPA requirement not satisfied")

        else:

            st.warning(
                "⚠️ CGPA requirement is not mentioned."
            )


        # --------------------------------
        # BRANCH
        # --------------------------------

        st.write("### Branch")

        if result["allowed_branches"]:

            st.write(
                "Eligible Branches: "
                + ", ".join(
                    result["allowed_branches"]
                )
            )

            st.write(
                f"Your Branch: {branch}"
            )

            if result["branch_status"]:
                st.success(
                    "✅ Branch requirement satisfied"
                )
            else:
                st.error(
                    "❌ Branch requirement not satisfied"
                )

        else:

            st.warning(
                "⚠️ Branch requirement is not mentioned."
            )


        # --------------------------------
        # BACKLOGS
        # --------------------------------

        st.write("### Backlogs")

        if result["required_backlogs"] is not None:

            if result["required_backlogs"] == 0:

                st.write(
                    "Required: No active backlogs"
                )

            else:

                st.write(
                    f"Maximum allowed: "
                    f"{result['required_backlogs']}"
                )

            st.write(
                f"Your Backlogs: {backlogs}"
            )

            if result["backlog_status"]:
                st.success(
                    "✅ Backlog requirement satisfied"
                )
            else:
                st.error(
                    "❌ Backlog requirement not satisfied"
                )

        else:

            st.warning(
                "⚠️ Backlog requirement is not mentioned."
            )


        # --------------------------------
        # YEAR
        # --------------------------------

        st.write("### Academic Year")

        if result["year_requirement"]:

            st.write(
                "Requirement: "
                + result["year_requirement"]
            )

            st.write(
                f"Your Year: {year}"
            )

            if result["year_status"] is True:

                st.success(
                    "✅ Academic year requirement satisfied"
                )

            elif result["year_status"] is False:

                st.error(
                    "❌ Academic year requirement not satisfied"
                )

            else:

                st.warning(
                    "⚠️ Academic year could not be determined."
                )

        else:

            st.warning(
                "⚠️ Academic year requirement is not mentioned."
            )


        # --------------------------------
        # OVERALL RESULT
        # --------------------------------

        st.divider()

        st.subheader("🎯 Overall Result")


        if result["overall"] is True:

            st.success(
                f"🎉 You appear to be ELIGIBLE for "
                f"{selected_company} based on the uploaded document."
            )


        elif result["overall"] is False:

            st.error(
                f"❌ You do NOT meet all the listed "
                f"eligibility requirements for {selected_company}."
            )


        else:

            st.warning(
                "⚠️ Eligibility could not be completely "
                "determined because some requirements are missing."
            )


        st.caption(
            f"📄 Source: {selected_company.lower()}.pdf"
        )


# ---------------------------------------
# ASK AI QUESTION
# ---------------------------------------

st.divider()

st.header("💬 Ask About This Company")


question = st.text_input(
    "Your question",
    placeholder="What is the minimum CGPA?"
)


if st.button("Ask AI"):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        results = search_company_documents(
            selected_company,
            question
        )


        documents = results.get(
            "documents",
            [[]]
        )[0]


        if not documents:

            st.warning(
                "The answer is not mentioned in "
                f"the {selected_company} placement document."
            )

        else:

            context = "\n\n".join(
                documents
            )


            prompt = f"""
You are an AI-Based Placement Eligibility Assistant.

Selected company:
{selected_company}

Answer ONLY using the uploaded
{selected_company} placement document.

Never use information from another company.

Student details:

CGPA: {cgpa}
Branch: {branch}
Year: {year}
Backlogs: {backlogs}

Question:
{question}

Document information:
{context}

Rules:

1. Do not invent information.
2. Do not use outside knowledge.
3. If the information is missing, say it is not mentioned.
4. Keep the answer simple and clear.
"""


            with st.spinner(
                "Generating answer..."
            ):

                response = ollama.chat(
                    model="llama3.2",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )


            st.subheader(
                "🤖 AI Response"
            )

            st.write(
                response[
                    "message"
                ][
                    "content"
                ]
            )


            st.caption(
                f"📄 Source: {selected_company.lower()}.pdf"
            )