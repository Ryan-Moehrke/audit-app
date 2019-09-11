from google.cloud import storage

from fhirclient import client
import fhirclient.models.patient as P
import fhirclient.models.auditevent as AE
import fhirclient.models.fhirsearch as S
from fhirclient.models.fhirabstractbase import FHIRValidationError
from requests.exceptions import HTTPError


def PatientSearch(struct=None):
    servers = [
        'http://test.fhir.org/r4',
        'http://hapi.fhir.org/baseR4',
        'https://r4.test.pyrohealth.net/fhir'
        ]
    patient = {}
    for server in servers:
        try:
            smart = client.FHIRClient(settings={'app_id':'audit_app','api_base':server})
            search = S.FHIRSearch(P.Patient, struct)
            patList = search.perform_resources(smart.server)
            #I acknowledge that if the search comes back with more than one bundle of patients this won't catch them all, but I hope that never happens
            for pat in patList:
                patient[pat.id] = server
        except HTTPError as e:
            patient[e.response.status_code] = server
    return patient  #dict format of {"patID":"fhirserver.org"}
                    #will have duplicate server values for multiple patients per server
                    #if http errors the entry will be {404 error_code:"fhirserver.org"}

def AuditSearch(pat, server):
    smart = client.FHIRClient(settings={'app_id':'audit_app','api_base':server})
    search = S.FHIRSearch(AE.AuditEvent, {'patient':pat}) #?
    bundle = search.perform(smart.server)
    return bundle

def SumAuditType(server, bundle):
    key = {}
    smart = client.FHIRClient(settings={'app_id':'audit_app','api_base':server})
    while bundle is not None and bundle.entry:
        for entry in bundle.entry:
            if entry.resource.type.code in key:
                key[entry.resource.type.code] += 1
            else:
                key[entry.resource.type.code] = 1
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
    msg.set_content("""Dear {Name},
No Patient found with name: {Name}
""".format(Name=person["Name"]))

    msg['Subject'] = "Patient Not Found"
    msg['To'] = "{} <{}>".format(person["Name"], person["Email"])

    return sendSMTP(msg)


def SendSummaryMail(person, sumJson):
    from pprint import pformat
    import smtplib
    from email.message import EmailMessage
    msg = EmailMessage()
    msg.set_content("""Dear {Name},
{pat} patients found with audits
{summary}
Thanks,
Management""".format(Name=person["Name"],
                     pat=len(sumJson),
                     summary=pformat(sumJson)
        ))
    msg['To']="{} <{}>".format(person["Name"], person["Email"])
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

def app():
    Mailing = getJsonBucket("email.json")
    
##    Mailing = [
##        {'Name':'Everywoman',
##         "Email":"Everywoman@gmail.com"},
##        {"Name":"Everyman",
##         "Email":"Everyman@gmail.com"}
##        ]

    for person in Mailing:
        sumJson = {}
        patient = PatientSearch({'name':person["Name"]})
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
    return 'Sent an email to {}.'.format(person["Name"])
