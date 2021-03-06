import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
from bson.code import Code
from geopy.distance import vincenty
import geopy


class transformation0(dml.Algorithm):
    contributor = 'aditid_benli95_teayoon_tyao'
    reads = ['aditid_benli95_teayoon_tyao.schoolsMaster', 'aditid_benli95_teayoon_tyao.allDrugCrimesMaster']
    writes = ['aditid_benli95_teayoon_tyao.drugCrimeDensityBySchool']

    @staticmethod
    def execute(trial = False):

        startTime = datetime.datetime.now()
        
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('aditid_benli95_teayoon_tyao', 'aditid_benli95_teayoon_tyao')
        
        #start
        schoolsMaster = repo.aditid_benli95_teayoon_tyao.schoolsMaster
        allDrugCrimesMaster = repo.aditid_benli95_teayoon_tyao.allDrugCrimesMaster


        schools = schoolsMaster.find()
        dCrimes = allDrugCrimesMaster.find()

        schoolList = []
        
        for school in schools:
            schoolName = school["schoolName"]             
            slocation = (school["latitude"],school["longitude"])
            closestCrimes = [1000]*40
            for crime in dCrimes:
                dist = vincenty(slocation, (crime['latitude'], crime['longitude']))
                index = closestCrimes.index(max(closestCrimes))
                if (dist < closestCrimes[index]):
                    closestCrimes[index] = dist
        
            averageCrimeDist = sum(closestCrimes)/40
            schoolList.append([schoolName,averageCrimeDist])
            denseSchool = ([schoolName,averageCrimeDist])
            repo.aditid_benli95_teayoon_tyao.drugCrimeDensityBySchool.insert_one(denseSchool)






         
        


        
        repo.logout()

        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}


    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        

         # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('aditid_benli95_teayoon_tyao', 'aditid_benli95_teayoon_tyao')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('cob', 'https://data.cityofboston.gov/resource/')
        doc.add_namespace('bod', 'http://bostonopendata.boston.opendata.arcgis.com/datasets/')

        this_script = doc.agent('alg:aditid_benli95_teayoon_tyao#densityCalcreator', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        calDen = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime, {'prov:label':'Calculate Density', prov.model.PROV_TYPE:'ont:Computation'})
        doc.wasAssociatedWith(calDen, this_script)
        
        schoolsMaster = doc.entity('dat:aditid_benli95_teayoon_tyao#schoolsMaster', {'prov:label':'All Schools', prov.model.PROV_TYPE:'ont:Dataset'})
        doc.usage(calDen, schoolsMaster, startTime)

        allDrugCrimesMaster = doc.entity('dat:aditid_benli95_teayoon_tyao#allDrugCrimesMaster', {'prov:label':'All Drug Crime Incident Reports', prov.model.PROV_TYPE:'ont:Dataset'})
        doc.usage(calDen, allDrugCrimesMaster, startTime)

        drugCrimeDensityBySchool = doc.entity('dat:aditid_benli95_teayoon_tyao#drugCrimeDensityBySchool', {'prov:label':'Crime Density of Each School', prov.model.PROV_TYPE:'ont:Dataset'})

        doc.wasAttributedTo(drugCrimeDensityBySchool, this_script)
        doc.wasGeneratedBy(drugCrimeDensityBySchool, calDen, endTime)
        doc.wasDerivedFrom(drugCrimeDensityBySchool, schoolsMaster, calDen, calDen, calDen)
        doc.wasDerivedFrom(drugCrimeDensityBySchool, allDrugCrimesMaster, calDen, calDen, calDen)

        repo.record(doc.serialize()) # Record the provenance document.
        repo.logout()

        return doc

densityCalcreator.execute()
doc = densityCalcreator.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
