from database.connection import get_connection


def clear_database():
    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute("drop table categories;")
        cur.execute("drop table transactions;")
        cur.execute("drop table statements;")
        cur.execute("drop table accounts;")

    conn.commit()
    conn.close()


def insert_account(account_data):
    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO accounts (
                account_holder,
                bank_name,
                currency,
                account_type
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (account_type)
            DO UPDATE SET account_type = EXCLUDED.account_type
            RETURNING account_id;
            """,
            (
                account_data["user_name"],
                account_data["bank_name"],
                account_data["currency"],
                account_data["account_type"],
            )
        )

        acc_id = cur.fetchone()[0]

    conn.commit()
    conn.close()

    return acc_id


def get_accounts():
    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute("Select * from accounts")
        accounts = cur.fetchall()
        columns = [desc.name for desc in cur.description]

    conn.close()
    return accounts, columns


def insert_statement(transaction_data, acc_id):
    statement_id = None
    start_date, end_date = transaction_data[0]['date'], transaction_data[-1]['date']
    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO statements (
                account_id,
                statement_start_date,
                statement_end_date
            )
            VALUES (%s, %s, %s)
            ON CONFLICT (
                account_id,
                statement_start_date,
                statement_end_date
            ) DO NOTHING
            RETURNING statement_id;
            """,
            (acc_id, start_date, end_date)
        )

        result = cur.fetchone()
        statement_id = result[0] if result else None

    conn.commit()
    conn.close()
    return statement_id


def get_statements(acc_id=None):
    conn = get_connection()

    with conn.cursor() as cur:
        if acc_id is not None:
            print('Here')
            cur.execute(
                "Select * from statements where account_id= %s", (acc_id,)
            )
        else:
            cur.execute(
                "Select * from statements;"
            )
        statements = cur.fetchall()
        columns = [desc.name for desc in cur.description]

    conn.close()
    return statements, columns


def insert_transactions(statement_id, transaction_data):
    conn = get_connection()

    with conn.cursor() as curr:
        rows = [
            (
                statement_id,
                transaction["date"],
                transaction["time"],
                transaction["description"],
                transaction["amount"],
                transaction["transaction_type"]
            )
            for transaction in transaction_data
        ]

        curr.executemany(
            """ 
            INSERT INTO transactions (
                statement_id,
                date,
                time,
                description,
                amount,
                transaction_type    
            ) VALUES (%s,%s,%s,%s,%s,%s)
            """,
            rows
        )

    conn.commit()
    conn.close()


def get_transactions(statement_id=None, account_id=None, date_range=None, transaction_type=None):
    conn = get_connection()

    query = "SELECT * FROM transactions"
    conditions = []
    params = []

    with conn.cursor() as cur:

        if account_id is not None:
            cur.execute(
                "SELECT statement_id FROM statements WHERE account_id = %s",
                (account_id,)
            )

            statement_ids = [row[0] for row in cur.fetchall()]

            conditions.append("statement_id = ANY(%s)")
            params.append(statement_ids)

        if statement_id is not None:
            conditions.append("statement_id = %s")
            params.append(statement_id)

        if date_range is not None:
            conditions.append("date BETWEEN %s AND %s")
            params.extend([date_range[0], date_range[1]])

        if transaction_type is not None:
            conditions.append("transaction_type = %s")
            params.append(transaction_type)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cur.execute(query, params)

        statements = cur.fetchall()
        columns = [desc.name for desc in cur.description]

    conn.close()
    return statements, columns


# Main insert function
def insert(data):
    meta_data = data['metadata']
    transactions_data = data['transactions']
    acc_id = insert_account(meta_data)
    statement_id = insert_statement(
        transactions_data, acc_id)
    if statement_id != None:
        insert_transactions(statement_id, transactions_data)
