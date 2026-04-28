import random
from datetime import datetime, timedelta
from database import init_db, execute_query, get_connection

def seed_data():
    init_db()
    
    categories = ["Food", "Transport", "Shopping", "Utilities", "Entertainment", "Health"]
    merchants = {
        "Food": ["Uber Eats", "Starbucks", "McDonalds", "Grocery Store", "Pizza Hut"],
        "Transport": ["Uber", "Lyft", "Gas Station", "Train Ticket"],
        "Shopping": ["Amazon", "Target", "Walmart", "Best Buy"],
        "Utilities": ["Electric Co", "Water Bill", "Internet Provider"],
        "Entertainment": ["Netflix", "Spotify", "Cinema", "Bowling"],
        "Health": ["Pharmacy", "Doctor Visit", "Gym Membership"]
    }

    # Generate 50 transactions for user_id 1
    transactions = []
    start_date = datetime.now() - timedelta(days=60)

    for _ in range(50):
        category = random.choice(categories)
        merchant = random.choice(merchants[category])
        amount = round(random.uniform(5.0, 200.0), 2)
        # Random date within last 60 days
        date = start_date + timedelta(days=random.randint(0, 60), hours=random.randint(0, 23))
        
        transactions.append((1, amount, category, merchant, date.strftime("%Y-%m-%d %H:%M:%S")))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO transactions (user_id, amount, category, merchant, transaction_date)
        VALUES (?, ?, ?, ?, ?)
    """, transactions)
    conn.commit()
    conn.close()
    print(f"Successfully seeded 50 transactions for user_id 1.")

if __name__ == "__main__":
    seed_data()
