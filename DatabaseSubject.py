import asyncio
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
                peer = writer.get_extra_info("peername")
                data = await reader.readline()
                text = data.decode(encoding="utf-8")
                # one time request, closing connection
                writer.close()
                await writer.wait_closed()
                print("Database Subject, received {0} from {1}".format(text,peer))
                # type of request, and value associated
                type,plate,badge,time = text.split(",")
                
                result = await self.dbRequest(int(type),plate,badge,time)
                
                evtType = "EventType.{0}".format(EventType(result).name)
                # create event
                evt = Event("{0},{1}".format(plate,badge),evtType,DeviceType.SERVER)
                print("submitting event {0}".format(evt.toString()))
                observer.on_next(evt)

            asyncio.create_task(connect())
        return reactivex.create(on_subscription)
    
    async def dbRequest(self,type,plate,badge,time):
        if type == RequestType.POLICY.value:
            if plate != "None":
                return selectPolicyFromVehicle(plate,time)
            elif badge != "None":
                return selectPolicyFromPerson(badge,time)
        
        elif type == RequestType.FIND_BADGE.value:
            if findBadgeInPersons(badge):
                return EventType.BADGE_OK
            else:
                return EventType.NO_GRANT
        
        elif type == RequestType.FIND_PLATE.value:
            if findPlateInVehicles(plate):
                return EventType.PLATE_OK
            else:
                return EventType.NO_GRANT
        
        elif type == RequestType.FIND_PLATE_BADGE.value:
            if findPlateAndBadge(plate,badge):
                return EventType.BADGE_PLATE_OK
            else:
                return EventType.NO_GRANT
        
        elif type == RequestType.INSERT_TRANSIT_HISTORY.value:
            idV = findIdVehicleFromPlate(plate)
            idP = findIdPersonFromBadge(badge)
            insertTransitHistory(idP,idV,time)
        
        return "non entra da nessuna parte"