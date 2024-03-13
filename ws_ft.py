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
