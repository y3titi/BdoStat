import requests
import json
from datetime import datetime
import os
import time
import keyboard

import pandas as pd
import matplotlib.pyplot as plt

# Durée totale d'attente en secondes (1800 secondes = 30 minutes)
wait_time = 1800
# Intervalle pour vérifier si 'q' est pressé (en secondes)
check_interval = 1


def plot_total_trades(json_file):
    """
    Trace un graphique de l'évolution des totalTradesSum dans le temps à partir d'un fichier JSON.

    :param json_file: Chemin du fichier JSON contenant les données.
    """
    # Charger le fichier JSON
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Convertir les données en DataFrame
    df = pd.DataFrame(data)

    # Convertir la colonne 'date' en0 format datetime
    df['date'] = pd.to_datetime(df['date'])
    # Extraire uniquement l'heure
    #df['heure'] = df['date'].dt.strftime('%H:%M:%S')

    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    # Tracer le graphique
    axes[0].plot(df['date'], df['totalTradesSum'], marker='o')
    axes[0].set_title('Évolution des totalTradesSum (Proportionnel) - ' + json_file)
    axes[0].set_xlabel('Date')
    axes[0].set_ylabel('Total Trades Sum')
    axes[0].xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M:%S'))
    axes[0].grid(True)
    

    df['jour'] = df['date'].dt.date
    
    daily_variation = df.groupby('jour').apply(lambda x: x['totalTradesSum'].iloc[-1] - x['totalTradesSum'].iloc[0])

    ventes_par_jour = df.groupby('jour').size()

    # Deuxième graphique : nombre de ventes par jour
    axes[1].bar(daily_variation.index, daily_variation.values, color='blue')
    axes[1].set_title('Variation quotidienne des totalTradesSum (Dernière - Première)')
    axes[1].set_xlabel('Date')
    axes[1].set_ylabel('Variation des totalTradesSum')
    axes[1].grid(True)

    # Rotation des labels pour une meilleure lisibilité
    axes[1].tick_params(axis='x', rotation=45)

    # Afficher le graphique
    plt.tight_layout()
    plt.show()


def extract_name_and_stock(data):
    return [(item['name'], item['currentStock']) for item in data]

def rechercher_par_nom(liste_elements, nom_a_chercher):
  """
  Recherche tous les éléments d'une liste dont le champ "name" correspond au nom recherché.

  Args:
    liste_elements: La liste d'éléments à parcourir.
    nom_a_chercher: Le nom à rechercher dans le champ "name" des éléments.

  Returns:
    Une nouvelle liste contenant tous les éléments correspondants.
  """

  resultats = []
  for element in liste_elements:
    test = element["name"]
    if nom_a_chercher in test:
      resultats.append(element)
  return resultats

def count_elements(data):
    return len(data)

def sum_total_trades_and_save(searchname):
    
    url = "https://api.arsha.io/v2/eu/market" #Convenience method for getting all items currently available on the market
    payload={}
    headers = {}


    response = requests.request("GET", url, headers=headers, data=payload)

    #print(response.text)

    nom_a_chercher = searchname

    dico = json.loads(response.content.decode('utf-8'))
    
    if nom_a_chercher == "":
        resultats = dico
    else:
        resultats = rechercher_par_nom(dico, nom_a_chercher)
        
    # Calculer la somme des "totalTrades"
    total_trades_sum = sum(item['totalTrades'] for item in resultats)
    
    # Obtenir la date et l'heure actuelles
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
        # Créer une nouvelle entrée
    new_entry = {
        'totalTradesSum': total_trades_sum,
        'date': current_time
    }
    
    nomfichier = searchname + "_total_trades.json"
    
    # Lire les données existantes si le fichier existe
    if os.path.exists(nomfichier):
        with open(nomfichier, 'r') as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = []
    
    # Ajouter la nouvelle entrée aux données existantes
    existing_data.append(new_entry)
    # Écrire les données mises à jour dans le fichier JSON
    with open(nomfichier, 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)
    
    print(f"[{current_time}] Les données ont été mises à jour et enregistrées dans {nomfichier}")
    
    
    
def sum_total_trades_all_and_save(filename="total_trades_ALL.json"):
    
    url = "https://api.arsha.io/v2/eu/market" #Convenience method for getting all items currently available on the market
    payload={}
    headers = {}


    response = requests.request("GET", url, headers=headers, data=payload)
   

    dico = json.loads(response.content.decode('utf-8'))

    #print(dico)
    # Calculer la somme des "totalTrades"
    total_trades_sum = sum(item['totalTrades'] for item in dico)
    
    # Obtenir la date et l'heure actuelles
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
        # Créer une nouvelle entrée
    new_entry = {
        'totalTradesSum': total_trades_sum,
        'date': current_time
    }
    
    # Lire les données existantes si le fichier existe
    if os.path.exists(filename):
        with open(filename, 'r') as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = []
    
    # Ajouter la nouvelle entrée aux données existantes
    existing_data.append(new_entry)
    # Écrire les données mises à jour dans le fichier JSON
    with open(filename, 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)
    
    print(f"[{current_time}] Les données ont été mises à jour et enregistrées dans {filename}")

print("******************************************")


url = "https://api.arsha.io/v2/eu/market" #Convenience method for getting all items currently available on the market
payload={}
headers = {}


#response = requests.request("GET", url, headers=headers, data=payload)

#print(response.text)

#nom_a_chercher = "Ring"
#nom_a_chercher = "Blackstar"
#nom_a_chercher = "Godr-Ayed"
#nom_a_chercher = "Deboreka"

#dico = json.loads(response.content.decode('utf-8'))
#resultats = rechercher_par_nom(dico, nom_a_chercher)
#print(resultats)

#print(count_elements(resultats))

#result = extract_name_and_stock(resultats)
#print(result)

#plot_total_trades('Deboreka_total_trades.json')



while True:
  sum_total_trades_all_and_save()
  sum_total_trades_and_save("Deboreka")
  sum_total_trades_and_save("Blackstar")
  sum_total_trades_and_save("Godr-Ayed")
  sum_total_trades_and_save("Caphras")
  sum_total_trades_and_save("Memory Fragment")
  sum_total_trades_and_save("Krogdalo")
  sum_total_trades_and_save("Manos")
  waited = 0
  while waited < wait_time:
        if keyboard.is_pressed('q'):
            print("La boucle a été interrompue pendant l'attente.")
            break
        time.sleep(check_interval)  # Attendre par petits intervalles
        waited += check_interval

  if keyboard.is_pressed('q'):
        break
plot_total_trades('total_trades_ALL.json')
plot_total_trades('Deboreka_total_trades.json')
plot_total_trades('Blackstar_total_trades.json')
plot_total_trades('Godr-Ayed_total_trades.json')
plot_total_trades('Caphras_total_trades.json')
plot_total_trades('Memory Fragment_total_trades.json')
plot_total_trades('Manos_total_trades.json')
plot_total_trades("Krogdalo_total_trades.json")

  
  