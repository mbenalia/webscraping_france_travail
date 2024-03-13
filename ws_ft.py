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
