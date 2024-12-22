from fastapi import FastAPI
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

# async def insert_normalized_data():
#     await payments_collection.insert_one({
#         "payee_email": "placeholder@example.com",
#         "amount": 0,
#         "status": "placeholder"
#     })
#     logger.info("🟩 Inserted placeholder record to initialize collection.")
#     # Check if collection is empty
#     count = await payments_collection.count_documents({})
#
#     if count == 0:
#         normalized_data = normalize_csv(csv_file_path)
#         if normalized_data:
#             await payments_collection.insert_many(normalized_data)
#             logger.info(f"✅ Inserted {len(normalized_data)} normalized records into MongoDB.")
#         else:
#             logger.info("⚠️ No records to insert.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        normalized_data = normalize_csv(csv_file_path)

        # Perfrom upsert for each record
        for payment in normalized_data:
            # Convert datetime.date to datetime.datetime
            if isinstance(payment["payee_due_date"], date):
                payment["payee_due_date"] = datetime.combine(payment["payee_due_date"], datetime.min.time())

            filter_query = {"payee_email": payment["payee_email"]}
            update_query = {"$set": payment}

            await payments_collection.update_one(filter_query, update_query, upsert=True)
        logger.info(f"✅ Upserted {len(normalized_data)} records into MongoDB.")
        yield

    finally:
        await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # await connect_to_mongo()
#
#     # Ensure the collection is initialized
#     # if not payments_collection or not evidence_collection:
#     #     logger.error("❌ MongoDB connection failed. Collection is not initialized.")
#     #     return
#
#     # Load and upsert normalized data
#     try:
#         await connect_to_mongo()
#
#         # Insert Csv data if collection is empty
#         # await insert_normalized_data()
#
#         logger.info("✅ MongoDB connected and initialized.")
#         yield
#
#     finally:
#         # Shutdown - Close MongoDB Connection
#         if client:
#             client.close()
#             logger.info(f"❌ Closed MongoDB collection")
#
#
# app = FastAPI(lifespan=lifespan)

app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
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
