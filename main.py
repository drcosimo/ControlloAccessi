import asyncio

from classes import *
from enums import *
from gateFactory import *
from reactivex import Observable, Subject

gateNord:Gate = None
 # lista di observables
laneObservables = [Observable]
# lista di observers
laneAnalyzers = [Subject]


async def main():
    # creazione gate nord dalla classe factory
    gateNord = GateFactory.createGateNord()
    if gateNord != None:
        gateNord.getLane(0).activateLane()
        
        obs = gateNord.getLane(0).getDevice(0).createObservable()
        obs.subscribe(TestAnalyzer(gateNord.getLane(0)))
        # per ogni lane del gate
        for index,lane in enumerate(gateNord.getLanes()):
            # se la lane è attiva
            if lane.getLaneStatus() == LaneStatus.LANE_ACTIVE:
                # observable di ogni lane
                observables = [Observable]

                # creo un observable a partire da ogni device di ogni lane
                for device in lane.getDevices():
                    observables.append(device.createObservable())
                
                # effettuo il merge degli observable di una stessa lane
                laneObservables.append(reactivex.merge(*observables))
                # creazione observable associato alla lane
                laneAnalyzers.append(Analyzer(lane))
                # sottoscrivo un analyzer per ogni lane
                laneObservables[index].subscribe(laneAnalyzers[index])

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    loop.create_task(main())
    loop.run_forever()