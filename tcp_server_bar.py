import asyncio
import random as rd
import sys

async def main(port):
    server = await asyncio.start_server(handleClient,"127.0.0.1",10000 + int(port))
    await server.serve_forever()
    
async def handleClient(reader,writer):
    try:
        while True:
            data = await reader.readline()
            print("signal received,opening gate")
    except KeyboardInterrupt:
        writer.write_eof()
        await writer.drain()
        writer.close()
        await writer.wait_closed()
    
if __name__ =="__main__":
    asyncio.run(main(sys.argv[1]))