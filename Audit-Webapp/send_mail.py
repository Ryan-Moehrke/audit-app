from google.cloud import storage

from fhirclient import client
import fhirclient.models.patient as P
import fhirclient.models.auditevent as AE
import fhirclient.models.fhirsearch as S
from fhirclient.models.fhirabstractbase import FHIRValidationError
import fhirclient.server as FHIRServer
from requests.exceptions import HTTPError


def PatientSearch(struct=None):
    servers = getListBucket("servers.txt")
##    'http://test.fhir.org/r4',
##    'https://r4.test.pyrohealth.net/fhir',
##    'http://hapi.fhir.org/baseR4',
##    
##    'http://wildfhir4.aegis.net/fhir4-0-0',
##    'http://www.pknapp.com:8081/con19',
##    'http://fhir.tukan.online/',
##    'http://sandbox.bluebutton.cms.gov',
##    'http://elsevier.demo.elsevierfhir.com/fhir/metadata',
##
##        #below have val errors but type:AuditEvent in their capability statements
##
##    'https://fhir.careevolution.com/Master.Adapter1.WebClient/api/fhir-r4', 
##    'http://sqlonfhir-r4.azurewebsites.net/fhir', 
##    'https://vhdir-demo.fhir.org/fhir', 
##        ]
    returnJson = {}
    for server in servers:
        returnJson[server] = {}
        try:
            smart = client.FHIRClient(settings={'app_id':'audit_app','api_base':server})
            if CheckServer(smart):
                
                search = S.FHIRSearch(P.Patient, struct)
                patList = search.perform_resources(smart.server)
                #I acknowledge that if the search comes back with more than one bundle of patients this won't catch them all, but I hope that never happens
                for pat in patList:
                    returnJson[server][pat.id] = {}
            else:
                returnJson[server] = "Does not implement AuditEvents"
        except HTTPError as e:
            returnJson[server]["http error"] = str(e.response.status_code)
        except FHIRValidationError as e:
            returnJson[server]["Validation error"] = e.errors
##        except FHIRServer.FHIRUnauthorizedException as e:
##            returnJson[server]["http error"] = e.response.status_code
##        except FHIRServer.FHIRPermissionDeniedException:
##            returnJson[server]["http error"] = e.response.status_code
##        except FHIRServer.FHIRNotFoundException:
##            returnJson[server]["http error"] = str(e.response.status_code)
        
    return returnJson   #dict form of {server:{patient:{}}}
                        #where the extra dict inside of patient will be filled later
                        #in the event of an error, the error message will replace patient

def CheckServer(smart):
    CS = smart.server.capabilityStatement
    for fmt in CS.format:
        if fmt.endswith("json"):
            
            for rst in CS.rest:
                if rst.mode == "server":
                
                    for res in rst.resource:
                        if res.type == "AuditEvent":
                            return True

                                    
##                            if rst.security.service:
##                                print(rst.security.service)
##                                for srv in rst.security.service:
##                                    if srv:
##                                        print(srv.description) #and stop srv
    return False

def AuditSearch(pat, server):
    smart = client.FHIRClient(settings={'app_id':'audit_app','api_base':server})
    search = S.FHIRSearch(AE.AuditEvent, {'patient':pat}) #?
    bundle = search.perform(smart.server)
    return bundle

def SumAuditType(server, bundle): #include rest summary
    key = {}
    smart = client.FHIRClient(settings={'app_id':'audit_app','api_base':server})
    while bundle is not None and bundle.entry:
        for entry in bundle.entry:
            if not entry.resource.type.code == "rest":
                if entry.resource.type.code in key:
                    key[entry.resource.type.code] += 1
                else:
                    key[entry.resource.type.code] = 1
            else:
                if not "rest" in key:
                    key["rest"] = {}
                if not entry.resource.subtype:
                    try:
                        key["rest"]['null'] += 1
                    except KeyError:
                        key["rest"]['null'] = 1
                else:
                    for subtype in entry.resource.subtype:
                        if not subtype.code:
                            try:
                                key["rest"]['null'] += 1
                            except KeyError:
                                key["rest"]['null'] = 1
                        else:
                            try:
                                key["rest"][subtype.code] += 1
                            except KeyError:
                                key["rest"][subtype.code] = 1

        bundle = NextBundle(smart, bundle)
    return key

def NextBundle(client, bundle):
    from fhirclient.models import bundle as BS
    res = None
    for link in bundle.link:
        if link.relation == "next":
            res = client.server.request_json(link.url)
            break
    if res:
        NewBundle = BS.Bundle(res, strict=False)
        NewBundle._server = client
        return NewBundle
    else:
        return None


def SendErrorMail(person):
    import smtplib
    from email.message import EmailMessage
    msg = EmailMessage()
    msg.set_content("""Dear {Given} {Family},
No Patient found with name: {Given} {Family}
""".format(Given=person["Given"],Family=person["Family"]))
    msg['Subject'] = "Patient Not Found"
    msg['To']="{Given} {Family} <{Email}>".format(Given=person["Given"],
                                                  Family=person["Family"],
                                                  Email=person["Email"])
    return sendSMTP(msg)


def SendSummaryMail(person, sumJson):
    from pprint import pformat
    import smtplib
    from email.message import EmailMessage
    msg = EmailMessage()
    msg.set_content("""Dear {Given} {Family},
{summary}
Thanks,
Management""".format(Given=person["Given"],
                     Family=person["Family"],
                     summary=pformat(sumJson)
        ))
    msg['To']="{Given} {Family} <{Email}>".format(Given=person["Given"],
                                                  Family=person["Family"],
                                                  Email=person["Email"])
    msg['Subject']="Audits Found"

    return sendSMTP(msg)

def sendSMTP(msg):
    import smtplib, ssl

    email = getJsonBucket("app-email.json")    

    port = 465
    From = email["From"]
    Password = email["Password"]

    msg['From'] = From
    
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(From, Password)

        
        server.send_message(msg)
        server.quit()
        return True

def getJsonBucket(path):
    bucket_name = "fhir-audit-app.appspot.com"
    
    blob = storage.Client().get_bucket(bucket_name).blob(path)

    import json
    jstring = blob.download_as_string()
    return json.loads(jstring)

def getListBucket(path):
    bucket_name = "fhir-audit-app.appspot.com"
    entries = []
    blob = storage.Client().get_bucket(bucket_name).blob(path)

    lines = blob.download_as_string().decode()
    entries = lines.splitlines()
    return entries

def app():
    Mailing = getJsonBucket("email.json")
    
##    Mailing = [
##        {'"Given":"Every",
##         "Family":"Woman",
##         "Email":"Everywoman@gmail.com"},
##        {'"Given":"Every",
##         "Family":"Man",
##         "Email":"Everyman@gmail.com"}
##        ]

    for person in Mailing:
        sumJson = {}
        patient = PatientSearch({'given':person["Given"],'family':person["Family"]})
        if len(patient) == 0:
            SendErrorMail(person)
        else:
            for pat, server in patient.items():
                if not isinstance(pat, str):
                    sumJson[server] = "Http error: {}".format(pat)
                else:
                    try:
                        AuditBundle = AuditSearch(pat, server)
                        if AuditBundle.entry:
                            sumJson[pat] = SumAuditType(server, AuditBundle)
                            #as is doesn't tell user it found a pat if they have no audits associated
     
                    except FHIRValidationError as e:
                        sumJson[pat] = e.errors
                        #doesnt tell user anything that passed on the pat if there is an error
                    except HTTPError as e:
                        sumJson[pat] = "Http Error: {}".format(e.response.status_code)
            SendSummaryMail(person,sumJson)
    return 'Sent an email to {} {}.'.format(person["Given"],person["Family"])
def sendSingleMail(person, debug=False):
##    person = {'"Given":"Every",
##              "Family":"Woman",
##              "Email":"Everywoman@gmail.com"}
    returnJson = PatientSearch({'given':person["Given"],'family':person["Family"]})
    if len(returnJson) == 0:
        SendErrorMail(returnJson)
    else:
        for server, pats in returnJson.items():
            for pat, audits in pats.items():
                if pat.endswith("error"):
                    if not debug:
                        pats.pop(pat)
                else:
                    try:
                        AuditBundle = AuditSearch(pat, server)
                        if AuditBundle.entry:
                            returnJson[server][pat] = SumAuditType(server, AuditBundle)
                        else:
                            returnJson[server][pat] = "No Audits Found"
                        
                    except FHIRValidationError as e:
                        returnJson[server][pat]["Validation Error"] = e.errors
                    except HTTPError as e:
                        returnJson[server][pat]["Http Error"] = str(e.response.status_code)
        SendSummaryMail(person,returnJson)
    return 'Sent an email to {} {}.'.format(person["Given"],person["Family"])

