import requests
import json
from datetime import datetime
import os
import time
import logging
import pandas as pd
from concurrent.futures import ThreadPoolExecutor


languageapi = "en"

# Configurer le logger avec un format personnalisé
logging.basicConfig(
    level=logging.INFO,  # Niveau de log (DEBUG, INFO, WARNING, etc.)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Format du message
    datefmt='%Y-%m-%d %H:%M:%S'  # Format de la date et de l'heure
)

def extract_ids(data_list):
    """
    Extrait tous les IDs d'une liste de dictionnaires.

    :param data_list: Liste de dictionnaires contenant un champ 'id'
    :return: Liste des IDs
    """
    ids = [item['id'] for item in data_list if 'id' in item]
    return ids

def fetch_data(item):
    """
    Fonction pour faire la requête GET pour un item et renvoyer les données reçues.
    """
    if 'url' in item:
        payload = {}
        headers = {}
        try:
            response = requests.get(item['url'], headers=headers, data=payload)
            if response.status_code == 200:
                return json.loads(response.content.decode('utf-8'))
            else:
                logging.error(f"Erreur lors de la requête pour {item['id']} : {item['name']}: {response.status_code}")
                return []
        except Exception as e:
            logging.error(f"Erreur pour {item['id']} : {item['name']} : {e}")
            return []
    return []

def add_full_data_tread(data_list, max_workers=500):
    """
    Ajoute une clé 'url' à chaque élément du dictionnaire dans la liste, et récupère des données via des requêtes GET en parallèle.

    :param data_list: Liste de dictionnaires contenant un champ 'id'
    :param max_workers: Nombre maximum de threads pour les requêtes parallèles
    :return: Liste mise à jour avec les résultats ajoutés
    """
    # Utilisation de ThreadPoolExecutor pour envoyer les requêtes en parallèle
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fetch_data, item) for item in data_list]
        
        # Attendre les résultats et ajouter les sous-éléments récupérés à la liste de données
        counter = 0
        for future in futures:
            subitems = future.result()
            
            if isinstance(subitems, dict):
               data_list.append(subitems)
               counter = counter +1  
            else:
                
                data_list.extend(subitems)
        logging.info(f" single item counter = {counter}")

    return data_list


def add_url_to_items(data_list):
    """
    Ajoute une clé 'url' à chaque élément du dictionnaire dans la liste.
    La valeur de 'url' est construite à partir de l'ID de l'élément.

    :param data_list: Liste de dictionnaires contenant un champ 'id'
    :return: Liste mise à jour avec la clé 'url' ajoutée
    """
    base_url = "https://api.arsha.io/v2/eu/item?id="
    
    for item in data_list:
        if 'id' in item:
            #print(item)
            item['url'] = base_url + str(item['id'])
            item['url'] = item['url'] + "&lang="+ languageapi      
    
    return data_list

def remove_items_with_mainCategory(data_list):
    """
    Supprime tous les éléments qui contiennent la clé 'mainCategory' dans une liste de dictionnaires.

    :param data_list: Liste de dictionnaires
    :return: Liste filtrée sans les éléments contenant 'mainCategory'
    """
    return [item for item in data_list if 'mainCategory' not in item]

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

url = "https://api.arsha.io/v2/eu/market" #Convenience method for getting all items currently available on the market
payload={}
headers = {}


response = requests.request("GET", url, headers=headers, data=payload)


dico = json.loads(response.content.decode('utf-8'))

if False:
  nom_a_chercher = "Deboreka"
  filtereddico = rechercher_par_nom(dico, nom_a_chercher)

  nom_a_chercher = "Blackstar"
  filtereddico = filtereddico + rechercher_par_nom(dico, nom_a_chercher)

  nom_a_chercher = "Godr-Ayed"
  filtereddico = filtereddico + rechercher_par_nom(dico, nom_a_chercher)
  
  nom_a_chercher = "Caphras"
  filtereddico = filtereddico + rechercher_par_nom(dico, nom_a_chercher)
  
  dico = filtereddico 
  
#print(dico)
ids = extract_ids(dico)


#print(ids)
count = len(ids)
logging.info(f"nb item found: [{count}]")
add_url_to_items(dico)

with open('input_with_url.json', 'w') as json_file:
        json.dump(dico, json_file, indent=4)
        
logging.info("url added")
add_full_data_tread(dico)

dico = remove_items_with_mainCategory(dico)

#print(dico)


count = len(dico)
logging.info(f" nb item found: [{count}]")

current_time = datetime.now().strftime('%Y_%m_%d_%H_%M_')

with open(current_time+'fulldata.json', 'w') as json_file:
        json.dump(dico, json_file, indent=4)    

df = pd.DataFrame(dico)
# Sauvegarder dans un fichier Excel
df.to_excel(current_time + "fulldata.xlsx", index=False)



