"""
    CONFIGURATION
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from reconciliation.api import router

@pytest.fixture(scope="module")
def client():
    """
        This function setup the configuration for testing the API
    """
    app = FastAPI()
    app.include_router(router, prefix="/api")
    return TestClient(app)
