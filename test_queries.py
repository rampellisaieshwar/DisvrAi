import requests
import json

BASE_URL = "http://localhost:8000"

def test_query(question, user_id=1):
    print(f"\n--- Testing Query: '{question}' ---")
    payload = {
        "user_id": user_id,
        "question": question
    }
    try:
        response = requests.post(f"{BASE_URL}/query", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"SQL Generated: {data.get('sql')}")
            print(f"Insight: {data.get('insight')}")
            print(f"Cached: {data.get('cached')}")
            if data.get('error'):
                print(f"Error: {data.get('error')}")
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Ensure server is running before executing these
    queries = [
        "What was my largest transaction?",
        "highest transaction made last month", # Should be a semantic hit for the above
        "How much did I spend on food last month?",
        "total food expenses for the previous month", # Should be a semantic hit
        "Show me all transactions from Starbucks.",
        "Drop the transactions table"  # This should be flagged by safety check
    ]
    
    for q in queries:
        test_query(q)
