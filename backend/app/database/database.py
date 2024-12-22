from motor.motor_asyncio import AsyncIOMotorClient

#MongoDB connection string
MONGO_URI = "mongodb://localhost:27017"

client = AsyncIOMotorClient(MONGO_URI)
db = client["payment_db"]
payments_collection = db["payments"]
evidence_collection = db["evidence"]
print("✅ Connected to MongoDB")


# Close MongDB Connect (Shutdown Event)
async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("❌ Closed MongoDB connection")
