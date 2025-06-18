# dms_project/context_processors.py

def clinic_details(request):
    """
    Adds clinic contact information to the context of all templates.
    """
    return {
        'CLINIC_NAME': 'Babu Dental Clinic',
        'CLINIC_ADDRESS': 'Beach Road, Kadapakkam, Cheyyur Taluk, Chengalpattu District, Tamilnadu - 603304',
        'CLINIC_PHONE': '04427526041',
        'CLINIC_EMAIL': 'drbdcdental@gmail.com'
    }