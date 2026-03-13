from flask import Flask, request, jsonify
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import numpy as np

app = Flask(__name__)

print("=== 1. Antrenare Model ML (Inclusiv Poziția) ===")

# 1. Citim fișierul CEL NOU
df = pd.read_csv('date.csv') # Asigură-te că ăsta e numele corect

# 2. Funcție pentru a curăța valoarea financiară
def curata_valoare(val_str):
    if pd.isna(val_str) or val_str == "0": return 0
    val_str = str(val_str).replace('€', '')
    if 'm' in val_str:
        return float(val_str.replace('m', '')) * 1_000_000
    elif 'k' in val_str:
        return float(val_str.replace('k', '')) * 1_000
    return 0

df['Valoare_Numar'] = df['Valoare_Piata'].apply(curata_valoare)

# 3. CURĂȚAREA DATELOR PROBLEMATICE (-)
coloane_numerice = ['Varsta', 'Meciuri', 'Goluri', 'Pase_Gol']
for col in coloane_numerice:
    # Înlocuim liniuțele '-' cu '0'
    df[col] = df[col].astype(str).replace('-', '0')
    # Forțăm coloana să devină număr (dacă ceva e dubios, pune 0)
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# 4. Alegem datele brute, INCLUSIV Poziția
X_brut = df[['Varsta', 'Meciuri', 'Goluri', 'Pase_Gol', 'Pozitie']]
y = df['Valoare_Numar']

# 5. Transformăm textul (Poziția) în coloane matematice cu 0 și 1
X_procesat = pd.get_dummies(X_brut, columns=['Pozitie'])
COLOANE_MODEL = X_procesat.columns 

# 6. Creăm și antrenăm modelul
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_procesat, y)
print("Model antrenat cu succes! Modelul a înțeles diferența dintre atacanți și portari.")

print("=== 2. Pornire API ===")
@app.route('/predict', methods=['POST'])
def predict():
    try:
        date = request.get_json()
        
        varsta = float(date.get('varsta', 0))
        meciuri = float(date.get('meciuri', 0))
        goluri = float(date.get('goluri', 0))
        pase_gol = float(date.get('pase_gol', 0))
        pozitie = date.get('pozitie', 'Centre-Forward')
        
        jucator_nou = pd.DataFrame([{
            'Varsta': varsta,
            'Meciuri': meciuri,
            'Goluri': goluri,
            'Pase_Gol': pase_gol,
            'Pozitie': pozitie
        }])
        
        jucator_procesat = pd.get_dummies(jucator_nou, columns=['Pozitie'])
        jucator_procesat = jucator_procesat.reindex(columns=COLOANE_MODEL, fill_value=0)
        
        predictie = model.predict(jucator_procesat)[0]
        valoare_formatata = f"€{predictie / 1000000:.2f}m"
        
        return jsonify({
            'status': 'success',
            'valoare_estimata': predictie,
            'valoare_formatata': valoare_formatata
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(port=5000, debug=True)