from datetime import datetime
import database_interactions as database
import random
import time

#database.createAllTables()


# database.insertRandomPeople()
# database.printPersons(database.findAllPersons())
# database.insertVehicle("AA123BB", "BMW", "M3", "Red")
# print(database.findIdVehicleFromPlate("AA123BB"))
# database.printVehicles(database.findAllVehicles())


# def random_date(seed):
#     random.seed(seed)
#     d = random.randint(1, int(time.time()))
#     return datetime.fromtimestamp(d).strftime('%Y-%m-%d')

# # print(random_date(1))
# database.updateVehicleOfPerson(2, 15)
# print(database.findAllPersonVehicle())

# database.insertTransitHistory(2, 15, datetime.now())
# print(database.findAllTransits())

# print(database.findAllPersons()[4])
# print(database.findAllVehicles()[4])
# print(database.findAllVehicles()[15])

# print(database.findPlateAndBadge(badge = "cc457344-ba4d-11ec-a178-28f10e16f9b5", plate = "HV777JQ"))
# print(database.findPlateAndBadge(badge = "cc457344-ba4d-11ec-a178-28f10e16f9b5", plate = "SM783MM"))

# database.printVehicles(database.findAllVehicles())
# print(database.selectPolicyFromVehicle("AA123BB", "12:30:00"))


# database.insertPolicy()
# database.insertRandomPeoples(10)
# database.insertRandomVehicles(10))

# database.insertRandomPeoples(10)
# database.insertPolicyToPeoples()
# database.insertRandomVehicles(1)
# database.insertPolicyToVehicles()
database.generateDbTest(3)
print(database.findAllVehicles())
print(database.findAllPersons())
print(database.findAllPersonVehicle())

