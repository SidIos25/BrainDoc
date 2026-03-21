import os
import tempfile
from typing import List, Tuple

from pypdf.errors import PdfReadError
from langchain_community.document_loaders import (
    PyPDFLoader,
    PDFPlumberLoader,
    PyMuPDFLoader,
    TextLoader,
    Docx2txtLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_documents(uploaded_files) -> Tuple[List, List[str]]:
    all_docs = []
    load_errors = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)

    for uploaded_file in uploaded_files:
        suffix = os.path.splitext(uploaded_file.name)[1].lower()
        tmp_path = None

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name

            if suffix == ".pdf":
                docs = []

                # Attempt 1: PyPDFLoader
                try:
                    docs = splitter.split_documents(PyPDFLoader(tmp_path).load())
                except PdfReadError as exc:
                    load_errors.append(f"{uploaded_file.name}: could not read PDF ({exc})")

                # Attempt 2: PDFPlumberLoader
                if not docs:
                    try:
                        docs = splitter.split_documents(PDFPlumberLoader(tmp_path).load())
                    except Exception:
                        pass

                # Attempt 3: PyMuPDFLoader
                if not docs:
                    try:
                        docs = splitter.split_documents(PyMuPDFLoader(tmp_path).load())
                    except Exception:
                        pass

                if not docs:
                    load_errors.append(
                        f"{uploaded_file.name}: no readable text found; PDF may be scanned/image-only"
                    )
                    continue

            elif suffix == ".docx":
                pages = Docx2txtLoader(tmp_path).load()
                docs = splitter.split_documents(pages)
            elif suffix == ".txt":
                pages = TextLoader(tmp_path, autodetect_encoding=True).load()
                docs = splitter.split_documents(pages)
            else:
                load_errors.append(f"Unsupported file type for {uploaded_file.name}")
                continue

            if not docs:
                load_errors.append(f"{uploaded_file.name}: no readable content found")
                continue

            # Use original uploaded filename instead of temporary paths in metadata.
            for doc in docs:
                doc.metadata["source"] = uploaded_file.name

            all_docs.extend(docs)
        except PdfReadError as exc:
            load_errors.append(f"{uploaded_file.name}: could not read PDF ({exc})")
        except Exception as exc:  # keep user-facing failures visible without crashing
            load_errors.append(f"{uploaded_file.name}: {exc}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    load_errors.append(f"Could not remove temp file for {uploaded_file.name}")

    return all_docs, load_errors
