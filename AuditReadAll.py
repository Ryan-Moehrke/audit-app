#find the patient as always
#query on observations

#query on allergy intolerence
#query on medication

#how to register app on graham
#get client id and password
#on server figure out how to get patient user
#logon to portal? with user
#auth this app for the user
#get tolken
#use tolken

#create, read, update, read, delete
#add provenance

from fhirclient import client
import fhirclient.models.fhirsearch as S
import fhirclient.models.patient as P
import fhirclient.models.observation as O
import fhirclient.models.auditevent as AE

def PatientSearch(client, struct=None):
    search = S.FHIRSearch(P.Patient, struct)
    patient = search.perform_resources(client.server)
    #print(len(patient))
    if len(patient) != 1:
        print(False)
        return False
    return patient[0].id

def PatientRead(client, patId):
    return P.Patient.read(patId, client.server)

def PatientCreate(client):
    print("PatCreate")
    jsondict = {
        "resourceType": "Patient",
        "text": {
            "status": "generated",
            "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">Ryan</div>"
            },
        "active": True,
        "name": [
            {
                "use": "official",
                "family": "Murky",
                "given": [
                    "Ryan"
                    ]
                }
            ],
        "gender": "male",
        "birthDate": "1974-12-25",
        "deceasedBoolean": False
        }
    
    return P.Patient(jsondict, strict=False).create(client.server)

def AuditSearch(client, struct=None):
    audit = AE.AuditEvent()
    search = S.FHIRSearch(audit, struct)
    bundle = search.perform(client.server)
    return bundle

def ObservationsSearch(client, struct=None):
    search = S.FHIRSearch(O.Observation, struct)
    return search.perform(client.server)

def ObservationCreate(client, patID):
    print("create")
    jsondict = {
  "resourceType": "Observation",
  "text": {
    "status": "generated"#,
 #   "div": "<div>Ryan Audit Test</div>"
    },
  "identifier": [
    {
      "use": "official",
      "system": "http://www.bmc.nl/zorgportal/identifiers/observations",
      "value": "632555"
    }
  ],
  "status": "final",
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "11557-6",
        "display": "Carbon dioxide in blood"
      }
    ]
  },
  "subject": {
    "reference": "Patient/" + patID
  },
##  "effectivePeriod": {
##    "start": "2013-04-02T10:30:10+01:00",
##    "end": "2013-04-05T10:30:10+01:00"
##  },
##  "issued": "2013-04-03T15:30:10+01:00",
  "performer": [
    {
      "reference": "Practitioner/f005",
      "display": "A. Langeveld"
    }
  ],
  "valueQuantity": {
    "value": 6.2,
    "unit": "kPa",
    "system": "http://unitsofmeasure.org",
    "code": "kPa"
  },
  "interpretation": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
          "code": "H",
          "display": "High"
        }
      ]
    }
  ],
  "referenceRange": [
    {
      "low": {
        "value": 4.8,
        "unit": "kPa",
        "system": "http://unitsofmeasure.org",
        "code": "kPa"
      },
      "high": {
        "value": 6.0,
        "unit": "kPa",
        "system": "http://unitsofmeasure.org",
        "code": "kPa"
      }
    }
  ]
}
    return O.Observation(jsondict, strict=False).create(client.server)

def ObservationRead(client, ObsId):
    print("read")
    struct = {
        '_id':ObsId
        }
    search = S.FHIRSearch(O.Observation, struct)
    return search.perform(client.server).entry[0].resource

def ObservationRead2(client, Observation):
    print("read2")
    return Observation.read(Observation.id, server=client.server)

def ObservationUpdate(client, Observation):
    print("update")
    Observation.valueQuantity.value = 6.3
    return Observation.update(client.server)
    

def ObservationDelete(client, Observation):
    print("delete")
    return Observation.delete(client.server)
    
def AuditCheck(client, Query):
    print(Query)
    audit = AuditSearch(client, Query)
    if not audit.entry:
        print("empty")
    else:
        print(len(audit.entry))
        for entry in audit.entry:
            from pprint import pprint
            pprint(entry.as_json())
##        for entry in audit.entry:
##            for agent in entry.resource.agent:
##                if agent.who:
##                    print(agent.who.identifier.value) if agent.who.identifier else agent.who.reference

    
    
###app setup
smart_defaults = {
    #'app_id':'Audit_Test_Bench',
    #'scope':'user/*.* openid profile',
    'app_id':'4d0dd077-70f4-4896-a2bd-b59aa2f7e02e',    #CE
    'app_secret':'porcupines',
    #'redirect_uri':'http://localhost:8000/fhir-app/',
    #'api_base':'http://test.fhir.org/r3',
    #'api_base':'http://test.fhir.org/r4',
    #'api_base':'http://hapi.fhir.org/baseDstu3'
    'api_base':'http://hapi.fhir.org/baseR4'
    #'api_base':'https://r4.test.pyrohealth.net/fhir'
	
	#'api_base': 'http://wildfhir4.aegis.net/fhir4-0-0'
	# NO -- wildfhir does not seem to auto create audit logs
	
	#'api_base': 'http://sqlonfhir-r4.azurewebsites.net/fhir'
	# ?? -- Telstr Health (HealthConnex) hung on creation of patient
	
	#'api_base': 'http://www.pknapp.com:8081/con19'
	# NO -- pknapp -- failure on patient create --- 400 client error : bsd request
	
	#'api_base': 'http://fhir.ext.apelon.com:7080/dts/fhir/'
	# NO -- apelon is just a termininology server
	
	#'api_base': 'http://sandbox.hspconsortium.org/'
	# NO -- HSPC ... -- somekind of error expectin a value
	
	#'api_base': 'http://fhir.tukan.online/'
	# NO -- Tukan -- failed on patient create
	
	#'api_base': 'https://fhir-open.stagingcerner.com/r4/0b8a0111-e8e6-4c26-a91c-5069cbc6b1ca/'
	# NO - Cerner -- failure on patient create
	
	#'api_base': 'http://r4.heliossoftware.com:8080'
	# NO -  Helios -- failure on patient create
	
	#'api_base': 'http://sandbox.bluebutton.cms.gov'
	# no - CMS -- FAILURE ON PATIENT CREATE
	
	#'api_base':'http://elsevier.demo.elsevierfhir.com/fhir'
	# NO - Elsevier - failure on patient create

	
    #'api_base':'https://fhir.careevolution.com/Master.Adapter1.WebClient/api/fhir-r4',
    #'patient_id':'1254099010',
    #'launch_token':'eyJhbGciIDogIlJTMjU2Iiwia2lkIiA6ICJodHRwczovL3Rlc3QuZmhpci5vcmcvcjQvYXV0aC9hdXRoX2tleSIsInR5cCIgOiAiSldUIn0.eyJleHAiIDogMTU2NzA1MDM3MCwiaWF0IiA6ICIxNTY3MDQ2OTI1IiwiaXNzIiA6ICJ0ZXN0LmZoaXIub3JnIiwianRpIiA6ICJ0ZXN0LmZoaXIub3JnL3Nlc3Npb25zLzUzMTA4In0.k4veGpcBqDBLZIU77nsuUi1YLaQGhV59_k9KKEHL0jxRRCJSFOSAMlghuIlQAMOqEwT1O-jy97vkg896P8U1sObnMLxtmhmveWC9uTA0tBv9f9tUt2D7xWFc6QtF2Rh15q1luNnK_Xi4g_HBmZjmfcDV0VquEjaawj661AKjIwMOwRnxx-x_Qd6vPaM-VHXPYMVbo3xB5aRKUs3gKdnwCiOsf7znomnYZXtAA7hDdOd5xQGDu-rGq-6jfdsCVOuZJ21sqhz97ifBvubxNGF7Wsdr7SzJLoglESUCt6SKQhflwT746O_j5c1yJRnS7maFEtDQc0YLfBGqar7om5etSQ'
}

print("settings: ")
print(smart_defaults)
print("\n")

client = client.FHIRClient(settings=smart_defaults)
print("client: ")
print (client)
print ("\n")

if client.prepare():
	print("ready: "  )

	CreatAudit = {
		'type': 'audit-event-type-rest'
		}
	AuditCheck(client, CreatAudit)


