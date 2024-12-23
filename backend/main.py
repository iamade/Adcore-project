from fastapi import FastAPI
from pymongo import UpdateOne
from fastapi.middleware.cors import CORSMiddleware

from app.routes import payments, evidence
from app.utils.csv_normalizer import normalize_csv
from app.database.database import payments_collection, evidence_collection, client, close_mongo_connection
import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime, date, time


# app = FastAPI()

#Path to the csv file
csv_file_path = os.path.join(os.path.dirname(__file__), "app/data/payment_information.csv") 

# Configure logging
logging .basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Normalize the CSV data
        normalized_data = normalize_csv(csv_file_path)

        # Prepare bulk upsert operations
        bulk_operations = []
        for payment in normalized_data:
            # Convert datetime.date to datetime.datetime
            if isinstance(payment["payee_due_date"], date):
                payment["payee_due_date"] = datetime.combine(payment["payee_due_date"], datetime.min.time())

            # Ensure phone number and postal code are strings
            payment["payee_phone_number"] = str(payment["payee_phone_number"])
            payment["payee_postal_code"] = str(payment["payee_postal_code"])

            # Prepare bulk upsert operation
            filter_query = {"payee_email": payment["payee_email"]}
            update_query = {"$set": payment}
            bulk_operations.append(
                UpdateOne(filter_query, update_query, upsert=True)
            )

        # Perform bulk upsert if there are records
        if bulk_operations:
            result = await payments_collection.bulk_write(bulk_operations)
            logger.info(
                f"✅ Upserted {result.upserted_count} new records, {result.modified_count} modified records."
            )
        else:
            logger.info("⚠️ No records to upsert.")

        yield

    finally:
        await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

# Allow specific origins (localhost:4200 for Angular)
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Allow all headers
)


app.include_router(payments.router, prefix="/api", tags=["Payments"])
app.include_router(evidence.router, prefix="/api/evidence", tags=["Evidence"])


# @app.get("/")
# async def get_all_todos():
#     data = payments_collection.find( )
#     return [payment for payment in data]@app.get("/")

# @app.get("/")
# async def get_all_todos():
#     data = payments_collection.find({})
#     payments = await data.to_list(length=None)
#     return payments

# Test endpoint to verify connection
@app.get("/test_connection")
async def test_connection():
    try:
        if payments_collection and evidence_collection:
            await payments_collection.find_one()
            await evidence_collection.find_one()
            return {"status": "Connected to MongoDB"}
        else:
            raise Exception("Database collections not initialized")
    except Exception as e:
        logger.error(f"Failed to connect: {e}")
        return {"status": "Failed to connect to MongoDB"}


@app.get("/verify_data")
async def verify_data():
    try:
        if payments_collection:
            records = await payments_collection.find().to_list(10)
            return records
        else:
            return {"error": "Database collection not initialized"}
    except Exception as e:
        logger.error(f"Failed to fetch records: {e}")
        return {"error": "Failed to fetch records"}

# async def load_data():
#     try:
#         # Normalize the CSV data
#         normalized_data = normalize_csv(csv_file_path)

#         # Insert into MongoDB
#         # if normalized_data:
#         #     await payments_collection.insert_many(normalized_data)
#         if await payments_collection.count_documents({}):
#             await payments_collection.insert_many(normalized_data)
        
#         print(f"Inserted {len(normalized_data)} records into MongoDB.")
#     except Exception as e:
#         print(f"Error loading data: {e}")
