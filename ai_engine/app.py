from flask import Flask, request, jsonify
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

app = Flask(__name__)

print("=== 1. Antrenare Model ML Super-Inteligent (cu FIFA Ratings) ===")

# 1. CITIM FIȘIERUL COMPLET
nume_fisier = 'top_500.csv' # Asigură-te că acesta este numele corect!
try:
    df = pd.read_csv(nume_fisier)
    print(f"Am încărcat cu succes {len(df)} jucători din {nume_fisier}.")
except FileNotFoundError:
    print(f"[EROARE] Nu găsesc fișierul '{nume_fisier}'! Asigură-te că e în același folder cu app.py.")
    exit()

# 2. CURĂȚAREA DATELOR (Inclusiv noile coloane)
# Funcție pentru valoarea în Euro
def curata_valoare(val_str):
    if pd.isna(val_str) or str(val_str).strip() == "0" or str(val_str).strip() == "-": 
        return 0
    val_str = str(val_str).replace('€', '').strip()
    if 'm' in val_str: 
        return float(val_str.replace('m', '')) * 1_000_000
    if 'k' in val_str: 
        return float(val_str.replace('k', '')) * 1_000
    return 0

df['Valoare_Numar'] = df['Valoare_Piata'].apply(curata_valoare)

# Curățăm coloanele matematice de posibile cratime sau texte dubioase
coloane_numerice = ['Varsta', 'Meciuri', 'Goluri', 'Pase_Gol', 'Overall', 'Potential']
for col in coloane_numerice:
    if col in df.columns:
        df[col] = df[col].astype(str).replace('-', '0')
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    else:
        print(f"[AVERTISMENT] Coloana {col} lipsește din CSV!")

# 3. ANTRENAMENTUL AI-ULUI
# Acum AI-ul primește 7 factori de decizie în loc de 5!
X_brut = df[['Varsta', 'Meciuri', 'Goluri', 'Pase_Gol', 'Overall', 'Potential', 'Pozitie']]
y = df['Valoare_Numar']

# Transformăm textul (Pozitie) în numere (0 și 1)
X_procesat = pd.get_dummies(X_brut, columns=['Pozitie'])
COLOANE_MODEL = X_procesat.columns 

# Creăm și antrenăm Random Forest-ul
model = RandomForestRegressor(n_estimators=150, random_state=42) # Am crescut la 150 de "copaci" pentru precizie
model.fit(X_procesat, y)
print("✅ Model antrenat cu succes! Acum ține cont de Rating și Potențial.")

print("\n=== 2. Pornire API pe portul 5000 ===")
@app.route('/predict', methods=['POST'])
def predict():
    try:
        date = request.get_json()
        
        # Preluăm datele trimise de Java (inclusiv ovr și pot)
        jucator_nou = pd.DataFrame([{
            'Varsta': float(date.get('varsta', 0)),
            'Meciuri': float(date.get('meciuri', 0)),
            'Goluri': float(date.get('goluri', 0)),
            'Pase_Gol': float(date.get('pase_gol', 0)),
            'Overall': float(date.get('ovr', 80)),       # Rating-ul curent
            'Potential': float(date.get('pot', 85)),     # Potențialul
            'Pozitie': date.get('pozitie', 'Centre-Forward')
        }])
        
        # Procesăm datele noului jucător la fel cum am procesat la antrenament
        jucator_procesat = pd.get_dummies(jucator_nou, columns=['Pozitie'])
        jucator_procesat = jucator_procesat.reindex(columns=COLOANE_MODEL, fill_value=0)
        
        # Facem predicția
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