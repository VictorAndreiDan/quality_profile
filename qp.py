import requests
import json

SONARQUBE_URL = "http://your-sonarqube-url"
BEARER_TOKEN = "your-bearer-token"
HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}"}

# Configuration - Get these from SonarQube UI or API response
PROFILE1_KEY = "AXClVdvHplZJkqX4abcd"  # Replace with actual profile key
PROFILE2_KEY = "AXClVdvHplZJkqX4efgh"  # Replace with actual profile key
NEW_PROFILE_KEY = "AXClVdvHplZJkqX4ijkl"  # Replace with actual profile key

def get_profile_rules(profile_key):
    """Get all activated rules from a profile with parameters"""
    rules = []
    page = 1
    try:
        while True:
            params = {
                "activation": "true",
                "qprofile": profile_key,
                "ps": 500,
                "p": page
            }
            response = requests.get(
                f"{SONARQUBE_URL}/api/rules/search",
                params=params,
                headers=HEADERS
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                print(f"⚠️ Invalid JSON response for profile {profile_key}")
                print(f"Response content: {response.text}")
                return []
            
            # Debug: Save raw API response
            with open(f"debug_{profile_key}_page_{page}.json", "w") as f:
                json.dump(data, f, indent=2)
                
            if 'rules' not in data:
                print(f"⚠️ Unexpected response format for profile {profile_key}")
                print(f"Response keys: {list(data.keys())}")
                return []
                
            for rule in data['rules']:
                rules.append({
                    "key": rule['key'],
                    "severity": rule['severity'],
                    "params": rule.get('params', [])
                })
                
            if page * data['ps'] >= data.get('total', 0):
                break
            page += 1
            
    except requests.exceptions.RequestException as e:
        print(f"🚨 API request failed for profile {profile_key}: {str(e)}")
        return []
        
    return rules

def activate_rule(profile_key, rule):
    """Activate a rule in target profile"""
    try:
        params = {
            "key": profile_key,
            "rule": rule['key'],
            "severity": rule['severity'],
            "reset": "false"
        }
        
        for param in rule['params']:
            params[f"params_{param['key']}"] = param['value']
            
        response = requests.post(
            f"{SONARQUBE_URL}/api/qualityprofiles/activate_rule",
            params=params,
            headers=HEADERS
        )
        response.raise_for_status()
        
    except requests.exceptions.RequestException as e:
        print(f"🚨 Failed to activate rule {rule['key']}: {str(e)}")

# Get rules from both profiles
print("🔄 Fetching rules for first profile...")
profile1_rules = get_profile_rules(PROFILE1_KEY)
print(f"📚 Found {len(profile1_rules)} rules in first profile")

print("🔄 Fetching rules for second profile...")
profile2_rules = get_profile_rules(PROFILE2_KEY)
print(f"📚 Found {len(profile2_rules)} rules in second profile")

# Activate rules
print("⚡ Activating rules in new profile...")
for rule in profile1_rules + profile2_rules:
    activate_rule(NEW_PROFILE_KEY, rule)

print("✅ Profile combination complete! Verify in SonarQube UI")