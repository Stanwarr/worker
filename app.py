import traceback
from API import *
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
from random import sample

def GetDBinfo():
	return os.environ.get("MONGODB_URI") + "?retryWrites=false"

async def do_5():
    load_dotenv()
    
    client = AsyncIOMotorClient(GetDBinfo())
    db = client.get_default_database()
    AccDB = db['accounts']

    all_accounts = await AccDB.distinct("_id")
    
    random_accounts = sample(all_accounts, min(5, len(all_accounts)))
    
    async for acc in AccDB.find({"_id": {"$in": random_accounts}}):
        try:
            async with API(acc) as L:
                sacs = os.environ.get("SAC").split(",")
                await L.SetSaC(sacs)
        except:
            pass


if __name__ == "__main__":
    asyncio.run(do_5())