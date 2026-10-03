"""Structural appliance checks. No signatures, admission, or hardware closure."""
from datetime import datetime

def check(record):
    r = record
    errors = []
    kind = r['contract']
    if 'issued_at' in r:
        start = datetime.fromisoformat(r['issued_at'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(r['expires_at'].replace('Z', '+00:00'))
        maximum = {'ApplianceQualificationGrant': 86400, 'ApplianceUpdateOffer': 86400, 'ApplianceUpdateLease': 300,
                   'ProductionCredentialChallenge': 120}[kind]
        if not 0 < (end-start).total_seconds() <= maximum:
            errors.append('APPLIANCE-TIME: invalid bounded interval')
    if kind == 'ApplianceRelease':
        if r['state_format'] not in r['readable_state_formats']:
            errors.append('APPLIANCE-STATE: own state format is not readable')
        if [i['slot'] for i in r['images']] != ['A', 'B']:
            errors.append('APPLIANCE-SLOTS: require ordered distinct A/B variants')
        for image in r['images']:
            if [a['role'] for a in image['artifacts']] != ['boot', 'root', 'hash', 'metadata']:
                errors.append('APPLIANCE-RANGES: require four ordered complete ranges')
    if kind in ('ApplianceQualificationGrant', 'ApplianceUpdateOffer', 'ApplianceUpdateReceipt'):
        if r['current_release'] == r['target_release']:
            errors.append('APPLIANCE-RELEASE: target must change release')
    if kind == 'ApplianceUpdateOffer':
        if (r['scope'] == 'qualification') != ('qualification_grant' in r):
            errors.append('APPLIANCE-SCOPE: qualification requires its grant; production excludes it')
    if kind == 'ProductionCredentialChallenge':
        if (r['purpose'] != 'enroll') != ('predecessor_certificate_digest' in r):
            errors.append('APPLIANCE-CREDENTIAL: predecessor required except for enrollment')
    if kind == 'ApplianceUpdateReceipt':
        outcomes = {'writing': 'reconciliation', 'staged': 'pending',
                    'trial_arming': 'reconciliation', 'trial': 'pending',
                    'committing': 'reconciliation', 'committed': 'pending',
                    'confirmed': 'confirmed', 'fallback': 'fallback',
                    'fallback_pending': 'pending', 'reconciliation': 'reconciliation'}
        if outcomes[r['phase']] != r['outcome']:
            errors.append('APPLIANCE-RECEIPT: phase and outcome differ')
        if r['readback'] and [a['role'] for a in r['readback']] != ['boot','root','hash','metadata']:
            errors.append('APPLIANCE-RECEIPT: incomplete ordered ranges')
        if r['outcome'] == 'confirmed' and (not r.get('boot_id') or not r['readback']):
            errors.append('APPLIANCE-RECEIPT: confirmed requires boot and readback')
    return errors
