import dns.resolver
from pymongo import AsyncMongoClient

from config.settings import settings


dns.resolver.default_resolver = dns.resolver.Resolver(
    configure=True
)

dns.resolver.default_resolver.nameservers = [
    "1.1.1.1",
    "1.0.0.1",
]


client = AsyncMongoClient(settings.mongodb_url)

database = client[settings.database_name]


async def connect_to_database():
    await client.admin.command("ping")
    print("MongoDB connected successfully")


async def close_database_connection():
    await client.close()
    print("MongoDB connection closed")