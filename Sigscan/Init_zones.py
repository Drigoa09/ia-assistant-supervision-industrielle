import requests

import os
from dotenv import load_dotenv

#Chargement des variables d'environnement
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
USERNAME = os.getenv("USERNAME_SIGSCAN")
PASSWORD = os.getenv("PASSWORD")

def authenticate():
    url = f"{BASE_URL}/api/login"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json={"username": USERNAME, "password": PASSWORD}, headers=headers, verify=False)
    response.raise_for_status()
    return response.text.strip().replace('"', '')


def get_organization_id(token):
    url = f"{BASE_URL}/api/organizations"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    orgs = response.json()["content"]
    return orgs[0]["id"] if orgs else None


def get_all_beacons(token, organization_id):
    url = f"{BASE_URL}/api/beacons"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"organizationId": organization_id, "size": 1000}
    response = requests.get(url, headers=headers, params=params, verify=False)
    response.raise_for_status()
    return response.json()["content"]

def get_positions(token, organization_id):
    url = f"{BASE_URL}/api/positions/history"
    headers = {"Authorization": f"Bearer {token}"}

    params = {"organizationId": organization_id, "sigscanObjectId" : 27986, "page": 0, "size": 50000, "startDate" : 1742993817000, "endDate" : 1750942617000}
    response = requests.get(url, headers=headers, params=params, verify=False)

    return response.json()

def get_all_objects(token, organization_id):
    url = f"{BASE_URL}/api/objects"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"organizationId": organization_id, "size": 1000}
    response = requests.get(url, headers=headers, params=params, verify=False)
    response.raise_for_status()
    return response.json()['content']

def get_areas(token, organization_id):
    url = f"{BASE_URL}/api/gateways"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"organizationId": organization_id, "size": 1000}
    response = requests.get(url, headers=headers, params=params, verify=False)
    response.raise_for_status()
    return response.json()['content']

def get_areas_sigscan():
    token = authenticate()
    print("✅ Auth OK")

    org_id = get_organization_id(token)
    if not org_id:
        print("❌ Organisation introuvable.")
        return

    print(f"🏢 Organisation ID : {org_id}")
    beacons = get_all_beacons(token, org_id)
    print(f"📡 Beacons récupérés : {len(beacons)}")

    print("Areas : ")
    return get_areas(token, org_id)