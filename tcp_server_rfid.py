import asyncio
import random as rd
import sys
from database_interactions import extractRandomBadge

async def main(port):
    server = await asyncio.start_server(handleClient,"127.0.0.1",10000 + int(port))
    await server.serve_forever()
    
async def handleClient(reader:asyncio.StreamReader,writer:asyncio.StreamWriter):
    try:
        while True:
            await asyncio.sleep(rd.randint(15,20))
            badge = extractRandomBadge()
            print("badge detected")
            writer.write(badge.encode("utf-8"))
            await writer.drain()
    except KeyboardInterrupt:
        writer.write_eof()
        await writer.drain()
        writer.close()
        await writer.wait_closed()
    
if __name__ =="__main__":
    asyncio.run(main(sys.argv[1]))