from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
import os


# ---------------------------------------
# PDF TEXT EXTRACTION
# ---------------------------------------

def extract_text(pdf_path):

    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


# ---------------------------------------
# CREATE TEXT CHUNKS
# ---------------------------------------

def create_chunks(text, chunk_size=500):

    words = text.split()

    chunks = []

    for i in range(0, len(words), chunk_size):

        chunk = " ".join(
            words[i:i + chunk_size]
        )

        if chunk.strip():
            chunks.append(chunk)

    return chunks


# ---------------------------------------
# EMBEDDING MODEL
# ---------------------------------------

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ---------------------------------------
# CHROMADB
# ---------------------------------------

client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = client.get_or_create_collection(
    name="placement_documents"
)


# ---------------------------------------
# PROCESS ALL PDF FILES
# ---------------------------------------

def process_pdfs():

    pdf_folder = "data"

    pdf_files = [
        file
        for file in os.listdir(pdf_folder)
        if file.lower().endswith(".pdf")
    ]

    for pdf_file in pdf_files:

        pdf_path = os.path.join(
            pdf_folder,
            pdf_file
        )

        print("Processing:", pdf_file)

        text = extract_text(pdf_path)

        if not text.strip():

            print(
                "No text found:",
                pdf_file
            )

            continue

        chunks = create_chunks(text)

        embeddings = embedding_model.encode(
            chunks
        ).tolist()

        ids = [
            f"{pdf_file}_{i}"
            for i in range(len(chunks))
        ]

        collection.upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=[
                {
                    "source": pdf_file
                }
                for _ in chunks
            ]
        )

    print("\nAll PDFs processed successfully!")


# ---------------------------------------
# CHECK COMPANY PDF
# ---------------------------------------

def company_pdf_exists(company):

    pdf_name = (
        company.strip().lower()
        + ".pdf"
    )

    pdf_path = os.path.join(
        "data",
        pdf_name
    )

    return os.path.exists(pdf_path)


# ---------------------------------------
# SEARCH ONLY SELECTED COMPANY
# ---------------------------------------

def search_company_documents(
    company,
    question,
    n_results=5
):

    pdf_name = (
        company.strip().lower()
        + ".pdf"
    )

    question_embedding = (
        embedding_model.encode(
            [question]
        ).tolist()
    )

    results = collection.query(
        query_embeddings=question_embedding,
        n_results=n_results,
        where={
            "source": pdf_name
        }
    )

    return results


# ---------------------------------------
# GET COMPLETE COMPANY DOCUMENT
# ---------------------------------------

def get_company_text(company):

    pdf_name = (
        company.strip().lower()
        + ".pdf"
    )

    pdf_path = os.path.join(
        "data",
        pdf_name
    )

    if not os.path.exists(pdf_path):
        return ""

    return extract_text(pdf_path)


# ---------------------------------------
# BUILD DATABASE
# ---------------------------------------

if __name__ == "__main__":

    process_pdfs()