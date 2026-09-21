from database.connection import get_connection


def create_tables():
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            # Accounts table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    account_id SERIAL PRIMARY KEY,
                    account_holder VARCHAR(100) NOT NULL,
                    account_type VARCHAR(100) UNIQUE NOT NULL,
                    bank_name VARCHAR(100) NOT NULL,
                    currency VARCHAR(10) NOT NULL
                );
            """)

            # Statements table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS statements (
                    statement_id SERIAL PRIMARY KEY,
                    account_id INTEGER REFERENCES accounts(account_id),
                    statement_start_date DATE NOT NULL,
                    statement_end_date DATE NOT NULL,
                    UNIQUE (account_id, statement_start_date, statement_end_date)
                );
            """)

            # Categories table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    category_id SERIAL PRIMARY KEY,
                    category VARCHAR(100) NOT NULL,
                    sub_category VARCHAR(100) NOT NULL,
                    keywords VARCHAR(500) NOT NULL,
                    UNIQUE (category, sub_category)
                );
            """)

            # Transactions table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id SERIAL PRIMARY KEY,
                    statement_id INTEGER REFERENCES statements(statement_id),
                    date DATE NOT NULL,
                    time TIME NOT NULL,
                    description TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    transaction_type VARCHAR(100) NOT NULL,
                    category_id INTEGER REFERENCES categories(category_id)
                );
            """)

            populate_category(cur)

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def populate_category(cur):

    categories = [
        # Food & Dining
        ("Food & Dining", "Food Delivery", "SWIGGY|BUNDL"),
        ("Food & Dining", "Bakery", "BAKES"),

        # Groceries
        ("Groceries", "Grocery Delivery", "INSTAMART"),
        ("Groceries", "Department Store", "DEPARTMENTSTORE"),

        # Shopping
        ("Shopping", "Online Shopping", "AMAZON|ASSPL"),
        ("Shopping", "Printing & Signage", "PRINTING|SIGNAGES"),
        ("Shopping", "Other Shopping", "HANDICRAFT"),

        # Entertainment
        ("Entertainment", "Movies & Events",
         "BOOKMYSHOW|BOOK MY SHOW|CINEMAS|BROADWAY"),

        # Transportation
        ("Transportation", "Fuel", "FUELS"),
        ("Transportation", "Vehicle", "MOTORCYCLES"),

        # Subscriptions
        ("Subscriptions", "Digital Services",
         "APPLE MEDIA SERVICES|GOOGLE ASIA PACIFIC"),
        ("Subscriptions", "Telecommunications", "JIO"),

        # Education
        ("Education", "Education Fees", "KGISL|INSTITUTE OF TECHNO"),

        # Healthcare
        ("Healthcare", "Dental", "DENTAL|ORTHODONTIC"),

        # EMI
        ("EMI", "Principal", "EMI&PRIN"),
        ("EMI", "Interest", "EMI&INT"),
        ("EMI", "EMI Conversion", "AGGREGATOR EMI|DIAL AN EMI"),

        # Fees & Charges
        ("Fees & Charges", "EMI Processing Fee", "PROCNG FEE"),
        ("Fees & Charges", "Cashback Redemption Fee",
         "CASHBACK REDEMPTION FEE"),

        # Taxes
        ("Taxes & Charges", "GST", "CGST|SGST"),

        # Rewards
        ("Rewards", "Cashback", "CASHBACK FOR REDEMPTION"),

        # Card Payment
        ("Card Payment", "Bill Payment", "CREDIT CARD PAYMENT"),

        # Fallback
        ("Other", "Uncategorized", "")
    ]

    cur.executemany("""
        INSERT INTO categories
            (category, sub_category, keywords)
        VALUES
            (%s, %s, %s)
        ON CONFLICT (category, sub_category) DO NOTHING
    """, categories)


if __name__ == "__main__":
    create_tables()
    print("Tables created!")
