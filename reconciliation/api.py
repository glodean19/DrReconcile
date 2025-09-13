"""
    RECONCILIATION SERVICE API
"""
from urllib.parse import parse_qs
import json
import pandas as pd
from sqlalchemy import text
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Query
from fastapi.responses import JSONResponse
from thefuzz import fuzz
from database.engine import get_engine
from .helper import (
    partial_ratio,
    cosine_similarity,
    get_token,
    query_icd11_api,
    remove_html_tags,
    sap_encode,
    encode
)


router = APIRouter()

engine = get_engine()


@router.get("/reconcile")
async def get_manifest():
    """
    The function is a GET route handler for the /reconcile endpoint, 
    and it returns a reconciliation manifest as a JSON response. 
    This manifest is a structured object that provides metadata about 
    the reconciliation service, including its version (0.2), 
    name (DrReconcile Reconciliation Service), and 
    namespaces for identifiers and schema (identifierSpace and schemaSpace). 
    It also defines how entities can be viewed (view) and previewed (preview) 
    by specifying URL templates, width, and height. The defaultTypes field lists 
    the entity types that the service can reconcile, 
    in this case, Ethnicity, Sexual Orientation and Diagnosis. 
    The manifest is essential for OpenRefine to understand 
    how to interact with the reconciliation service, 
    therefore it must be returned.
    """
    manifest = {
        "versions": ["0.2"],
        "name": "DrReconcile Reconciliation Service",
        "identifierSpace": "http://127.0.0.1:8000/api/reconcile",
        "schemaSpace": "http://127.0.0.1:8000/api/reconcile",
        "view": {
            "url": "http://127.0.0.1:8000/api/view/{{id}}"
        },
        "preview": {
            "url": "http://127.0.0.1:8000/api/view/{{id}}",
            "width": 300,
            "height": 200
        },
        "defaultTypes": [
            {"id": "/ethnicity", "name": "Ethnicity"},
            {"id": "/sexual-orientation", "name": "Sexual Orientation"},
            {"id": "/icd11", "name": "Diagnosis"}
        ]
    }

    return JSONResponse(content=manifest)

@router.post("/reconcile")
async def reconcile(request: Request):
    """
    The function is a POST route handler for the /reconcile endpoint. 
    It extracts the queries parameter from the request body, 
    which is expected to be form-encoded and containing JSON data. 
    The payload is parsed into a dictionary, and for each query, 
    it searches for matching records in the ethnicity, 
    sexual_orientation tables and ICD-11 API. 
    For each match, it constructs a response object containing 
    the id, name, score, match status, and type metadata. 
    The response is then structured as a dictionary of query results and 
    returned as a JSON response. If any error occurs during processing,
    it raises an exception.
    """
    try:
        # Decode and parse the request body sent by OpenRefine
        raw_body = await request.body()
        # it converts the raw bytes to UTF-8 string
        decoded_body = raw_body.decode("utf-8")
        # it decodes the form-encoded query string (like in a browser)
        # This is necessary because OpenRefine sends the requests
        # as application/x-www-form-urlencoded, not application/json.
        parsed_data = parse_qs(decoded_body)

        # errors are when queries re not found in the form data
        # when it fails to parse a JSON string so the payload is malformed
        # when the resulting dictionary is empty
        if "queries" not in parsed_data:
            raise HTTPException(status_code=400, detail="Missing 'queries' parameter.")

        try:
            # queries values is a JSON string
            payload = json.loads(parsed_data["queries"][0])
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400,
                                detail="Malformed JSON in request payload.") from e

        if not payload:
            raise HTTPException(status_code=400,
                                detail="Empty payload. Please provide a valid query.")

        response = {}

        with engine.connect() as conn:
            for key, q in payload.items():
                # this is the string to reconcile
                query_string = q.get("query", "").strip()
                # matches to return are limited to 5
                limit = q.get("limit", 5)
                # type to search between ethnicity and sexual orientation
                type_param = q.get("type")
                matches = []

                # If type is specified as '/ethnicity', only search ethnicity
                if type_param == "/ethnicity" or not type_param:
                    ethnicity_query = conn.execute(
                        text("SELECT ethnicityid, description FROM ethnicity")
                    ).fetchall()

                    for row in ethnicity_query:
                        ethnicity_id = row[0]
                        description = row[1]
                        # Calculates similarity score with each entry
                        score = partial_ratio(query_string, description)
                        matches.append({
                            "id": f"/ethnicity/{ethnicity_id}",
                            "name": description,
                            "score": score,
                            "match": score >= 90,
                            "type": [{"id": "/ethnicity", "name": "Ethnicity"}]
                        })

                # If type is specified as '/sexual-orientation', only search sexual_orientation
                if type_param == "/sexual-orientation" or not type_param:
                    so_query = conn.execute(
                        text("SELECT soid, soname FROM sexual_orientation")
                    ).fetchall()

                    for row in so_query:
                        so_id = row[0]
                        soname = row[1]

                        # Normalize candidate labels:
                        # Lowercase
                        # Remove parentheses
                        # Split on “or” and treat as multiple aliases
                        # (e.g., “Gay or Lesbian” becomes ["Gay", "Lesbian"])

                        # Normalize and clean the soname string
                        clean_soname = soname.lower().replace("(", "").replace(")", "")
                        # Split and strip each alias
                        aliases = [a.strip() for a in clean_soname.split("or")]
                        # Lowercase the query once
                        query_encoded = encode(query_string.lower())
                        # Compute similarity scores for each alias
                        scores = [
                            cosine_similarity(query_encoded, encode(alias))
                            for alias in aliases
                        ]
                        max_score = max(scores)
                        # Semantic similarity
                        semantic_score = max_score * 100

                        # Lexical similarity
                        lexical_score = partial_ratio(query_string, soname)

                        # Match if either score is above threshold
                        is_match = bool(semantic_score >= 90 or lexical_score >= 90)

                        matches.append({
                            "id": f"/sexual-orientation/{so_id}",
                            "name": soname,
                            "semantic_score": round(semantic_score, 2),
                            "lexical_score": lexical_score,
                            "score": max(semantic_score, lexical_score),
                            "match": is_match,
                            "type": [{"id": "/sexual-orientation", "name": "Sexual Orientation"}]
                        })

                # If type is specified as '/icd-11', only search diagnosis
                if type_param == "/icd11" or not type_param:
                    # get the token
                    access_token = get_token()
                    # query the ICD-11 API
                    icd_results = query_icd11_api(query_string, access_token, limit)

                    # for each term in the list
                    for entity in icd_results:
                        # Extract the unique ICD identifier for the entity
                        icd_id = entity.get("id", None)
                        # Extract and clean the title by removing any HTML tags
                        title = remove_html_tags(entity.get("title", ""))
                        # Calculate the similarity score between the query string and the ICD title
                        # Semantic similarity
                        sap_query_vec = sap_encode(query_string)
                        sap_title_vec = sap_encode(title)
                        sap_score = cosine_similarity(sap_query_vec, sap_title_vec) * 100

                        sbert_query_vec = encode(query_string)
                        sbert_title_vec = encode(title)
                        sbert_score = cosine_similarity(sbert_query_vec, sbert_title_vec) * 100

                        # Combine scores
                        semantic_score = max(sap_score, sbert_score)
                        #semantic_score = sap_score
                        #semantic_score = sbert_score

                        # Lexical similarity
                        lexical_score = fuzz.partial_ratio(query_string, title)

                        # Match logic
                        is_match = bool(semantic_score >= 90 or lexical_score >= 90)
                        #is_match = bool(lexical_score >= 90)

                        matches.append({
                            "id": icd_id,
                            "name": title,
                            "semantic_score": round(semantic_score, 2),
                            "lexical_score": lexical_score,
                            #"score": lexical_score,
                            "score": max(semantic_score, lexical_score),
                            "match": is_match,
                            "type": [{"id": "/icd11", "name": "Diagnosis"}]
                        })

                # Sort matches by score in descending order and limit results
                matches = sorted(matches, key=lambda x: x["score"], reverse=True)[:limit]

                response[key] = {
                    "result": matches
                }

        return JSONResponse(content=response)

    except Exception as e:
        print(f"Reconciliation Error: {e}")
        raise HTTPException(status_code=500,
                            detail=f"Error performing reconciliation: {str(e)}") from e

@router.post("/fetch-update-reconciled-data")
# endpoint parameters: uploading file and selecting the type_param
async def fetch_update_reconciled_data(
    file: UploadFile = File(...),
    type_param: str = Query(..., description="This is the GET id")
):
    """
       This endpoint handles a CSV file upload to update the database with reconciled values.
       The uploaded file is read as DataFrame and for each row, the script extracts the 
       patientid and the corresponding column value. Depending on the table, it updates 
       specific attributes and append the results.
    """
    try:
        df = pd.read_csv(file.file)

        # Determine the column and table to update
        match type_param:
            case "/ethnicity":
                column_name = "ethnicity"
                table = "patient"
            case "/sexual-orientation":
                column_name = "sexual_orientation"
                table = "patient"
            case "/icd11":
                column_name = "reason_for_admission"
                table = "registration"
            case _:
                raise HTTPException(status_code=400, detail=f"Unsupported type: {type_param}")

        updated_rows = []

        # Iterate through the DataFrame and run updates
        with engine.begin() as conn:
            for _, row in df.iterrows():
                patientid = row.get("patientid")
                value = row.get(column_name)

                # skip missing values
                if pd.isna(patientid) or pd.isna(value):
                    continue

                # for each table a different update query
                if table == "patient":
                    conn.execute(
                        text(f"""
                            UPDATE patient
                            SET {column_name} = :value
                            WHERE patientid = :patientid
                        """),
                        {"value": value, "patientid": patientid}
                    )
                elif table == "registration":
                    conn.execute(
                        text("""
                            UPDATE registration
                            SET reason_for_admission = :value
                            WHERE patientid = :patientid
                        """),
                        {"value": value, "patientid": patientid}
                    )
                # updated rows will list in the Swagger UI
                updated_rows.append({
                    "patientid": patientid,
                    "updated_field": column_name,
                    "new_value": value
                })

        return {"status": "success", "updated_rows": updated_rows}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update database: {str(e)}") from e
