import asyncio
import random as rd
import sys
from database_interactions import extractRandomPlate

async def main(port):
    try:
        r,w = await asyncio.open_connection("127.0.0.1",10000 + int(port))
        while True:
            await asyncio.sleep(rd.randint(10,15))
            print("plate detected")
            plate = extractRandomPlate()
            w.write(plate.encode("utf-8"))
            await w.drain()
    except KeyboardInterrupt:
        w.write_eof()
        await w.drain()
        w.close()
        await w.wait_closed()
    except ConnectionResetError:
        print("server disconnected")
        
if __name__ =="__main__":
    asyncio.run(main(sys.argv[1]))