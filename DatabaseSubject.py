import asyncio
import sys
from urllib.request import Request
from reactivex import Observable, Subject
from datetime import datetime, time
import reactivex
from database_interactions import *

from classes import TCPDevice,Event
from enums import DeviceType, EventType, RequestType

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
                    type,plate,badge,time = text.split(",")
                    
                    result = await self.dbRequest(int(type),plate,badge,time)
                    
                    if result is not None:
                        # create event
                        evt = Event("{0},{1}".format(plate,badge),result,DeviceType.SERVER)
                        print("submitting event {0}".format(evt.toString()))
                        observer.on_next(evt)
                except Exception as err:
                    print("errore nel database subject")
                    print(sys.call_tracing(sys.exc_info()[2],))
                    observer.on_error(sys.exc_info())

            asyncio.create_task(connect())
        return reactivex.create(on_subscription)
    
    async def dbRequest(self,tipo,plate,badge,time):
        if tipo == RequestType.POLICY:
            if plate != "None":
                return selectPolicyFromVehicle(plate,time)
            elif badge != "None":
                return selectPolicyFromPerson(badge,time)
        
        elif tipo == RequestType.FIND_BADGE:
            if findBadgeInPersons(badge):
                return EventType.BADGE_OK
            else:
                return EventType.NO_GRANT
        
        elif tipo == RequestType.FIND_PLATE:
            if findPlateInVehicles(plate):
                return EventType.PLATE_OK
            else:
                return EventType.NO_GRANT
        
        elif tipo == RequestType.FIND_PLATE_BADGE:
            if findPlateAndBadge(plate,badge):
                return EventType.BADGE_PLATE_OK
            else:
                return EventType.NO_GRANT
        
        elif tipo == RequestType.INSERT_TRANSIT_HISTORY:
            idV = findIdVehicleFromPlate(plate)
            idP = findIdPersonFromBadge(badge)
            insertTransitHistory(idP,idV,time)
            return None
