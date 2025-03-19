import requests
import pandas as pd
import os
import json
import time
from datetime import datetime, timedelta

# Définition des dates
start_date = datetime(2020, 1, 22)
end_date = datetime(2023, 3, 9)

# URL de l'API
url = "https://covid-api.com/api/reports"

# Création des dossiers pour stocker les fichiers
os.makedirs("json_data", exist_ok=True)
os.makedirs("csv_data", exist_ok=True)

# Liste pour stocker toutes les données
data_list = []

current_date = start_date

# On télécharge les données seulement 3 jours par mois
while current_date <= end_date:
    if current_date.day in [1, 10, 20]:  # Télécharger seulement le 1er, 10 et 20 de chaque mois
        date_str = current_date.strftime("%Y-%m-%d")
        response = requests.get(url, params={"date": date_str})

        if response.status_code == 200:
            try:
                data = response.json()
                
                if isinstance(data, dict) and "data" in data:
                    reports = data["data"]

                    # Sauvegarde en JSON
                    json_file = f"json_data/covid_{date_str}.json"
                    with open(json_file, "w", encoding="utf-8") as f:
                        json.dump(reports, f, ensure_ascii=False, indent=4)
                    print(f"✅ JSON sauvegardé : {json_file}")

                    if reports:
                        # Transformation en DataFrame bien structuré
                        df = pd.json_normalize(reports)

                        # Sélection et renommage des colonnes pour plus de clarté
                        df = df[[
                            'date', 'confirmed', 'deaths', 'recovered', 
                            'confirmed_diff', 'deaths_diff', 'recovered_diff',
                            'last_update', 'active', 'active_diff', 'fatality_rate',
                            'region.iso', 'region.name', 'region.province', 'region.lat', 'region.long'
                        ]]

                        df.rename(columns={
                            'region.iso': 'iso',
                            'region.name': 'country',
                            'region.province': 'province',
                            'region.lat': 'latitude',
                            'region.long': 'longitude'
                        }, inplace=True)

                        # Sauvegarde en CSV
                        csv_file = f"csv_data/covid_{date_str}.csv"
                        df.to_csv(csv_file, index=False)
                        print(f"✅ CSV sauvegardé : {csv_file}")

                        data_list.append(df)
            except json.JSONDecodeError:
                print(f"Erreur de décodage JSON pour {date_str}")
        else:
            print(f"❌ Erreur API pour {date_str}: {response.status_code}")

        # Pause pour éviter d'être bloqué par l'API
        time.sleep(1)

    current_date += timedelta(days=1)

# Enregistrement d'un fichier CSV global bien structuré
if data_list:
    df_all = pd.concat(data_list, ignore_index=True)
    df_all.to_csv("covid_data_global.csv", index=False)
    print("✅ Fichier global CSV sauvegardé : covid_data_global.csv")
