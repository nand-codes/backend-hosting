# FastAPI router for defining API routes
from fastapi import APIRouter

# Pydantic is used to validate request body
from pydantic import BaseModel

# Import embedding model service
from services.embedding_service import get_embedding_model

# Import vector database service
from services.vector_store import get_vector_store

# Used to call OpenRouter API
import requests

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create API router
router = APIRouter()


# Request schema for chat API
class ChatRequest(BaseModel):
    question: str


# Chat API endpoint
@router.post("/chat")
def chat(request: ChatRequest):

    # Extract user question
    question = request.question

    # Load embedding model
    embeddings = get_embedding_model()

    # Connect to vector database
    vector_db = get_vector_store(embeddings)

    # Retrieve top 3 relevant document chunks
    docs = vector_db.similarity_search(question, k=3)

    # Combine document chunks into context
    context = "\n\n".join([doc.page_content for doc in docs])

    # Construct prompt for the LLM
    prompt = f"""
You are an internal company assistant.

Answer the user's question using ONLY the context below.

If the answer is not present in the context, say:
"I could not find the answer in the company documents."

Context:
{context}

Question:
{question}

Answer:
"""

    # Get API key
    api_key = os.getenv("OPENROUTER_API_KEY")

    # OpenRouter endpoint
    url = "https://openrouter.ai/api/v1/chat/completions"

    # Headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Request payload
    data = {
        "model": "nvidia/nemotron-3-super-120b-a12b:free",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    # Call OpenRouter API
    response = requests.post(url, headers=headers, json=data)

    # Convert response to JSON
    result = response.json()

    # Extract answer
    answer = result["choices"][0]["message"]["content"]

    # Extract document sources
    sources = [doc.metadata.get("source", "unknown") for doc in docs]

    # Return final response
    return {
        "answer": answer,
        "sources": sources
    }