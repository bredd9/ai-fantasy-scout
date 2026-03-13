import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

jucatori = []

print("=== PASUL 1: Extragerea listei Top 500 jucători ===")
# Acum trecem prin paginile 1-20 (25 jucători x 20 pagini = 500)
for page in range(1, 21):
    print(f"-> Scanăm pagina {page} din 20...")
    url_lista = f"https://www.transfermarkt.com/spieler-statistik/wertvollstespieler/marktwertetop?page={page}"
    
    try:
        response = requests.get(url_lista, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        randuri = soup.find_all('tr', class_=['odd', 'even'])
        
        for rand in randuri:
            try:
                hauptlinks = rand.find_all('td', class_='hauptlink')
                nume_tag = hauptlinks[0].find('a')
                nume = nume_tag.text.strip()
                link = "https://www.transfermarkt.com" + nume_tag['href']
                valoare = hauptlinks[-1].text.strip()
                
                inline_table = rand.find('table', class_='inline-table')
                pozitie = inline_table.find_all('tr')[1].text.strip() if inline_table else "Unknown"
                
                zentriert_tds = rand.find_all('td', class_='zentriert')
                varsta = zentriert_tds[1].text.strip() if len(zentriert_tds) > 1 else "0"
                
                club_tag = rand.find('a', href=lambda href: href and '/verein/' in href, title=True)
                club = club_tag['title'] if club_tag else "Unknown"
                
                jucatori.append({
                    'Nume': nume,
                    'Varsta': varsta,
                    'Pozitie': pozitie,
                    'Club': club,
                    'Valoare_Piata': valoare,
                    'Link_Profil': link
                })
            except Exception as e:
                continue
    except Exception as e:
        print(f"Eroare pe pagina {page}")
        
    time.sleep(1)

print(f"\nAm extras {len(jucatori)} jucători de bază. Trecem la pasul 2.")
print("ATENȚIE: Extragerea statisticilor va dura aproximativ 15-20 de minute!")

for i, jucator in enumerate(jucatori):
    print(f"[{i+1}/{len(jucatori)}] Analizăm: {jucator['Nume']}...")
    link_stats = jucator['Link_Profil'].replace('/profil/', '/leistungsdaten/')
    
    try:
        res = requests.get(link_stats, headers=headers)
        soup = BeautifulSoup(res.content, 'html.parser')
        
        tfoot = soup.find('tfoot')
        m, g, a = "0", "0", "0"
        
        if tfoot:
            celule_total = tfoot.find_all('td')
            m = celule_total[2].text.strip() if len(celule_total) > 2 else "0"
            g = celule_total[3].text.strip() if len(celule_total) > 3 else "0"
            a = celule_total[4].text.strip() if len(celule_total) > 4 else "0"
            
        jucator['Meciuri'] = m
        jucator['Goluri'] = g
        jucator['Pase_Gol'] = a
        
    except Exception as e:
        jucator['Meciuri'], jucator['Goluri'], jucator['Pase_Gol'] = "0", "0", "0"
        
    time.sleep(2)

df = pd.DataFrame(jucatori)
df.to_csv('top_500_jucatori.csv', index=False)
print("\nGATA! Baza ta de date completă a fost salvată în 'top_500_jucatori.csv'")