import re
import time
import random
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import sqlite3


def build_url(limite_basse, limite_haute,recherche='data',partenaires="true",):

    base_url = "https://candidat.francetravail.fr/offres/recherche"
    params = {
      "motsCles": recherche,
      "offresPartenaires": partenaires,
      "range": f"{limite_basse}-{limite_haute}",
      "rayon": 10,
      "tri": 0
    }
    url = base_url + "?" + "&".join(f"{key}={value}" for key, value in params.items())
    return url

def get_nombre_offres():
    #fonction à faire évoluer en prenant en compte l'url variable
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    url='https://candidat.francetravail.fr/offres/recherche?motsCles=data&offresPartenaires=true&rayon=10&tri=0'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        h1_element = soup.find('h1', class_='title')
        h1_text = h1_element.get_text()
        nombre_offres = re.search(r'\d+', h1_text).group()
        return int(nombre_offres)
    else:
        print("Erreur lors de la récupération de la page : HTTP", response.status_code)
        return None
def extract_job_information(job_section):

    title = job_section.find('span', class_='media-heading-title').get_text(strip=True)
    subtext = job_section.find_next_sibling('p', class_='subtext')
    company = subtext.get_text(strip=True) if subtext else 'Information non disponible'
    location = subtext.find('span').get_text(strip=True) if subtext and subtext.find('span') else 'Lieu non disponible'
    description = job_section.find_next_sibling('p', class_='description').get_text(strip=True)
    contract = job_section.find_next_sibling('p', class_='contrat').get_text(strip=True)
    date_posted = job_section.find_next_sibling('p', class_='date').get_text(strip=True)
    return {
          'poste': title,
          'entreprise': company,
          'lieu': location,
          'description': description,
          'contrat': contract,
          'date_publication': date_posted
      }

def get_offres(limite_basse, limite_haute, job_list):
    url = build_url(limite_basse, limite_haute)
    headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    html_content = fetch_job_offers(url, headers)
    if html_content:
        job_data = parse_job_details(html_content)
        job_list.extend(job_data)
    return job_list# Use extend to add elements to an existing list    return job_list

def fetch_job_offers(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error fetching job offers: HTTP {response.status_code}")
        return None

def parse_job_details(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    job_sections = soup.find_all('h2', class_='t4 media-heading')
    job_data = []
    for job_section in job_sections:
        job_details = extract_job_information(job_section)
        if job_details:
            job_data.append(job_details)
    return job_data

def scrap_FT():
    job_list=[]
    nb_max=get_nombre_offres()
    nb_max=41
    for i in range(0,nb_max,20):
        delai_attente = random.randint(1, 5)
        #time.sleep(delai_attente)
        get_offres(i, min(i+20, nb_max), job_list)

    if nb_max % 20 != 0:
        get_offres(nb_max-nb_max%20,nb_max,job_list)

    return pd.DataFrame(job_list)

def nettoyer_entreprise(df):
    # Utilise une expression régulière pour supprimer les caractères précédents et le tiret avant le nombre
    clean_df = df.str.split('\n').str[0]
    return clean_df

def nettoyer_contrat(df):
    # Divise la colonne "Entreprise" en fonction du caractère "\n" et ne conserve que la première partie
    clean_df = df.str.replace('\n','')
    return clean_df

def convert_to_date(duree):
    if "aujourd'hui" in duree:
        return datetime.now().strftime("%Y-%m-%d")
    elif "hier" in duree:
        return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    elif "il y a plus de" in duree:
        return (datetime.now() - timedelta(days=31)).strftime("%Y-%m-%d")
    elif "il y a" in duree:
        days_ago = int(duree.split()[4])
        return (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

def nettoyage_total(df):
    df['entreprise'] = nettoyer_entreprise(df['entreprise'])
    df['contrat'] = nettoyer_contrat(df['contrat'])
    df["date_publication"] = df["date_publication"].apply(convert_to_date)
    return df
