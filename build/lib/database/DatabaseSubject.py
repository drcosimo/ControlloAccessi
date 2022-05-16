import asyncio
import sys

from reactivex import Observable, Subject
import reactivex
from database.database_interactions import *

from model.TCPDevice import TCPDevice
from model.Event import Event
from utils.enums import DeviceType, EventType, PolicyType

class DatabaseSubject(Subject,TCPDevice):
    def __init__(self,ip,port,lane) -> None:
        TCPDevice.__init__(self,ip,port,None,DeviceType.SERVER,lane)

    def createObservable(self) -> Observable:
        def on_subscription(observer,scheduler):
            async def connect():
                server = await asyncio.start_server(handleClient,self.ip,self.port)
                await server.serve_forever()

            async def handleClient(reader:asyncio.StreamReader,writer:asyncio.StreamWriter):
                try:
                    peer = writer.get_extra_info("peername")
                    data = await reader.read(1024)
                    text = data.decode(encoding="utf-8")
                    # one time request, closing connection
                    writer.close()
                    await writer.wait_closed()
                    print("Database Subject, received {0} from {1}".format(text,peer))
                    # type of request, and value associated
                    plate,badge,time = text.split(",")

                   
                    result = await self.dbRequest(plate,badge,time)
                    
                    # inserimento transit history se il grant va a buon fine
                    if result == EventType.GRANT_OK:
                        insertTransitHistory(plate,badge,time)
                    
                    # emissione risposta all'analyzer
                    evt = Event("{0},{1}".format(plate,badge),result,DeviceType.SERVER,self.lane)
                    print("database subject, submitting event {0}".format(evt.toString()))
                    observer.on_next(evt)

                except Exception as err:
                    print("errore nel database subject")
                    print(sys.call_tracing(sys.exc_info()[2],))
                    observer.on_error(sys.exc_info())

            asyncio.create_task(connect())
        return reactivex.create(on_subscription)
    
    async def dbRequest(self,plate,badge,time):
        if plate != "None" and badge != "None":
            res = findPlateAndBadge(plate,badge)
            if res:
                return EventType.GRANT_OK
            else:
                return EventType.GRANT_REFUSED
        elif badge == "None":
            res = selectPolicyFromVehicle(plate,time)
            if res == PolicyType.ONLY_PLATE_POLICY:
                return EventType.GRANT_OK
            elif res == PolicyType.NO_POLICY:
                return EventType.GRANT_REFUSED
            else:
                return EventType.NEED_BADGE
        elif plate == "None":
            res = selectPolicyFromPerson(badge,time)
            if res == PolicyType.ONLY_BADGE_POLICY:
                return EventType.GRANT_OK
            elif res == PolicyType.NO_POLICY:
                return EventType.GRANT_REFUSED
            else:
                return EventType.NEED_PLATE