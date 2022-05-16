import asyncio

from model.Devices import *
from utils.enums import *
from utils.gateFactory import *
from database.database_interactions import generateDbTest
from controller.lane_analyzer import TransitAnalyzer
from controller.logger import Logger
import reactivex

gateNord:Gate = None
 # lista di observables
laneObservables = []
# lista di observers
laneObservers = []

async def main():
    # GENERAZIONE DATASET DI PROVA
    generateDbTest(10)

    # creazione gate nord dalla classe factory
    gateNord:Gate = GateFactory.createGateNord()
    
    # per ogni lane
    for index, lane in enumerate(gateNord.getLanes()):
        # controllo se è attiva
        if lane.getLaneStatus() == LaneStatus.LANE_ACTIVE:
            observables = []
            # per ogni device
            for device in lane.getDevices():
                observables.append(device.createObservable())
            
            # merge degli oservable della lane
            laneObservables.append(reactivex.merge(*observables))
            # creazione analyzer e logger di linea
            if gateNord.executionMode == ExecutionMode.LOGGING:
                laneObservers.append(Logger(lane))
                laneObservables[index].subscribe(laneObservers[index])
            elif gateNord.executionMode == ExecutionMode.AUTOMATION:
                laneObservers.append(TransitAnalyzer(lane.analyzerConnection,lane))
                laneObservables[index].subscribe(laneObservers[index])
            else:
                laneObservers.append(TransitAnalyzer(lane.analyzerConnection, lane))
                laneObservers[index].createObservable().subscribe(Logger(lane))
                laneObservables[index].subscribe(laneObservers[index])
            
            
if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    loop.create_task(main())
    loop.run_forever()