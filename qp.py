import requests

SONARQUBE_URL = "http://your-sonarqube-url"
BEARER_TOKEN = "your-bearer-token"
HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}"}

# Configuration
PROFILE1_KEY = "your-first-profile-key"
PROFILE2_KEY = "your-second-profile-key"
NEW_PROFILE_KEY = "your-new-profile-key"

def get_profile_rules(profile_key):
    """Get all activated rules from a profile with parameters"""
    rules = []
    page = 1
    while True:
        params = {
            "activation": "true",
            "qprofile": profile_key,
            "ps": 500,
            "p": page
        }
        response = requests.get(f"{SONARQUBE_URL}/api/rules/search", 
                              params=params, 
                              headers=HEADERS)
        data = response.json()
        
        for rule in data['rules']:
            rules.append({
                "key": rule['key'],
                "severity": rule['severity'],
                "params": rule.get('params', [])
            })
            
        if page * data['ps'] >= data['total']:
            break
        page += 1
    return rules

def activate_rule(profile_key, rule):
    """Activate a rule in target profile"""
    params = {
        "key": profile_key,
        "rule": rule['key'],
        "severity": rule['severity'],
        "reset": "false"
    }
    
    # Add parameters if they exist
    for param in rule['params']:
        params[f"params_{param['key']}"] = param['value']
    
    requests.post(f"{SONARQUBE_URL}/api/qualityprofiles/activate_rule",
                params=params,
                headers=HEADERS)

# Get rules from both profiles
profile1_rules = get_profile_rules(PROFILE1_KEY)
profile2_rules = get_profile_rules(PROFILE2_KEY)

# Activate all rules from first profile
for rule in profile1_rules:
    activate_rule(NEW_PROFILE_KEY, rule)

# Activate rules from second profile (overwrite if duplicates)
for rule in profile2_rules:
    activate_rule(NEW_PROFILE_KEY, rule)

print(f"Combined profile {NEW_PROFILE_KEY} created with " 
      f"{len(profile1_rules)+len(profile2_rules)} total rules")