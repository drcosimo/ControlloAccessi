import asyncio
from model.Event import Event

# classe intermediaria per le richieste al database,alla sbarra e al logger
class Connection():
    def __init__(self,db_ip,db_port,bar_ip,bar_port,logger_ip,logger_port) -> None:
        self.dp_ip = db_ip
        self.db_port = db_port
        self.bar_ip = bar_ip
        self.bar_port = bar_port
        self.logger_ip = logger_ip
        self.logger_port = logger_port

    # connessione al database
    async def connectToDb(self,req):
        r,w = await asyncio.open_connection(self.dp_ip,self.db_port)
        w.write(req.encode("utf-8"))
        await w.drain()

        w.close()
        await w.wait_closed()
    
    # connessione alla sbarra
    async def connectToBar(self):
        r,w = await asyncio.open_connection(self.bar_ip,self.bar_port)
        w.write("OPEN_GATE".encode("utf-8"))
        await w.drain()

        w.close()
        await w.wait_closed()

    # creazione richiesta database
    def dbRequest(self,plate,badge,time):
        # richiesta grant badgeplate
        req = f"{plate},{badge},{time}"
        
        asyncio.create_task(self.connectToDb(req))

    # creazione richiesta logger
    def loggerRequest(self, evt: Event):
        req = f"{evt.value},{evt.eventType},{evt.deviceType}"

        asyncio.create_task(self.connectToLogger(req))

    # connessione al logger
    async def connectToLogger(self, evt):
        r, w = await asyncio.open_connection(self.logger_ip, self.logger_port)
        w.write(evt.encode("utf-8"))
        await w.drain()

        w.close()
        await w.wait_closed()