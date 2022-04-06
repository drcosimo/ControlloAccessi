import asyncio
import random as rd
import sys
plates = ["QW123WQ","SA222SD","FD121TR"]

async def main(port):
    try:
        r,w = await asyncio.open_connection("127.0.0.1",10000 + int(port))
        while True:
            await asyncio.sleep(rd.randint(1,10))
            print("plate detected")
            w.write(plates[rd.randint(0,2)].encode("utf-8"))
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