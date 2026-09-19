
from database.connection import get_connection


def create_tables():
    conn = get_connection()

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
                        statement_end_date DATE NOT NULL
                    )
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
                        transaction_type VARCHAR(100) NOT NULL
                    )
                    """)

        # Categories table
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS categories (
                        category_id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL
                    )
                    """)

        dat = cur.execute("select * from accounts;")
        print(dat)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
    print("Tables created!")
