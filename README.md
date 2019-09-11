# audit-app

This repository is for development of consumer (Patient) focused applications that leverage FHIR AuditEvent and Provennce to keep the patient informed about how their data are being used.  https://healthcaresecprivacy.blogspot.com/2019/06/patient-engagement-access-log.html

Hopefully there will be something worthy of the Patient Innovator Track at DevDays https://healthcaresecprivacy.blogspot.com/2019/08/the-patient-innovator-track-at-devdays.html

# Pre-condition for Python aspp
Requires FHIR Python toolkit.  Note the pip for R4 seems to be broken, so here is what he did. (the pip seemed to work before for STU3)

1. must have python installed from python.org
2. Start  https://github.com/smart-on-fhir/client-py 
3. go to the R4 branch https://github.com/smart-on-fhir/client-py/tree/feature/r4
4. download the whole thing (clone the repository locally... possibly using just zip and extract)
5. run the "setup"
   > python setup.ph install

# Test application
## AuditWrite.py
* create a Patient (there is an option for using an existing Patient)
* create an Observation
* Read the Observation
* Update the Observation
* Read the Observation
* Delete the Observation
* Pause to allow audits to be created lazy
* Read all auditEvent for 

This app is not yet enabled with OAuth, so it needs anonymous access

## Results
### Grahame's server 
works now
Initially auditEvent did not have .entity with Patient identified. This inspired GF#23835
https://chat.fhir.org/#narrow/stream/179247-Security-and.20Privacy
### Pyro server 
works now
Initially the AuditEvent were not valid with problems with the .text div
### Fire.ly Vonk server 
does NOT auto create audit logs
### HAPI server
does not auto create audit logs
https://chat.fhir.org/#narrow/stream/179167-hapi/topic/automatic.20Audit.20logs
