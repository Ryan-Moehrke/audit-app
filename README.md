# audit-app

Requires FHIR Python toolkit 
Here is what my son says he did... Note the pip for R4 seems to be broken, so here is what he did. (the pip seemed to work before for STU3)

must have python installed from python.org

Start  https://github.com/smart-on-fhir/client-py 

go to the R4 branch
    https://github.com/smart-on-fhir/client-py/tree/feature/r4

download the whole thing (clone the repository locally... possibly using just zip and extract)

run the "setup"
   > python setup.ph install

# Test application
## AuditWrite.py
* create a Patient
* create an Observation
* Read the Observation
* Update the Observation
* Read the Observation
* Delete the Observation
* Pause to allow audits to be created lazy
* Read all auditEvent for 

# Results
## Grahame's server 
works now
Initially auditEvent did not have .entity with Patient identified. This inspired GF#23835
https://chat.fhir.org/#narrow/stream/179247-Security-and.20Privacy
## Pyro server 
works now
Initially the AuditEvent were not valid with problems with the .text div
## Fire.ly Vonk server 
does NOT auto create audit logs
## HAPI server
does not auto create audit logs
https://chat.fhir.org/#narrow/stream/179167-hapi/topic/automatic.20Audit.20logs
