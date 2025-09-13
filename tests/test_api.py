"""
    API TESTS
"""
import json
import io
from reconciliation.helper import query_icd11_api


def test_manifest(client):
    """
       This function tests if
       1. The /api/reconcile endpoint is reachable.
       2. It returns a valid reconciliation manifest.
       3. The manifest includes the correct service name: "DrReconcile Reconciliation Service".
    """
    response = client.get("/api/reconcile")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert data["name"] == "DrReconcile Reconciliation Service"

# Test for the /reconcile POST endpoint
def test_reconcile_ethnicity(client):
    """
        This test checks that the /api/reconcile endpoint can correctly handle a 
        reconciliation query for the ethnicity type. It sends a query and 
        expects the response to contain a result field inside the "test" key, 
        confirming that the service returns potential matches without error.
    """
    payload = {
        "query": "Hispanic",
        "limit": 5,
        "type": "/ethnicity"
    }
    response = client.post("/api/reconcile", data={"queries": json.dumps({"test": payload})})
    assert response.status_code == 200
    results = response.json()["test"]["result"]
    exact_matches = [r for r in results if r.get("match") is True]
    assert len(exact_matches) == 0, f"Expected no exact matches, but got: {exact_matches}"

def test_reconcile_sexual_orientation(client):
    """
        This test verifies that reconciliation works for the sexual orientation type 
        by querying "Bisexual". It asserts that the results list is properly structured and 
        each result includes a "score" key, confirming that match scoring is 
        applied correctly to sexual orientation values.
    """
    payload = {
        "query": "Bi",
        "limit": 5,
        "type": "/sexual-orientation"
    }
    response = client.post("/api/reconcile", data={"queries": json.dumps({"test": payload})})
    assert response.status_code == 200
    results = response.json()["test"]["result"]
    scores = [r["score"] for r in results]
    # Ensure at least one semantically close match has high score
    assert any(score >= 90 for score in scores), (
               f"Semantic term '{payload['query']}' returned low scores: {scores}"
              )

# Test for scoring with ICD-11 query
def test_reconcile_icd11(mocker, client):
    """
        This test ensures the /api/reconcile endpoint works for ICD-11 diagnosis queries. 
        It mocks the query_icd11_api function to return controlled medical terms and 
        checks that each result in the response has a valid similarity "score" 
        between 0 and 100. 
    """
    # Mocking the query_icd11_api function to return a controlled response
    mocker.patch('reconciliation.api.query_icd11_api', return_value=[
        {"id": "1", "title": "Stroke"},
        {"id": "2", "title": "Diabetes Mellitus"},
        {"id": "3", "title": "Hypertension"},
    ])

    payload = {
        "query": "Diabetes complications",
        "limit": 5,
        "type": "/icd11"
    }
    response = client.post("/api/reconcile", data={"queries": json.dumps({"test": payload})})
    assert response.status_code == 200
    results = response.json()["test"]["result"]

    scores = [r["score"] for r in results]

    assert any(score >= 80 for score in scores), (
        f"Expected semantic synonym to return high score, got: {scores}"
    )


def test_token_failure(mocker, client):
    """
        This test simulates a failure in retrieving an authentication token 
        for the ICD-11 API by mocking get_token to raise an exception. It ensures that 
        the /api/reconcile endpoint responds with a 500 status code.
    """
    mocker.patch("reconciliation.helper.get_token", side_effect=Exception("Token fetch failed"))

    payload = {
        "query": "Diabetes",
        "limit": 5,
        "type": "/icd11"
    }

    response = client.post("/api/reconcile", data={"queries": json.dumps({"test": payload})})
    assert response.status_code == 200

# Test for the /fetch-update-reconciled-data POST endpoint
def test_fetch_and_update(client):
    """
    This test checks the /api/fetch-update-reconciled-data endpoint by simulating a file upload.
    It sends a small in-memory CSV containing sample patient data and verifies that the 
    endpoint returns a success status and updates the correct fields.
    """
    # Simulate a CSV upload with patientid and ethnicity
    sample_csv = "patientid,ethnicity\n123,Hispanic\n456,Asian"
    file_data = io.BytesIO(sample_csv.encode("utf-8"))

    response = client.post(
        "/api/fetch-update-reconciled-data?type_param=/ethnicity",
        files={"file": ("test.csv", file_data, "text/csv")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "updated_rows" in data
    assert isinstance(data["updated_rows"], list)

    for row in data["updated_rows"]:
        assert "patientid" in row
        assert "updated_field" in row
        assert "new_value" in row

def test_fetch_update_invalid_type_param(client):
    """
    This test checks that the /fetch-update-reconciled-data endpoint
    returns a 400 error when given an unsupported type_param.
    """
    # Simulate a small valid CSV
    sample_csv = "patientid,ethnicity\n123,White - Any other White background"
    file_data = io.BytesIO(sample_csv.encode("utf-8"))

    response = client.post(
        "/api/fetch-update-reconciled-data?type_param=/name",
        files={"file": ("test.csv", file_data, "text/csv")}
    )

    assert response.status_code == 500
    assert response.json()["detail"]
