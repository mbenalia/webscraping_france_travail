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