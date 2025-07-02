from State import State
import requests
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import urllib3
import pandas as pd

from langchain_core.messages.ai import AIMessage

class InteractionBdd:

    def __init__(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        load_dotenv()
        self.BASE_URL = os.getenv("SIGSCAN_URL")
        self.USERNAME = os.getenv("SIGSCAN_USER")
        self.PASSWORD = os.getenv("SIGSCAN_PASS")

        

    def authenticate(self):
        url = f"{self.BASE_URL}/api/login"
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json={"username": self.USERNAME, "password": self.PASSWORD}, headers=headers, verify=False)
        response.raise_for_status()
        return response.text.strip().replace('"', '')
    
    def temps_to_datetime(self, temps_obj):
        return datetime(temps_obj.annee, temps_obj.mois, temps_obj.jour)

    def parse_date(self, date_input):
        if isinstance(date_input, str):
            return datetime.fromisoformat(date_input.replace("Z", "+00:00"))
        return self.temps_to_datetime(date_input)

    def to_unix_millis(self, dt_obj):
        return int(dt_obj.timestamp() * 1000)
    
    def get_positions_history(self, token, org_id, object_id, start_date, end_date):
        url = f"{self.BASE_URL}/api/positions/history"
        headers = {"Authorization": f"Bearer {token}"}
        dt_start = self.parse_date(start_date)
        dt_end =  self.parse_date(end_date)
        params = {
            "organizationId": org_id,
            "sigscanObjectId": object_id,
            "startDate": self.to_unix_millis(dt_start),
            "endDate": self.to_unix_millis(dt_end),
            "page": 0,
            "size": 1000
        }
        response = requests.get(url, headers=headers, params=params, verify=False)
        response.raise_for_status()
        return response.json()
    
    def get_objects(self, token, org_id):
        url = f"{self.BASE_URL}/api/objects"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"organizationId": org_id, "size": 1000}
        response = requests.get(url, headers=headers, params=params, verify=False)
        response.raise_for_status()
        return response.json()["content"]

    def get_organization_id(self, token):
        url = f"{self.BASE_URL}/api/organizations"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        orgs = response.json()["content"]
        return orgs[0]["id"] if orgs else None
    
    def interactionBdd(self, state : State) -> State:
        """ Fonction permettant l'interaction avec la base de données."""
        # Identifier la plage temporelle (start_date, end_date)
        # Vérification si start_date ou end_date vaut None:
        #print(state)
        req = state.get('call_request')
        print(req)
        # Plage temporelle
        today = datetime.utcnow()
        if req.startDate and req.endDate:
            start_date = req.startDate
            end_date = req.endDate

            # Si une date est future, on reset
            if self.parse_date(start_date) > today or self.parse_date(end_date) > today:
                start_date = (today - timedelta(days=90)).isoformat() + "Z"
                end_date = today.isoformat() + "Z"
        else:
            start_date = (today - timedelta(days=90)).isoformat() + "Z"
            end_date = today.isoformat() + "Z"


        # Authentification de l'utilisateur
        token = self.authenticate()

        # Identification de l'ID de l'organisation
        org_id = self.get_organization_id(token)
        # Obtenir tous les objets de l’organisation
        objects = self.get_objects(token, org_id)
        
        object_label = getattr(req, 'object', None)
        zone_label = getattr(req, 'area', None)

        object_filter = str(object_label.value) if hasattr(object_label, 'value') else str(object_label) if object_label else None
        zone_filter = str(zone_label.value) if hasattr(zone_label, 'value') else str(zone_label) if zone_label else None
        all_positions = []
        for obj in objects:
            pos_data = self.get_positions_history(token, org_id, obj["id"], start_date, end_date)
            if pos_data:
                for pos in pos_data:
                    #print(pos_data)
                    pos["sigscan_object_name"] = obj["name"]
                    pos["sigscan_object_id"] = obj["id"]
                all_positions.extend(pos_data)

        df_positions = pd.DataFrame(all_positions)

        # Nettoyage rapide
        if not df_positions.empty:
            df_positions["last_update_date"] = pd.to_datetime(df_positions["last_update_date"], unit='ms')
        #print("🧾 Colonnes disponibles dans df_positions :", df_positions.columns.tolist())

        # Filtrage zone
        if zone_filter:
            if "area_name" in df_positions.columns or "area" in df_positions.columns:
                df_positions = df_positions[
                    ((df_positions["area_name"] == zone_filter) if "area_name" in df_positions.columns else False) |
                    (df_positions["area"].apply(lambda a: isinstance(a, dict) and a.get("name") == zone_filter)
                    if "area" in df_positions.columns else False)
                ]

        #filtrage objet
        if object_filter and "sigscan_object_name" in df_positions.columns:
            df_positions = df_positions[
                df_positions["sigscan_object_name"].str.contains(object_filter, case=False, na=False)
            ]


        # Stockage dans le state
        state["dataFrames"] = [
            {"role": "Positions objets", "dataFrame": df_positions},
        ]
        def pretty_dataframe_summary(df, zone=None):
            if df.empty:
                return "📭 Aucune donnée trouvée."

            df = df[["sigscan_object_id", "sigscan_object_name", "area_name", "last_update_date","positionx","positiony"]].copy()
            df.columns = ["Objet ID", "Nom objet", "Zone", "Date de passage","Position_X","Position_Y"]
            df.drop_duplicates(inplace=True)
            return "📋 Résultat :\n" + df.to_string(index=False)

        df_summary = pretty_dataframe_summary(df_positions)
        return state | {"messages": AIMessage(content=df_summary)}
