import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup
import time
import urllib.parse

print("=== Începem Scraping-ul pentru TOP 500 (Anti-Bot + Auto-Fallback) ===")

# 1. CITIM FIȘIERUL MARE (Asigură-te că ai rulat primul scraper și ai acest fișier!)
df = pd.read_csv('date.csv') 

# Dicționar manual pentru jucătorii foarte faimoși cu nume atipice
nume_problematice = {
    "Vinicius Junior": "Vini Jr.",
    "Rodrygo": "Rodrygo Goes",
    "Raphinha": "Raphinha", # Uneori brazilienii au nevoie de atenție
}

overall_list = []
potential_list = []

# Spărgătorul Cloudflare
scraper = cloudscraper.create_scraper(browser={
    'browser': 'chrome',
    'platform': 'windows',
    'desktop': True
})

# Parcurgem TOȚI cei 500 de jucători
for index, row in df.iterrows():
    nume_jucator = row['Nume']
    print(f"\n[{index+1}/{len(df)}] Analizăm: {nume_jucator}...")
    
    # Pasul A: Verificăm dicționarul manual
    nume_corectat = nume_problematice.get(nume_jucator, nume_jucator)
    
    # Pasul B: Generăm variante de căutare pentru Fallback automat
    cuvinte = nume_corectat.split()
    variante_cautare = [nume_corectat] # Prima încercare: numele întreg
    
    if len(cuvinte) > 1:
        variante_cautare.append(cuvinte[-1]) # A doua încercare: doar numele de familie (ex: "Yamal")
        variante_cautare.append(cuvinte[0])  # A treia încercare: doar prenumele (ex: "Lamine")
        
    ovr = 80 # Valori de siguranță (dacă nu-l găsim deloc)
    pot = 85
    jucator_gasit = False
    
    # Încercăm variantele pe rând
    for varianta in variante_cautare:
        if jucator_gasit:
            break # L-am găsit deja, ne oprim din a încerca alte variante
            
        print(f"   -> Căutăm: '{varianta}'")
        nume_url = urllib.parse.quote_plus(varianta)
        url_search = f"https://sofifa.com/players?keyword={nume_url}"
        
        try:
            res = scraper.get(url_search)
            soup = BeautifulSoup(res.content, 'html.parser')
            
            titlu_pagina = soup.title.text if soup.title else ""
            if "Just a moment" in titlu_pagina or "Cloudflare" in titlu_pagina:
                print("   -> [!] BLOCAT DE CLOUDFLARE. Așteptăm 5 secunde...")
                time.sleep(5)
                continue
                
            td_ovr = soup.find('td', {'data-col': 'oa'})
            td_pot = soup.find('td', {'data-col': 'pt'})
            
            if td_ovr and td_pot:
                em_ovr = td_ovr.find('em')
                ovr = int(em_ovr.text.strip()) if em_ovr else int(td_ovr.text.strip())
                
                em_pot = td_pot.find('em')
                pot = int(em_pot.text.strip()) if em_pot else int(td_pot.text.strip())
                
                print(f"   ✅ Găsit! OVR: {ovr} | POT: {pot}")
                jucator_gasit = True
            else:
                pass # Nu am găsit tabelul, probabil a dat 0 results. Trecem la următoarea variantă.
                
        except Exception as e:
            print(f"   -> [Eroare]: {e}")
            
        # Pauză esențială de 3 secunde între căutări!
        time.sleep(3)
        
    if not jucator_gasit:
        print(f"   ❌ Nu a fost găsit pe SoFIFA. Rămâne OVR 80.")
        
    overall_list.append(ovr)
    potential_list.append(pot)

# Adăugăm noile coloane magice la baza de date
df['Overall'] = overall_list
df['Potential'] = potential_list

# Salvăm SUPER-FIȘIERUL final
nume_fisier_nou = 'top_500_FINAL_cu_fifa.csv'
df.to_csv(nume_fisier_nou, index=False)

print(f"\n🏆 MAGIA S-A TERMINAT! Baza ta de date completă este în '{nume_fisier_nou}'.")