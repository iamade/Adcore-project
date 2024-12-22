import pandas as pd
from datetime import datetime, date, time
import re
import pycountry

# Map Full Country Names to Alpha-2 Codes
def get_country_alpha_2(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_2
    except LookupError:
        return None  # Return None if country is not found

def normalize_csv(file_path):
    df = pd.read_csv(file_path)

    # 1. Trim Whitespace from All Columns
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

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

    # 3. Validate Payment Status
    valid_statuses = ["completed", "due_now", "overdue", "pending"]
    df["payee_payment_status"] = df["payee_payment_status"].str.lower()
    if not df["payee_payment_status"].isin(valid_statuses).all():
        raise ValueError("❌ Invalid payee_payment_status. Accepted values: completed, due_now, overdue, pending")


    # 4. Convert payee_added_date_utc to UTC Timestamp
    df["payee_added_date_utc"] = pd.to_datetime(df["payee_added_date_utc"], errors='coerce')
    if df["payee_added_date_utc"].isnull().any():
        raise ValueError("❌ Invalid payee_added_date_utc. Must be in UTC timestamp format.")

    # 5. Convert payee_due_date to YYYY-MM-DD
    df["payee_due_date"] = pd.to_datetime(df["payee_due_date"], format='%Y-%m-%d', errors='coerce')
    if df["payee_due_date"].isnull().any():
        raise ValueError("❌ Invalid payee_due_date. Must be in YYYY-MM-DD format.")

    # 1. Handle Missing Countries
    df["payee_country"] = df["payee_country"].fillna("XX")  # Default to "XX"

    # 2. Convert Full Country Names to Alpha-2 Codes
    df["payee_country"] = df["payee_country"].apply(lambda x: get_country_alpha_2(str(x)) if len(str(x)) > 2 else x)

    # 6. Validate Country (ISO 3166-1 alpha-2)
    valid_countries = {country.alpha_2 for country in pycountry.countries}
    valid_countries.add("XX")

    invalid_countries = df[~df["payee_country"].isin(valid_countries)]

    if not invalid_countries.empty:
        raise ValueError(f"❌ Invalid payee_country values: {invalid_countries['payee_country'].unique()}. Must follow ISO 3166-1 alpha-2.")


        # 7. Validate Currency (ISO 4217)
    valid_currencies = {currency.alpha_3 for currency in pycountry.currencies}
    if not df["currency"].isin(valid_currencies).all():
        raise ValueError("❌ Invalid currency. Must follow ISO 4217 (e.g., USD, EUR).")

    # 8. Validate Phone Number (E.164 Format)
    def validate_phone(phone):
        phone = str(phone)
        if not re.match(r'^\+?[1-9]\d{1,14}$', phone):
            raise ValueError(f"❌ Invalid phone number format: {phone}. Must follow E.164 format.")

    df["payee_phone_number"].apply(validate_phone)

    # 9. Round Percentages to 2 Decimal Places
    df["discount_percent"] = df["discount_percent"].fillna(0.0).round(2)
    df["tax_percent"] = df["tax_percent"].fillna(0.0).round(2)

    # 10. Calculate total_due (2 Decimal Places)
    df["due_amount"] = df["due_amount"].round(2)
    df["total_due"] = round(
        df["due_amount"] * (1 + df["tax_percent"] / 100) -
        (df["due_amount"] * df["discount_percent"] / 100), 2
    )


    # # Normalize date formats
    # df["payee_added_date_utc"] = pd.to_datetime(df["payee_added_date_utc"], errors="coerce")
    # df["payee_due_date"] = pd.to_datetime(df["payee_due_date"], errors="coerce").dt.date
    #
    # # Calculate total_due
    # df["total_due"] = ( df["due_amount"] * (1 + df["tax_percent"] / 100) - (
    #         df["due_amount"] * df["discount_percent"] / 100)).round(2)

    # Normalize status based on due date
    df["payee_payment_status"] = "pending"
    today = datetime.now().date()
    df["payee_due_date"] = pd.to_datetime(df["payee_due_date"]).dt.date

    df.loc[df["payee_due_date"] < today, "payee_payment_status"] = "overdue"
    df.loc[df["payee_due_date"] == today, "payee_payment_status"] = "due_now"

    # Drop invalid rows
    # df.dropna(inplace=True)

    return df.to_dict(orient="records")

