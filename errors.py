# In questo file verranno inseriti tutti gli errori custom

class CustomErrors(Exception):
    def __init__(self, message):
        self.message = message

    def addInLogger(self):
        pass
        # TODO: implementare l'aggiunta dell'errore nel logger


class AlreadyInitialized(CustomErrors):
    """ Eccezione che viene sollevata quando si cerca di inializzare una variabile già inizializzata """
    def __init__(self, message):
        super().__init__(message)
    
    def addInLogger(self):
        # TODO: in che formato viene inserito l'errore nel logger?
        super().addInLogger()
        