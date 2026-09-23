from database.connection import get_connection
import pandas as pd

non_purchase_categories = [
    'EMI',
    'Fees & Charges',
    'Taxes & Charges',
    'Card Payment'
]

MONTH_ORDER = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]


def get_total_purchases():
    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute(
            "SELECT sum(amount) FROM transactions WHERE category_id NOT IN (SELECT category_id FROM categories WHERE category = ANY(%s)) AND transaction_type='Debit';", (non_purchase_categories,))
        total_purchases = cur.fetchone()

    conn.close()
    return 0 if not (total_purchases[0]) else total_purchases[0]


def get_total_rewards():
    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute(
            "SELECT SUM(amount) FROM transactions WHERE category_id=(SELECT category_id FROM categories WHERE category='Rewards');"
        )
        total_rewards = cur.fetchone()

    conn.close()
    return 0 if not (total_rewards[0]) else total_rewards[0]


def get_emi_summary():
    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute(
            "SELECT SUM(amount) FROM transactions WHERE category_id = (SELECT category_id FROM categories WHERE sub_category='Principal');"
        )
        total_principal = cur.fetchone()
        cur.execute(
            "SELECT SUM(amount) FROM transactions WHERE category_id = (SELECT category_id FROM categories WHERE sub_category='Interest');"
        )
        total_interest = cur.fetchone()
        cur.execute(
            "SELECT SUM(amount) FROM transactions WHERE category_id = (SELECT category_id FROM categories WHERE sub_category='EMI Conversion' AND transaction_type='Debit');"
        )
        total_conversion = cur.fetchone()

    conn.close()
    return ([0 if not (total_principal[0]) else total_principal[0], 0 if not (total_interest[0]) else total_interest[0], 0 if not (total_conversion[0]) else total_conversion[0]])


def get_fee_breakdown():
    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute(
            "SELECT SUM(amount) FROM transactions WHERE category_id = (SELECT category_id FROM categories WHERE sub_category='EMI Processing Fee' AND transaction_type='Debit');"
        )
        total_processing_fee = cur.fetchone()
        cur.execute(
            "SELECT SUM(amount) FROM transactions WHERE category_id = (SELECT category_id FROM categories WHERE sub_category='Cashback Redemption Fee' AND transaction_type='Debit');"
        )
        total_cashback_redemption_fee = cur.fetchone()

    conn.close()

    return (0 if not (total_processing_fee[0]) else total_processing_fee[0], 0 if not (total_cashback_redemption_fee[0]) else total_cashback_redemption_fee[0])


def get_total_fees():
    processing_fees, redemption_fees = get_fee_breakdown()
    return processing_fees + redemption_fees


def get_spending_by_category(category=None):
    conn = get_connection()

    with conn.cursor() as cur:
        if category:
            cur.execute(
                "SELECT c.sub_category,SUM(t.amount) FROM transactions t JOIN categories c ON t.category_id=c.category_id WHERE t.transaction_type='Debit' AND c.category=%s GROUP BY c.sub_category;", (category,)
            )
        else:
            cur.execute(
                "SELECT c.category,SUM(t.amount) FROM transactions t JOIN categories c ON t.category_id=c.category_id WHERE transaction_type='Debit' AND c.category != ALL(%s) GROUP BY c.category;", (
                    non_purchase_categories,)
            )
        category_spending = cur.fetchall()

    conn.close()
    return (category_spending)


def get_monthly_spending(month, year):
    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute(
            "SELECT SUM(amount) FROM transactions WHERE EXTRACT(MONTH FROM date)=%s AND EXTRACT(YEAR FROM date)=%s AND transaction_type='Debit' AND category_id NOT IN (SELECT category_id FROM categories WHERE category = ANY(%s));", (month, year, non_purchase_categories,)
        )
        monthly_spending = cur.fetchone()

    conn.close()
    return (0 if not (monthly_spending[0]) else monthly_spending[0])


def get_yearly_monthly_spending(year):
    data = []

    for month in range(1, 13):
        spending = get_monthly_spending(month, year)

        data.append({
            "Month": MONTH_ORDER[month - 1],
            "Spending": float(spending)
        })

    df = pd.DataFrame(data)

    # Explicitly tell pandas the correct order
    df["Month"] = pd.Categorical(
        df["Month"],
        categories=MONTH_ORDER,
        ordered=True
    )

    return df.sort_values("Month")
