from fastapi import APIRouter, UploadFile, File
import os
import shutil

from services.embedding_service import get_embedding_model
from services.vector_store import get_vector_store
from utils.document_loader import load_document
from utils.text_splitter import split_documents

router = APIRouter()

UPLOAD_DIR = "documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    documents = load_document(file_path)

    chunks = split_documents(documents)

    embeddings = get_embedding_model()

    vector_db = get_vector_store(embeddings)

    vector_db.add_documents(chunks)

    vector_db.persist()

    return {
        "message": "Document uploaded and indexed successfully",
        "filename": file.filename,
        "chunks_created": len(chunks)
    }