import requests

url = 'http://127.0.0.1:5000/predict'

# ---------------------------------------------------------
# TESTUL 1: Un Atacant Tânăr cu multe goluri
# ---------------------------------------------------------
jucator_atacant = {
    "varsta": 18,
    "meciuri": 35,
    "goluri": 22,
    "pase_gol": 8,
    "pozitie": "Right-Winger"
}

print("=== TEST 1: Atacant (Right-Winger) ===")
print(f"Trimitem datele: {jucator_atacant}")
response_atacant = requests.post(url, json=jucator_atacant)
print("RĂSPUNS AI:", response_atacant.json())
print("-" * 40)

# ---------------------------------------------------------
# TESTUL 2: Un Portar cu 0 goluri (cum e normal)
# ---------------------------------------------------------
jucator_portar = {
    "varsta": 27,
    "meciuri": 38,
    "goluri": 0,
    "pase_gol": 1,
    "pozitie": "Goalkeeper"
}

print("\n=== TEST 2: Portar (Goalkeeper) ===")
print(f"Trimitem datele: {jucator_portar}")
response_portar = requests.post(url, json=jucator_portar)
print("RĂSPUNS AI:", response_portar.json())