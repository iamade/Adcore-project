export interface Payment {
    id?: string;  // Optional, generated by MongoDB
    payee_first_name: string;
    payee_last_name: string;
    payee_payment_status: string;
    payee_added_date_utc: string;  // ISO date string (e.g., "2024-12-18T18:08:21.012Z")
    payee_due_date: string;        // ISO date string (e.g., "2024-12-22")
    payee_address_line_1: string;
    payee_address_line_2?: string; // Optional
    payee_city: string;
    payee_country: string;         // ISO 3166-1 alpha-2 (e.g., "CA")
    payee_province_or_state?: string; // Optional
    payee_postal_code: string;
    payee_phone_number: string;    // E.164 format (e.g., "+123456789")
    payee_email: string;
    currency: string;              // ISO 4217 (e.g., "USD")
    discount_percent?: number;     // Optional, defaults to 0
    tax_percent?: number;          // Optional, defaults to 0
    due_amount: number;
    total_due: number;             // Dynamically calculated on the backend
  }
  