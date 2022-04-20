import asyncio

from classes import *
from enums import *
from gateFactory import *
from reactivex import Observable
from database_interactions import findAllVehicles,printVehicles,insertRandomVehicles,insertRandomPeoples
from lane_analyzer import TransitAnalyzer

gateNord:Gate = None
 # lista di observables
laneObservables = [Observable]
# lista di observers
laneAnalyzers = [TransitAnalyzer]


async def main():
    insertRandomPeoples(50)
    
    print("questi sono i veicoli:")
    printVehicles(findAllVehicles())
    # creazione gate nord dalla classe factory
    gateNord = GateFactory.createGateNord()
    lane = gateNord.getLanes()[0]
    observables = []
    for device in lane.getDevices():
        print(device)
        observables.append(device.createObservable())
    laneObservable = reactivex.merge(*observables)
    trans = TransitAnalyzer(Connection())
    laneObservable.subscribe(trans)

    '''if gateNord != None:
        # per ogni lane del gate
        for index,lane in enumerate(gateNord.getLanes()):
            # se la lane è attiva
            if lane.getLaneStatus() == LaneStatus.LANE_ACTIVE:
                # observable di ogni lane
                observables = [Observable]
                print("sto per creare gli observables")
                # creo un observable a partire da ogni device di ogni lane
                for device in lane.getDevices():
                    observables.append(device.createObservable())
                
                # effettuo il merge degli observable di una stessa lane
                laneObservables.append(reactivex.merge(*observables))
                # creazione observable associato alla lane
                laneAnalyzers.append(TransitAnalyzer(Connection()))
                # sottoscrivo un analyzer per ogni lane
                laneObservables[index].subscribe(laneAnalyzers[index])
            '''
if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    loop.create_task(main())
    loop.run_forever()