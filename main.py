import asyncio

from classes import *
from enums import *
from gateFactory import *
from reactivex import Observable
from database_interactions import generateDbTest
from lane_analyzer import TransitAnalyzer
from logger import Logger

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
    for lane in gateNord.getLanes():
        # controllo se è attiva
        if lane.getLaneStatus() == LaneStatus.LANE_ACTIVE:
            observables = []
            # per ogni device
            for device in lane.getDevices():
                observables.append(device.createObservable())
            
            # merge degli oservable della lane
            laneObservable = reactivex.merge(*observables)
            # creazione analyzer e logger di linea
            if gateNord.loggingMode:
                laneObservable.subscribe(Logger(lane))
            else:
                laneObservable.subscribe(TransitAnalyzer(lane.analyzerConnection,lane))
            
if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    loop.create_task(main())
    loop.run_forever()