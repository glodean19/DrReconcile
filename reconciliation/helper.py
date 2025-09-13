"""
    HELPER FUNCTIONS
"""
import re
import requests
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
import torch
import numpy as np



# Semantic similarity
# SapBERT model  https://github.com/cambridgeltl/sapbert
# more ontological than descriptive pre-trained model
MODEL_NAME = "cambridgeltl/SapBERT-from-PubMedBERT-fulltext"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
sap_model = AutoModel.from_pretrained(MODEL_NAME)

def sap_encode(text):
    """
        This function loads the SapBERT model, a BERT-based language model 
        pre-trained on biomedical text from PubMed, using Hugging Face's Transformers library. 
        It first initializes the tokenizer and model using the model name 
        "cambridgeltl/SapBERT-from-PubMedBERT-fulltext". It takes a text string as input, 
        tokenizes and encodes it into model-compatible tensors, 
        then runs the text through the model in inference mode. 
        It extracts the embedding vector corresponding to the special [CLS] token (the first token),
        which serves as a summary representation of the input text. 
        It converts this embedding from a PyTorch tensor 
        to a NumPy array for computing semantic similarity.
    """
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = sap_model(**inputs)
        embeddings = outputs.last_hidden_state[:, 0, :]
        return embeddings[0].cpu().numpy()

# SBERT model https://huggingface.co/sentence-transformers/all-mpnet-base-v2
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

def encode(text):
    """
        This function initialises a SentenceTransformer model using 
        the pretrained 'all-mpnet-base-v2'from the Sentence Transformers library, 
        which is designed to generate meaningful sentence embeddings 
        for general language tasks. The encode function takes a text string as input and 
        passes it to the model's encode method, which converts the text into a fixed-size vector. 
        The output embedding is returned as a NumPy array.
    """
    return model.encode(text, convert_to_numpy=True)

def cosine_similarity(a, b):
    """
        This function calculates the cosine similarity between two vectors a and b. 
        The cosine similarity measures how similar two vectors are 
        by finding the cosine of the angle between them. It's computed as 
        the dot product of a and b divided by the product of their magnitudes. The result 
        ranges from -1 to 1, where 1 means the vectors point 
        in the same direction (high similarity), 
        0 means they are orthogonal (no similarity), 
        and -1 means they point in opposite directions.
    """
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Lexical similarity
def levenshtein(s1, s2):
    """
        The Levenshtein distance between two strings is 
        the minimum number of single-character edits 
        (insertions, deletions, or substitutions) 
        required to change one string into the other.
    """
    #  the function always makes s1 the longer string
    if len(s1) < len(s2):
        # pylint: disable=arguments-out-of-order
        return levenshtein(s2, s1)

    # If the second string is empty, the distance is just the length of the first
    if len(s2) == 0:
        return len(s1)

    # This sets up the base case: converting an empty string to s2 one character at a time.
    # Example: s2 = "cat" → [0, 1, 2, 3] (0 edits to go from "" to "", 1 to "c", 2 to "ca", etc.)
    previous_row = list(range(len(s2) + 1))

    for i, c1 in enumerate(s1):
        # Each row compares c1 from s1 to every character c2 in s2
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # add c2 into s1
            insert = previous_row[j + 1] + 1
            # remove c1 from s1
            delete = current_row[j] + 1
            #if c1 != c2, change one into the other
            replace = previous_row[j] + (0 if c1 == c2 else 1)
            # pick the least expensive operation and store it
            current_row.append(min(insert, delete, replace))
        # set the current row as the new "previous" one
        previous_row = current_row
    # After going through all characters,
    # the last value in the final row is
    # the Levenshtein distance between s1 and s2
    return previous_row[-1]

def generality_boost(candidate: str, term: str) -> float:
    """
        This function adds or subtracts a boost to a similarity score 
        based on how generic the match is.
    """

    # If the candidate contains "any {term}" or "other {term}"
    # then this is treated as very generic and the score is up by +5.0
    if f"any {term}" in candidate or f"other {term}" in candidate:
        return 5.0
    # if the term appear somewhere in the candidate, but not in a generic form,
    # then no boost is applied
    if term in candidate:
        return 0.0
    #  If the term doesn't appear in the candidate at all, this is a worse match,
    # so a penalty of -5.0 is applied to make it rank lower
    return -5.0

def null_equivalence_score(term: str, candidate: str) -> float:
    """
        It checks whether both the term and candidate represent a "null-like" or "no data" value,
        If both do, it returns a perfect match score of 100,
        even if they're different phrases.
    """
    null_terms = {
        "none", "n/a", "not applicable", "not answered", "not stated", "prefer not to say",
        "unknown", "don't know", "does not apply", "null", "missing", "no answer"
    }

    # Exact or near match within null expressions
    if term in null_terms and candidate in null_terms:
        # Considered semantically identical
        return 100.0
    # If either string is not in the set, it returns 0.0,
    # meaning they’re not considered null-equivalent
    return 0.0

def partial_ratio(s1: str, s2: str) -> int:
    """
        It tries to find the part of the longer string that 
        best matches the shorter string, even if they aren't aligned. It answers:
        What's the best similarity score I can get if 
        I match the shorter string to any part of the longer one?
    """

     # Lower case and normalising
    s1, s2 = s1.strip().lower(), s2.strip().lower()

    # Returns 0 similarity if either string is empty
    if not s1 or not s2:
        return 0

    # Handle null-like equivalence
    semantic_score = null_equivalence_score(s1, s2)
    if semantic_score == 100.0:
        return 100

    # slide the shorter string over the longer one to find the best substring match
    shorter, longer = (s1, s2) if len(s1) <= len(s2) else (s2, s1)
    # keep track of the maximum similarity score
    len_short = len(shorter)
    max_score = 0

    # This slides a window of the same length as the shorter string across the longer string
    for i in range(len(longer) - len_short + 1):
        substring = longer[i : i + len_short]
        # Calculate the Levenshtein distance between the shorter string and the current substring
        distance = levenshtein(shorter, substring)
        # Convert it into a percentage
        ratio = 100 * (len_short - distance) / len_short
        # If it's a perfect match, apply position-based decay
        if distance == 0:
            # Scale down based on how far into the string the match starts
            # Decay factor: every character into the string drops score slightly
            decay = (i / len(longer)) * 30
            base_score = 100 - decay
        else:
            base_score = ratio

        # It adds the boost to the base score
        base_score += generality_boost(longer, shorter)
        # Keeps track of the highest score encountered across all substring positions
        # Is the current score better than my best so far? If yes, update it.
        # The base_score gets compared against all previous scores and
        # the highest becomes the new max_score
        max_score = max(max_score, base_score)
    # Return the best match score, rounded to an integer between 0 and 100
    return int(round(max_score))

# ICD-11 API
def query_icd11_api(search_term: str, access_token: str, limit: int = 5):
    """
        This function uses the API reference has shown in the Open-API(swagger)
        documentation: https://id.who.int/swagger/index.html
        It sends an HTTP GET request to the WHO ICD-11 entity search endpoint, 
        passing the access token in the request headers for authentication and 
        specifying the search term as a query parameter. The function sets headers 
        to request a JSON response in English and specify the API version to use. 
        If the API call is successful (HTTP 200), it retrieves the list of matching disease 
        entities from the destinationEntities field in the JSON response, 
        limits the number to 5. If the request fails, it raises a ValueError 
        with the status code and error message for debugging.
    """
    url = "https://id.who.int/icd/entity/search"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Accept-Language": "en",
        "API-Version": "v2"
    }
    params = {"q": search_term}

    response = requests.get(url, headers=headers, params=params, timeout=10)

    if response.status_code != 200:
        raise ValueError(f"ICD-11 API error {response.status_code}: {response.text}")

    results = response.json().get("destinationEntities", [])[:limit]
    return results

def get_token():
    """
        This function sets up the ICD API authentication. It gets
        the access token using the OAuth 2.0 client credentials. 
        It sends a POST request with the client_id, client_secret, 
        and scope (icdapi_access). If the request is successful (HTTP 200), 
        it extracts and returns the access token from the JSON response.
        If the token request fails, the function raises an error 
        showing the response status and message.
        Reference: https://github.com/ICD-API/Python-samples/blob/master/sample.py
    """
    token_url = "https://icdaccessmanagement.who.int/connect/token"
    client_id = "your_client_id"
    client_secret = "your_client_secret"
    scope = "icdapi_access"

    token_data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scope
    }

    response = requests.post(token_url, data=token_data, timeout=10)
    if response.status_code != 200:
        raise ValueError(f"Token error {response.status_code}: {response.text}")
    return response.json()["access_token"]

def remove_html_tags(text):
    """
        This function removes html tags from a string and it can be found here:
        https://medium.com/@jorlugaqui/how-to-strip-html-tags-from-a-string-in-python-7cb81a2bbf44
    """
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)
