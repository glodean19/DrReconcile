"""
    MAIN
    Setup basic web API using FastAPI deployed on the uvicorn server and
    applies CORS middleware to allow cross-origin requests from 
    http://127.0.0.1:3333
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from reconciliation.api import router as reconciliation_router

app = FastAPI(title="DrReconcile API", version="1.0.0")

# Add CORS middleware
# https://fastapi.tiangolo.com/tutorial/cors/#use-corsmiddleware
app.add_middleware(
    CORSMiddleware,
    # Allow requests from OpenRefine
    allow_origins=["http://127.0.0.1:3333"],
    allow_credentials=True,
    # Allow all HTTP methods
    allow_methods=["*"],
    # Allow all headers
    allow_headers=["*"],
)

# Include the reconciliation routes
app.include_router(reconciliation_router, prefix="/api",
                   tags=["Reconciliation"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
