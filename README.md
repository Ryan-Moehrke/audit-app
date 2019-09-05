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
* AuditWrite.py
** create a Patient
** create an Observation
** Read the Observation
** Update the Observation
** Read the Observation
** Delete the Observation
** Pause to allow audits to be created lazy
** Read all auditEvent for 

# Results
1. Grahame's server works (Note needed to update his auditEvent to record .entity with Patient)
2. Pyro server works (Got them to fix their div on their auto created audit logs)
3. Fire.ly server does NOT auto create audit logs
