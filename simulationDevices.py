import asyncio
import sys
import random as rd
from database_interactions import extractRandomBadge,extractRandomPlate

# lane 1 => 10001,10002,10003,10004,10005

# lane 2 => 20001,20002,20003,20004,20005

# lane n => n0001(Client),n0002(Client),n0003(Server),n0004(Client),n0005(Server)

async def createServerRfid(lane,index):
    server = await asyncio.start_server(handleClientRfid,"127.0.0.1",(lane*10000+index))
    print("rfid started")
    await server.serve_forever()

async def createServerBar(lane,index):
    server = await asyncio.start_server(handleClientBar,"127.0.0.1",(lane*10000+index))
    print("bar started")
    await server.serve_forever()

async def handleClientBar(reader,writer):
    try:
        
        data = await reader.read(1024)
        print("signal received,opening gate")
        
        writer.write_eof()
        await writer.drain()
        writer.close()
        await writer.wait_closed()
    except KeyboardInterrupt:
        writer.write_eof()
        await writer.drain()
        writer.close()
        await writer.wait_closed()

async def handleClientRfid(reader,writer):
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

async def createClient(lane,index):
    try:
        await asyncio.sleep(10)
        r,w = await asyncio.open_connection("127.0.0.1",(lane*10000+index))

        while True:
            value = ""
            # differenza valore tra cam e button
            if index == 4:
                await asyncio.sleep(rd.randint(30,40))
                value = "OPEN_GATE"
            else:
                await asyncio.sleep(rd.randint(10,15))
                value = extractRandomPlate()
            
            w.write(value.encode("utf-8"))
            await w.drain()
            
    except KeyboardInterrupt:
        w.write_eof()
        await w.drain()
        w.close()
        await w.wait_closed()
    except ConnectionResetError:
        print("server disconnected")


async def main(numLanes):
    # per ogni lane
    for i in range(1,numLanes+1):
        # per ogni device della lane
        for j in range(1,6):
            # controllo server o client
            #rfid server
            if j == 3:
                # creazione server
                asyncio.create_task(createServerRfid(i,j))
            #bar server
            elif j == 5:
                asyncio.create_task(createServerBar(i,j))
            #client
            else:
                # creazione client
                asyncio.create_task(createClient(i,j))

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    loop.create_task(main(int(sys.argv[1])))
    loop.run_forever()
