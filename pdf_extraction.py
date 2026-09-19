import re
import pymupdf as pdf
import data_cleaner as dc


# ============================================================
# REGEX
# ============================================================

DATE_RE = re.compile(r"^\d{2}/\d{2}/\d{4}\|?$")
TIME_RE = re.compile(r"^\d{2}:\d{2}$")
AMOUNT_RE = re.compile(r"^[\d,]+\.\d{2}$")


def is_date(text):
    return bool(DATE_RE.match(text.strip()))


def is_time(text):
    return bool(TIME_RE.match(text.strip()))


def is_amount(text):
    return bool(AMOUNT_RE.match(text.strip()))


def clean_date(text):
    return text.strip().rstrip("|")


def parse_amount(text):
    return float(text.replace(",", ""))


# ============================================================
# STATEMENT METADATA
# ============================================================

def extract_statement_metadata(doc):
    """
    Extract only the required statement metadata:

        - bank_name
        - user_name
        - currency
    """

    text_parts = []

    for page in doc:
        text_parts.append(page.get_text())

    text = "\n".join(text_parts)

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    metadata = {
        "bank_name": None,
        "user_name": None,
        "currency": None,
    }

    # ========================================================
    # BANK NAME
    # ========================================================

    if re.search(
        r"\bHDFC\s+Bank\b",
        text,
        re.I
    ):
        metadata["bank_name"] = "HDFC Bank"

    # ========================================================
    # USER NAME
    # ========================================================

    for i, line in enumerate(lines):

        if re.match(
            r"^(S/O|D/O|W/O)\b",
            line,
            re.I
        ):

            if i > 0:
                metadata["user_name"] = lines[i - 1]

            break

    # ========================================================
    # CURRENCY
    # ========================================================

    if (
        metadata["bank_name"] == "HDFC Bank"
        and re.search(
            r"GSTIN|HDFC\s+Bank\s+Credit\s+Cards",
            text,
            re.I
        )
    ):
        metadata["currency"] = "INR"

    return metadata


# ============================================================
# CARD FORMAT
# ============================================================

def detect_card_format(doc):
    """
    Detect the card format from the COMPLETE PDF.

    Detection is performed once for the entire document.
    It is NOT performed page-by-page.
    """

    text_parts = []

    for page in doc:
        text_parts.append(page.get_text())

    text = "\n".join(text_parts)

    normalized = re.sub(r"\s+", " ", text).lower()

    # --------------------------------------------------------
    # RuPay
    # --------------------------------------------------------

    if "rupay credit card statement" in normalized:
        return "rupay"

    if "upi rupay credit card" in normalized:
        return "rupay"

    if "rupay credit card" in normalized:
        return "rupay"

    # --------------------------------------------------------
    # Millennia
    # --------------------------------------------------------

    if "millennia credit card statement" in normalized:
        return "millennia"

    if "millennia" in normalized:
        return "millennia"

    return None


# ============================================================
# MILLENNIA
#
# DO NOT CHANGE THIS PIPELINE.
# ============================================================

def extract_millennia_transactions(page):

    words = page.get_text("words")

    header = {}

    for x0, y0, x1, y1, text, block, line, word in words:

        if text == "DATE":
            header["date"] = x0

        elif text == "TIME":
            header["time"] = x0

        elif text == "TRANSACTION":
            header["description"] = x0

        elif text == "AMOUNT":
            header["amount"] = x0

        elif text == "PI":
            header["pi"] = x0

    required = {
        "date",
        "time",
        "description",
        "amount",
        "pi",
    }

    if not required.issubset(header):
        return []

    date_x = header["date"]
    time_x = header["time"]
    description_x = header["description"]
    amount_x = header["amount"]
    pi_x = header["pi"]

    date_right = (date_x + time_x) / 2
    time_right = (time_x + description_x) / 2
    description_right = (description_x + amount_x) / 2

    amount_left = description_right
    amount_right = pi_x

    starts = []

    for item in words:

        x0, y0, x1, y1, text, block, line, word = item

        if not (date_x - 10 <= x0 < date_right):
            continue

        if not is_date(text):
            continue

        if y0 <= 270:
            continue

        starts.append({
            "y": y0,
            "date": clean_date(text),
        })

    starts = sorted(
        starts,
        key=lambda x: x["y"]
    )

    unique_starts = []

    for start in starts:

        if (
            not unique_starts
            or abs(
                start["y"]
                - unique_starts[-1]["y"]
            ) > 2
        ):
            unique_starts.append(start)

    starts = unique_starts

    transactions = []

    for i, start in enumerate(starts):

        start_y = start["y"]

        if i + 1 < len(starts):
            end_y = starts[i + 1]["y"]
        else:
            end_y = float("inf")

        row_words = []

        for item in words:

            x0, y0, x1, y1, text, block, line, word = item

            if start_y - 1 <= y0 < end_y - 1:
                row_words.append(item)

        date = start["date"]

        time = None

        for item in row_words:

            x0, y0, x1, y1, text, block, line, word = item

            if time_x - 10 <= x0 < time_right:

                if is_time(text):
                    time = text
                    break

        description_parts = []

        for item in row_words:

            x0, y0, x1, y1, text, block, line, word = item

            if (
                description_x - 5
                <= x0
                < description_right
            ):
                description_parts.append(text)

        description = " ".join(
            description_parts
        )

        amount = None

        for item in row_words:

            x0, y0, x1, y1, text, block, line, word = item

            if (
                amount_left - 15
                <= x0
                < amount_right
            ):

                if is_amount(text):
                    amount = parse_amount(text)

        indicators = []

        for item in row_words:

            x0, y0, x1, y1, text, block, line, word = item

            if (
                amount_left - 20
                <= x0
                < amount_right
            ):

                if text in ("+", "-", "C", "D"):
                    indicators.append(text)

        # Never create incomplete records.
        if (
            date is None
            or time is None
            or amount is None
        ):
            continue

        transactions.append({
            "date": date,
            "time": time,
            "description": description,
            "amount": amount,
            "indicators": indicators
        })

    return transactions


# ============================================================
# RUPAY
#
# RuPay format:
#
# Domestic Transactions
#
# DATE & TIME TRANSACTION DESCRIPTION REWARDS AMOUNT PI
#
# 14/08/2026| 00:00 CGST-... C 152.01 l
#
# ============================================================

def find_rupay_header_y(page):
    """
    Find the Y position of the RuPay transaction table header.

    We intentionally do NOT depend on X coordinates.
    """

    words = page.get_text("words")

    lines = {}

    for item in words:

        x0, y0, x1, y1, text, block, line, word = item

        key = round(y0, 1)

        lines.setdefault(
            key,
            []
        ).append(item)

    for y, line_words in sorted(
        lines.items()
    ):

        line_words = sorted(
            line_words,
            key=lambda item: item[0]
        )

        line_text = " ".join(
            item[4].strip().upper()
            for item in line_words
        )

        normalized = re.sub(
            r"[^A-Z& ]",
            " ",
            line_text
        )

        normalized = re.sub(
            r"\s+",
            " ",
            normalized
        ).strip()

        if (
            "DATE" in normalized
            and "TIME" in normalized
            and "TRANSACTION" in normalized
            and "DESCRIPTION" in normalized
            and "REWARDS" in normalized
            and "AMOUNT" in normalized
            and "PI" in normalized
        ):
            return y

    return None


def find_rupay_transaction_starts(page, header_y):
    """
    Find transaction starting rows.

    A RuPay transaction starts with:

        DD/MM/YYYY|

    followed by:

        HH:MM
    """

    words = page.get_text("words")

    starts = []

    for item in words:

        x0, y0, x1, y1, text, block, line, word = item

        if y0 <= header_y:
            continue

        if not is_date(text):
            continue

        date = clean_date(text)

        has_time = False

        for time_item in words:

            tx0, ty0, tx1, ty1, time_text, *_ = time_item

            if abs(ty0 - y0) <= 3:

                if is_time(time_text):
                    has_time = True
                    break

        if not has_time:
            continue

        starts.append({
            "y": y0,
            "date": date,
        })

    starts.sort(
        key=lambda item: item["y"]
    )

    unique = []

    for start in starts:

        if (
            not unique
            or abs(
                start["y"]
                - unique[-1]["y"]
            ) > 2
        ):
            unique.append(start)

    return unique


def extract_rupay_transactions(page):

    words = page.get_text("words")

    # --------------------------------------------------------
    # Locate transaction table.
    # --------------------------------------------------------

    header_y = find_rupay_header_y(page)

    if header_y is None:

        print(
            "WARNING: RuPay transaction header not found"
        )

        return []

    # --------------------------------------------------------
    # Locate transaction rows.
    # --------------------------------------------------------

    starts = find_rupay_transaction_starts(
        page,
        header_y
    )

    if not starts:
        return []

    transactions = []

    # --------------------------------------------------------
    # Process every transaction.
    # --------------------------------------------------------

    for index, start in enumerate(starts):

        start_y = start["y"]

        if index + 1 < len(starts):
            end_y = starts[index + 1]["y"]
        else:
            end_y = float("inf")

        # ----------------------------------------------------
        # Get all words belonging to this transaction.
        # ----------------------------------------------------

        row_words = []

        for item in words:

            x0, y0, x1, y1, text, block, line, word = item

            if start_y - 1 <= y0 < end_y - 1:
                row_words.append(item)

        # ----------------------------------------------------
        # Sort top-to-bottom, then left-to-right.
        # ----------------------------------------------------

        row_words.sort(
            key=lambda item: (
                round(item[1], 1),
                item[0]
            )
        )

        # ----------------------------------------------------
        # DATE
        # ----------------------------------------------------

        date = start["date"]

        # ----------------------------------------------------
        # TIME
        # ----------------------------------------------------

        time = None
        time_item = None

        for item in row_words:

            text = item[4].strip()

            if is_time(text):

                time = text
                time_item = item
                break

        # ----------------------------------------------------
        # AMOUNT
        #
        # Find all monetary values and use the right-most one.
        # ----------------------------------------------------

        amount_candidates = []

        for item in row_words:

            x0, y0, x1, y1, text, block, line, word = item

            if is_amount(text):

                amount_candidates.append({
                    "x": x0,
                    "amount": parse_amount(text),
                    "item": item,
                })

        amount = None
        amount_item = None

        if amount_candidates:

            candidate = max(
                amount_candidates,
                key=lambda item: item["x"]
            )

            amount = candidate["amount"]
            amount_item = candidate["item"]

        # ----------------------------------------------------
        # DESCRIPTION
        # ----------------------------------------------------

        description_parts = []

        if time_item is not None:

            time_x = time_item[0]

            amount_x = (
                amount_item[0]
                if amount_item is not None
                else float("inf")
            )

            for item in row_words:

                x0, y0, x1, y1, text, block, line, word = item

                text = text.strip()

                # Must come after TIME.
                if x0 <= time_x:
                    continue

                # Must come before AMOUNT.
                if x0 >= amount_x:
                    continue

                # Ignore non-description tokens.
                if text in {
                    "+",
                    "-",
                    "C",
                    "D",
                    "l",
                    "|",
                }:
                    continue

                # Ignore monetary values.
                if is_amount(text):
                    continue

                description_parts.append(text)

        description = " ".join(
            description_parts
        )

        # ----------------------------------------------------
        # INDICATORS
        # ----------------------------------------------------

        indicators = []

        for item in row_words:

            text = item[4].strip()

            if text in ("+", "-", "C", "D"):

                if text not in indicators:
                    indicators.append(text)

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if date is None:
            continue

        if time is None:
            continue

        if amount is None:
            continue

        transactions.append({
            "date": date,
            "time": time,
            "description": description,
            "amount": amount,
            "indicators": indicators
        })

    return transactions


# ============================================================
# MAIN EXTRACTION
# ============================================================

def extract_transactions(pdf_path):

    doc = pdf.open(pdf_path)

    try:

        # ----------------------------------------------------
        # Extract metadata once from complete PDF.
        # ----------------------------------------------------

        metadata = extract_statement_metadata(doc)

        # ----------------------------------------------------
        # Detect card format once from complete PDF.
        # ----------------------------------------------------

        card_format = detect_card_format(doc)
        if card_format is None:

            raise ValueError(
                "Could not detect HDFC card format."
            )
        all_transactions = []

        # ----------------------------------------------------
        # Process pages.
        # ----------------------------------------------------

        for page_number, page in enumerate(doc):

            # ------------------------------------------------
            # Millennia
            # ------------------------------------------------

            if card_format == "millennia":

                transactions = (
                    extract_millennia_transactions(page)
                )

            # ------------------------------------------------
            # RuPay
            # ------------------------------------------------

            elif card_format == "rupay":

                transactions = (
                    extract_rupay_transactions(page)
                )

            else:

                transactions = []

            # ------------------------------------------------
            # Output transactions.
            # ------------------------------------------------

            for transaction in transactions:

                all_transactions.append(
                    transaction
                )

        # Add card type
        metadata['card_type'] = card_format
        # ----------------------------------------------------
        # Return metadata + transactions.
        # ----------------------------------------------------

        return {
            "metadata": metadata,
            "transactions": all_transactions,
        }

    finally:

        doc.close()


# ============================================================
# RUN
# ============================================================

def run(file_path):

    result = extract_transactions(
        'samples/'+file_path
    )
    return dc.clean_data(result)
