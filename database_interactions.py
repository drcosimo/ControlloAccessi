from os import curdir
import random 
import string

from database_connection import DatabaseConnection
from custom_errors import NotUniqueException
import uuid


DATABASE_NAME = "database.db"

"""
Metodi utilizzati per gestire le interazioni con il database
"""

###################### METODI PER LA CREAZIONE DEL DB ######################

def createPersonTable():
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS Person("
                        "IdPerson INTEGER PRIMARY KEY, "
                        "CF varchar(16), "
                        "Name varchar(255), "
                        "Surname varchar(255), "
                        "DateOfBirth date, "
                        "City varchar(255), "
                        "Badge varchar(255) UNIQUE NOT NULL)")


def createVehicleTable():
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS Vehicle("
                        "IdVehicle INTEGER PRIMARY KEY, "
                        "Plate varchar(7) NOT NULL UNIQUE, "
                        "Brand varchar(255), "
                        "Model varchar(255), "
                        "Color varchar(255))")


def createPersonVehicleTable():
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS PersonVehicle("
                        "IdPerson INTEGER, "
                        "IdVehicle INTEGER, "
                        "PRIMARY KEY (IdPerson, IdVehicle)"
                        "FOREIGN KEY(IdPerson) REFERENCES Person(IdPerson), "
                        "FOREIGN KEY(IdVehicle) REFERENCES Vehicle(IdVehicle))")


def createPolicyTable():
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS Policy(GrantPolicy INTEGER PRIMARY KEY)")


def createPersonPolicyTable():
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS PersonPolicy("
                        "IdPersonPolicy INTEGER PRIMARY KEY, "
                        "IdPerson INTEGER NOT NULL, "
                        "GrantPolicy INTEGER NOT NULL, "
                        "StartTime TIME , "
                        "EndTime TIME, "
                        "FOREIGN KEY(IdPerson) REFERENCES Person(IdPerson), "
                        "FOREIGN KEY(GrantPolicy) REFERENCES Policy(GrantPolicy))")


def createVehiclePolicyTable():
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS VehiclePolicy("
                        "IdVehiclePolicy INTEGER PRIMARY KEY, "
                        "IdVehicle INTEGER NOT NULL, "
                        "GrantPolicy INTEGER NOT NULL, "
                        "StartTime TIME , "
                        "EndTime TIME , "
                        "FOREIGN KEY(IdVehicle) REFERENCES Vehicle(IdVehicle))")


def createTransitHistoryTable():
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS TransitHistory("
                        "IdTransit INTEGER PRIMARY KEY, "
                        "IdPerson INTEGER, "
                        "IdVehicle INTEGER, "
                        "TransitDate DATE NOT NULL, "
                        "FOREIGN KEY(IdPerson) REFERENCES Person(IdPerson), "
                        "FOREIGN KEY(IdVehicle) REFERENCES Vehicle(IdVehicle))")


###################### METODI PER L'INSERIMENTO DEI DATI ######################

def insertPerson(cf, name, surname, birthdate, city, badge):
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("INSERT INTO Person (CF, Name, Surname, DateOfBirth, City, Badge)"
                        " VALUES (?, ?, ?, ?, ?, ?)", (cf, name, surname, birthdate, city, badge,))


def insertVehicle(plate, brand, model, color):
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("INSERT INTO Vehicle (Plate, Brand, Model, Color) VALUES (?, ?, ?, ?)",
        (plate, brand, model, color,))


def insertPersonVehicle(idperson, idvehicle):
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("INSERT INTO PersonVehicle (IdPerson, IdVehicle) VALUES (?, ?)", (idperson, idvehicle,))


def insertPolicy():
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("INSERT INTO Policy (GrantPolicy) VALUES (1), (2), (3)")


def insertPersonPolicy(idperson, grantpolicy, start, end):
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("INSERT INTO PersonPolicy (IdPerson, GrantPolicy, StartTime, EndTime) "
                        "VALUES (?, ?, ?, ?)", (idperson, grantpolicy, start, end,))


def insertVehiclePolicy(idvehicle, grantpolicy, start, end):
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("INSERT INTO VehiclePolicy (IdVehicle, GrantPolicy, StartTime, EndTime) "
                        "VALUES (?, ?, ?, ?)", (idvehicle, grantpolicy, start, end,))


def insertTransitHistory(idPerson, idVehicle, date):
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("INSERT INTO TransitHistory (IdPerson, IdVehicle, TransitDate) "
                        "VALUES (?, ?, ?)", (idPerson, idVehicle, date,))


def insertRandomPeoples(number):
    for i in range(number):   
        with DatabaseConnection(DATABASE_NAME) as connection:
            cursor = connection.cursor()
            badge = str(uuid.uuid1())
            cursor.execute("INSERT INTO Person(Badge) VALUES (?)", (badge,))
            id = findIdPersonFromBadge(badge)
            randPolicy = random.randint(1,4)
            cursor.execute("INSERT INTO PersonPolicy(IdPerson,GrantPolicy) VALUES(?,?)", (id,randPolicy,))

def insertRandomVehicles(number):
    for i in range(number):
        with DatabaseConnection(DATABASE_NAME) as connection:
            cursor = connection.cursor()            
            plate = createRandomPlate()
            cursor.execute("INSERT INTO Vehicle(Plate) VALUES (?)", (plate,))
            id = findIdVehicleFromPlate(plate)
            randPolicy = random.randint(1,4)
            cursor.execute("INSERT INTO VehiclePolicy(IdVehicle,GrantPolicy) VALUES(?,?)", (id,randPolicy,))


def updateVehicleOfPerson(idperson, idvehicle):
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("UPDATE PersonVehicle SET IdVehicle = ? WHERE IdPerson = ?", (idvehicle, idperson,))


###################### METODI PER LE INTERROGAZIONI ######################
def findIdPersonFromBadge(badge):
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT IdPerson FROM Person AS p WHERE p.badge = ?", (badge,))

        result = cursor.fetchall()

        if len(result) > 1:
            raise NotUniqueException("Il badge inserito non è unico")
        elif len(result) == 0:
            return None

    return result[0][0]


def findIdVehicleFromPlate(plate):
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT IdVehicle FROM Vehicle AS v WHERE v.plate = ?", (plate,))

        result = cursor.fetchall()

        if len(result) > 1:
            raise NotUniqueException("La targa inserita non è unica")
        elif len(result) == 0:
            return None

    return result[0][0]


def selectPolicyFromPerson(badge, actualTime):

    idperson = findIdPersonFromBadge(badge)

    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT p.GrantPolicy FROM Policy AS p INNER JOIN PersonPolicy AS pp "
                        "ON pp.GrantPolicy = p.GrantPolicy WHERE pp.IdPerson = ? "
                        "AND ? BETWEEN pp.StartTime AND pp.EndTime", (idperson,actualTime,))

        result = cursor.fetchall()

    if len(result) > 1:
        raise NotUniqueException("La policy cercata non è unica")

    return int(result[0][0])
        

def selectPolicyFromVehicle(plate, actualTime):

    idvehicle = findIdVehicleFromPlate(plate)

    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT p.GrantPolicy FROM Policy AS p INNER JOIN VehiclePolicy AS vp "
                        "ON vp.GrantPolicy = p.GrantPolicy WHERE vp.IdVehicle = ? "
                        "AND ? BETWEEN vp.StartTime AND vp.EndTime", (idvehicle,actualTime,))
        
        result = cursor.fetchall()

    if len(result) > 1:
        raise NotUniqueException("La policy cercata non è unica")

    return int(result[0][0])


def findPlateAndBadge(plate, badge):
    idperson = findIdPersonFromBadge(badge)
    idvehicle = findIdVehicleFromPlate(plate)

    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM PersonVehicle "
                        "WHERE IdPerson = ? AND IdVehicle = ?", (idperson, idvehicle,))
        result = cursor.fetchall()

    if len(result) == 0:
        return False
    elif len(result) == 1:
        return True

        
# Estrae una targa in maniera random dal database
def extractRandomPlate():
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM Vehicle")
        numbersVehicle = int(cursor.fetchall()[0][0])

        randomIndex = random.randint(1, numbersVehicle)
        cursor.execute("SELECT Plate FROM Vehicle AS V WHERE V.IdVehicle = ?", (randomIndex,))
        result = cursor.fetchall()

    return result[0][0]

def extractRandomBadge():
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM Person")
        numbersPerson = int(cursor.fetchall()[0][0])

        randomIndex = random.randint(1, numbersPerson)
        cursor.execute("SELECT Badge FROM Person AS P WHERE P.IdPerson = ?", (randomIndex,))
        result = cursor.fetchall()

    return result[0][0]

def findAllPersons():
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM Person")
        result = cursor.fetchall()

    return result


def findAllVehicles():
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM Vehicle")
        result = cursor.fetchall()

    return result


def findPolicy():
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM Policy")
        result = cursor.fetchall()

    return result


def findPersonPolicy(idperson):
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT GrantPolicy FROM PersonPolicy WHERE IdPerson = ?", (idperson,))
        result = cursor.fetchall()

    return result

    
def findVehiclePolicy(idvehicle):
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT GrantPolicy FROM VehiclePolicy WHERE IdVehicle = ?", (idvehicle, ))
        result = cursor.fetchall()

    return result


def deleteVehiclePolicy(idvehiclepolicy):
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("DELETE FROM VehiclePolicy WHERE 1 = ?", (idvehiclepolicy,))


def findAllPersonVehicle():
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM PersonVehicle")
        result = cursor.fetchall()

    return result


def findAllTransits():
    with DatabaseConnection(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM TransitHistory")
        result = cursor.fetchall()

    return result



###################### METODI DI UTILITA' ######################
def createAllTables():
    with DatabaseConnection(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS {0}".format("Person"))
        cursor.execute("DROP TABLE IF EXISTS {0}".format("Vehicle"))
        cursor.execute("DROP TABLE IF EXISTS {0}".format("PersonVehicle"))
        cursor.execute("DROP TABLE IF EXISTS {0}".format("PersonPolicy"))
        cursor.execute("DROP TABLE IF EXISTS {0}".format("VehiclePolicy"))
        cursor.execute("DROP TABLE IF EXISTS {0}".format("Policy"))
        cursor.execute("DROP TABLE IF EXISTS {0}".format("TransitHistory"))
        
        
    createPersonTable()
    createVehicleTable()
    createPersonVehicleTable()
    createPolicyTable()
    createPersonPolicyTable()
    createVehiclePolicyTable()
    createTransitHistoryTable()


def findPlateInVehicles(plate):
    if findIdVehicleFromPlate(plate) is not None:
        return True
    else:
        return False


def findBadgeInPersons(badge):
    if findIdPersonFromBadge(badge) is not None:
        return True
    else:
        return False


def createRandomPlate():
    firsts_letters = "".join([random.choice(string.ascii_letters) for i in range(2)])
    numbers = "".join([random.choice(string.digits) for i in range(3)])
    lasts_letters = "".join([random.choice(string.ascii_letters) for i in range(2)])

    plate = firsts_letters.upper() + numbers + lasts_letters.upper()

    return plate


def printPersons(persons):
    for person in persons:
        print(f"ID: {person[0]} \nBadge: {person[6]}")


def printVehicles(vehicles):
    for vehicle in vehicles:
        print(f"ID: {vehicle[0]} \nPlate: {vehicle[1]}")
