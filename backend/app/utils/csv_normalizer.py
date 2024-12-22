import pandas as pd
from datetime import datetime, date, time

def normalize_csv(file_path):
    df = pd.read_csv(file_path)

    # Ensure all mandatory fields are present
    required_fields = [
        "payee_first_name",
        "payee_last_name",
        "payee_payment_status",
        "payee_added_date_utc",
        "payee_due_date", 
        "payee_address_line_1",
        "payee_city",
        "payee_country",
        "payee_postal_code",
        "payee_phone_number",
        "payee_email",
        "currency",
        "due_amount"
    ]

    for field in required_fields:
        if field not in df.columns:
            raise ValueError(f"Missing mandatory field: {field}")
        
    # Normalize date formats
    df["payee_added_date_utc"] = pd.to_datetime(df["payee_added_date_utc"], errors="coerce")
    df["payee_due_date"] = pd.to_datetime(df["payee_due_date"], errors="coerce").dt.date

    # # Convert date to datetime to avoid BSON Error
    # df["payee_due_date"] = df["payee_due_date"].apply(
    #     lambda x: datetime.combine(x, time(0, 0)) if isinstance(x, date) else x
    # )

    # Calculate total_due
    # df["total_due"] = df["due_amount"] * (1 + df.get("tax_percent", 0)/100) - (df.get("discount_percent", 0)/100)

    df["total_due"] = ( df["due_amount"] * (1 + df["tax_percent"] / 100) - (
            df["due_amount"] * df["discount_percent"] / 100)).round(2)

    # Normalize status based on due date
    df["payee_payment_status"] = "pending"
    today = datetime.now().date()
    df["payee_due_date"] = pd.to_datetime(df["payee_due_date"]).dt.date

    df.loc[df["payee_due_date"] < today, "payee_payment_status"] = "overdue"
    df.loc[df["payee_due_date"] == today, "payee_payment_status"] = "due_now"

    # Drop invalid rows
    # df.dropna(inplace=True)

    return df.to_dict(orient="records")

