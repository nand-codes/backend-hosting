from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from api.chat import router as chat_router
from api.upload import router as upload_router

load_dotenv()

app = FastAPI()

# allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register routes
app.include_router(chat_router)
app.include_router(upload_router)