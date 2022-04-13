import datetime
from database.custom_errors import AlreadyInitialized, CustomErrors
from reactivex import Subject

class TransitAnalyzer(Subject):

    def __init__(self, plate, badge):
        self.actualPlate = plate
        self.actualBadge = badge


    # Funzione che ha il compito di di assegnare un valore alla targa se essa non ha ancora un valore
    def setActualPlate(self, plate):
        if self.actualPlate is None:
            self.actualPlate = plate
        elif self.actualPlate != plate:
            raise AlreadyInitialized("E' stato già assegnato un valore alla targa")


    # Funzione che ha il compito di di assegnare un valore al badge se esso non ha ancora un valore
    def setActualBadge(self, badge):
        if self.actualBadge is None:
            self.setActualBadge = badge
        else:
            raise AlreadyInitialized("E' stato già assegnato un valore al badge")


    def on_next(self, event):
        if event is not None:
            self.analyze(event)
        else:
            raise TypeError("L'evento passato risulta NULL")


    def on_error(self, error):
        print(f"E' stato rilevato un errore: {error}")    # TODO: Gestire tramite console oppure tramite logger?


    def on_completed(self):
        print("Evento completato")    # TODO: Gestire tramite console oppure tramite logger?

    
    def analyze(self, event): # TODO: aggiungere il tipo all'event
        self.inTransit = True
        self.startTimeTransit = datetime.now()
        
        if event.eventType == "READ_FRONT_PLATE" or event.evenType == "READ_REAR_PLATE":
            try:
                self.setActualPlate(event.value)
            except CustomErrors as ce:
                ce.addInLogger()
            except Exception:
                pass
                # TODO: errore da inviare al logger

        if event.eventType == "READ_PERSON_CREDENTIALS":
            try:
                self.setActualBadge(event.value)
            except CustomErrors as ce:
                ce.addInLogger()
            except Exception:
                pass
                # TODO: errore da inviare al logger

        if event.eventType == "MANUAL_OPEN_BAR":
            self.cleanAnalyzer()
            return
        
        # Controllo la policy




    def cleanAnalyzer(self):
        self.actualPlate = None
        self.actualBadge = None
        self.inTransit = False
        self.startTimeTransit = None
        self.endTimeTransit = None