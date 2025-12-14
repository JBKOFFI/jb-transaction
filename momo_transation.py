from flask import Flask, request
import datetime as dt

app = Flask(__name__)

# --- Données en mémoire ---
liste_comptes = []

# --------------------
# FONCTIONS DE GESTION DES COMPTES
# --------------------


def enregistrer_compte(numero, nom, prenom, date_naissance_str, code_secret):

    numero = numero         
    for c in liste_comptes:
        if c['numero_comptes'] == numero:
            return "❌ Ce numéro est déjà enregistré !"
    
    if len(code_secret) != 4 or not code_secret.isdigit():
        return "❌ Le code doit contenir exactement 4 chiffres !"
    
    try:
        date_naissance = dt.datetime.strptime(date_naissance_str, "%d/%m/%Y")
    except:
        return "❌ Format date invalide ! JJ/MM/AAAA attendu"
    
    compte = {
        "numero_comptes": numero,
        "nom": nom.upper(),
        "prenom": prenom.capitalize(),
        "date_naissance": date_naissance.strftime("%d/%m/%Y"),
        "code": code_secret,
        "solde": 0.0
    }
    liste_comptes.append(compte) 
    return (
    f"✅ Compte créé avec succès.<br>"
    f"<br>"
    f"📝 Voici les informations du compte :<br>"
    f"Numéro de compte :0{compte['numero_comptes']}<br>"
    f"Nom : {compte['nom']}<br>"
    f"Prénom : {compte['prenom']}<br>"
    f"Date de naissance : {compte['date_naissance']}<br>"
    
    f"Solde : {compte['solde']} FCFA"
)


def verifier_identite(code):

    if len(code) != 4 or not code.isdigit():
        return "❌ Code secret invalide"

    for compte in liste_comptes:
        if compte['code'] == code:
            return compte

    return "❌ Code secret incorrect OU compte inexistant !"




def afficher_solde(code):
    compte = verifier_identite(code)
    if compte:
        return{ f"💰 Bonjour {compte['prenom']} {compte['nom']}.<br>"
        f"Solde actuel : {compte['solde']} FCFA"}
    return "❌ Code secret invalide OU compte inexistant !"

def depot_argent(numero, montant):
    for compte in liste_comptes:
        if compte['numero_comptes'] == numero:
            if montant <= 0:
                return "❌ Montant invalide,vous est foché  !"
            compte['solde'] += montant
            return f"✅ Dépôt réussi ! Nouveau solde : {compte['solde']} FCFA"
    return "❌ Numéro non enregistré , veillez créer un compte d'abord !"

def retrait_argent(numero, montant,code):
    compte = verifier_identite(code)
    if not compte:
        return "❌ code secret incorrect, ou compte inexistant !"
    for compte in liste_comptes:
        if compte['numero_comptes'] == numero:
            if montant <= 0:
                return "❌ Montant invalide !, le montant doit être positif"
            if compte['solde'] < montant:
                return "❌ Solde insuffisant !"
            compte['solde'] -= montant
            return f"✅ Retrait réussi ! Nouveau solde : {compte['solde']} FCFA"
    return "❌ Numéro non enregistré !"

def transfert_argent(numero_dest, montant, code):
    code = str(code)   # ✅ CORRECTION ICI

    compte_exp = verifier_identite(code)

    if not isinstance(compte_exp, dict):
        return (
            "❌ Code secret incorrect ou compte inexistant.<br>"
            "Veuillez vérifier votre code secret ou créer un compte d'abord !"
        )

    if montant <= 0:
        return "❌ Montant invalide !"

    if compte_exp['solde'] < montant:
        return "❌ Solde insuffisant !"

    compte_dest = None
    for compte in liste_comptes:
        if compte['numero_comptes'] == numero_dest:
            compte_dest = compte
            break

    compte_exp['solde'] -= montant

    if compte_dest:
        compte_dest['solde'] += montant
        return f"✅ Transfert interne vers 0{numero_dest} réussi ! Nouveau solde : {compte_exp['solde']} FCFA"
    else:
        return f"✅ Transfert externe vers 0{numero_dest} réussi ! Nouveau solde : {compte_exp['solde']} FCFA"




def afficher_comptes():
    if not liste_comptes:
        return "<p>Aucun compte pour le moment</p>"
    html = ""
    for c in liste_comptes:
        html += f"""
        <div style='border:1px solid #ddd; padding:10px; margin:5px; border-radius:8px; background:#f9f9f9;'>
            <strong>Numéro:</strong> {c['numero_comptes']}<br>
            <strong>Nom:</strong> {c['nom']} {c['prenom']}<br>
            <strong>Date Naissance:</strong> {c['date_naissance']}<br>
            <strong>Solde:</strong> {c['solde']} FCFA<br>
            <form method="POST" action="/supprimer/{c['numero_comptes']}" onsubmit="return confirm('Êtes-vous sûr de vouloir supprimer le compte {c['numero_comptes']} ?');">
                <button type="submit">Supprimer</button>
            </form>
        </div>
        """
    return html

# --------------------
# GÉNÉRATION DU HTML



def generer_html(message=""):
    html = f"""
<html>
<head>
<title>💰 OM/Mobile Money de JB</title>

<style>
body {{
    margin: 0;
    padding: 0;
    font-family: 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #ff9500, #ff6a00);
    color: #222;
}}
.container {{
    max-width: 420px;
    margin: auto;
    background: #f9f9f9;
    min-height: 100vh;
    padding: 15px;
}}
.header {{
    text-align: center;
    margin-bottom: 15px;
}}
.header h1 {{
    font-size: 2em;
    font-weight: bold;
}}
.header h2 {{
    font-size: 1.2em;
    color: #555;
}}
.card {{
    background: white;
    border-radius: 15px;
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: 0 6px 15px rgba(0,0,0,0.15);
}}
.operations {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
}}
.op {{
    background: #fff;
    border-radius: 12px;
    padding: 12px;
    text-align: center;
    font-size: 14px;
    cursor: pointer;
    box-shadow: 0 4px 10px rgba(0,0,0,0.12);
    transition: transform 0.2s;
}}
.op:hover {{
    transform: scale(1.05);
}}
.message {{
    color: #d35400;
    font-weight: bold;
    text-align: center;
    margin: 10px 0;
}}
.form-container {{
    display: none;
    margin-top: 10px;
}}
input, button {{
    width: 100%;
    padding: 10px;
    margin-top: 8px;
    border-radius: 8px;
    border: 1px solid #ccc;
}}
button {{
    background: #ff6a00;
    color: white;
    border: none;
    font-size: 16px;
    cursor: pointer;
}}
button:hover {{
    background: #e65c00;
}}
.photo-card img {{
    width: 120px;
    border-radius: 50%;
    margin-top: 10px;
}}
.footer {{
    font-size: 13px;
    color: #555;
    margin-top: 8px;
}}
</style>

<script>
function showForm(id) {{
    document.querySelectorAll('.form-container').forEach(f => f.style.display='none');
    document.getElementById("message").innerHTML = "";
    document.querySelectorAll('.liste-comptes').forEach(c => c.style.display='none');
    if(id) document.getElementById(id).style.display='block';
}}

// Afficher ou cacher la liste des comptes
function toggleComptes() {{
    const liste = document.getElementById('liste_comptes');
    if(liste.style.display === 'block') {{
        liste.style.display = 'none';
    }} else {{
        liste.style.display = 'block';
    }}
}}

// Supprimer un compte avec confirmation
function supprimerCompte(numero) {{
    if(confirm('Êtes-vous sûr de vouloir supprimer le compte '+numero+' ?')) {{
        alert('Compte '+numero+' supprimé !'); // Ici tu peux appeler une route Flask pour supprimer réellement
    }}
}}
</script>
</head>

<body>
<div class="container">

<!-- HEADER + COMMENTAIRE BLEU -->
<div class="header">
  <h1>Bienvenue sur JB-Transaction</h1>
  <h2>Votre démo personnelle d'Orange Money et Mobile Money</h2>
  <p style="
      color: #0056b3; 
      font-size: 1em; 
      background-color: #e6f0ff; 
      padding: 10px 15px; 
      border-radius: 8px; 
      display: inline-block;
      margin-top: 15px;
      max-width: 500px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    ">
    ⚠️ Note importante : Cette application est une <strong>démo web personnelle</strong>. 
    Aucune connexion réelle aux services Orange ou MTN n’est effectuée ici. 
    Toutes les opérations sont simulées et <strong>ne doivent pas être utilisées avec de l’argent réel</strong>. 
    Amusez-vous à tester l’interface sur votre navigateur 💻😄, pas besoin de la mettre sur votre téléphone pour de vrai 📱💸 !
  </p>
</div>

<!-- CARTE OPERATIONS -->
<div class="card">
    <b>Opérations</b>
    <p style="color: blue; font-size: 0.9em;">Sélectionnez l’opération que vous souhaitez effectuer</p>
    <div class="operations">
        <div class="op" onclick="showForm('creer_form')">Créer<br>Compte</div>
        <div class="op" onclick="showForm('verifier_form')">Vérifier</div>
        <div class="op" onclick="showForm('solde_form')">Solde</div>
        <div class="op" onclick="showForm('depot_form')">Dépôt</div>
        <div class="op" onclick="showForm('retrait_form')">Retrait</div>
        <div class="op" onclick="showForm('transfert_form')">Transfert</div>
        <div class="op" onclick="toggleComptes()">Afficher<br>Comptes</div>
    </div>
</div>

<div id="message" class="message">{message}</div>

<!-- FORMULAIRES -->
<div id="creer_form" class="form-container card">
<form method="POST" action="/creer">
Numéro <input name="numero" required>
Nom <input name="nom" required>
Prénom <input name="prenom" required>
Date (JJ/MM/AAAA) <input name="date_naissance" required>
Code secret <input name="code" required>
<button>Créer</button>
</form>
</div>

<div id="verifier_form" class="form-container card">
<form method="POST" action="/verifier">
Code secret <input name="code" required>
<button>Vérifier</button>
</form>
</div>

<div id="solde_form" class="form-container card">
<form method="POST" action="/solde">
Code secret <input name="code" required>
<button>Voir solde</button>
</form>
</div>

<div id="depot_form" class="form-container card">
<form method="POST" action="/depot">
Numéro <input name="numero" required>
Montant <input name="montant" required>
<button>Déposer</button>
</form>
</div>

<div id="retrait_form" class="form-container card">
<form method="POST" action="/retrait">
Numéro <input name="numero" required>
Montant <input name="montant" required>
Code secret <input name="code" required>
<button>Retirer</button>
</form>
</div>

<div id="transfert_form" class="form-container card">
<form method="POST" action="/transfert">
Numéro destinataire <input name="numero_dest" required>
Montant <input name="montant" required>
Code secret <input name="code" required>
<button>Transférer</button>
</form>
</div>

<!-- LISTE DES COMPTES (CACHÉE PAR DÉFAUT) -->
<div id="liste_comptes" class="card liste-comptes" style="display:none;">
    <b>Comptes existants</b>
    {afficher_comptes()}
</div>

<!-- FOOTER PROFESSIONNEL -->
<div class="footer" style="
    background:#f0f0f0; 
    padding:20px; 
    display:flex; 
    justify-content:center; 
    align-items:center; 
    gap:20px; 
    border-top:1px solid #ccc;
">
    <div class="footer-left">
        <img src="/static/jb-photo.jpeg" alt="Jean-Baptiste Koffi" style="
            width:120px; 
            height:120px; 
            border-radius:50%;
            object-fit: cover;
        ">
    </div>

    <div class="footer-right" style="text-align:left;">
        <p style="margin:5px 0; font-weight:bold;">Développé avec passion par <strong>Jean-Baptiste Koffi</strong></p>
        <p style="margin:5px 0;">💻 Python & Flask</p>
        <p style="margin:5px 0;">📅 {dt.datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
    </div>
</div>



<script>
function toggleComptes() {{
    const liste = document.getElementById('liste_comptes');
    if(liste.style.display === 'block') {{
        liste.style.display = 'none';
    }} else {{
        liste.style.display = 'block';
    }}
}}

function supprimerCompte(numero) {{
    if(confirm('Êtes-vous sûr de vouloir supprimer le compte ' + numero + ' ?')) {{
        alert('Compte ' + numero + ' supprimé !');
    }}
}}
</script>





</div>
</body>
</html>
"""
    return html

# --------------------
# ROUTES FLASK
# --------------------
@app.route('/')
def index():
    return generer_html()

@app.route('/creer', methods=['POST'])
def creer_route():
    numero = int(request.form.get('numero'))
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    date_naissance = request.form.get('date_naissance')
    code = request.form.get('code')
    message = enregistrer_compte(numero, nom, prenom, date_naissance, code)
    return generer_html(message)

@app.route('/verifier', methods=['POST'])
def verifier_route():
    code = request.form.get('code')
    compte = verifier_identite(code)
    if compte:
        message = {f"💡 Compte trouvé pour:<br>"
        f"{compte['prenom']} {compte['nom']}<br>"
        f" Numéro: {compte['numero_comptes']}<br>"
         f" Solde: {compte['solde']} FCFA"}
    else:
        message = "❌ Code invalide ou compte inexistant !"
    return generer_html(message)

@app.route('/solde', methods=['POST'])
def solde_route():
    code = request.form.get('code')
    message = afficher_solde(code)
    return generer_html(message)

@app.route('/depot', methods=['POST'])
def depot_route():
    numero = int(request.form.get('numero'))
    montant = float(request.form.get('montant'))
    message = depot_argent(numero, montant)
    return generer_html(message)

@app.route('/retrait', methods=['POST'])
def retrait_route():
    # Récupération des données du formulaire
    numero = int(request.form.get('numero'))
    montant = float(request.form.get('montant'))
    code = request.form.get('code')  # Récupération du code secret

    # Appel de la fonction avec les 3 paramètres
    message = retrait_argent(numero, montant, code)

    return generer_html(message)


@app.route('/transfert', methods=['POST'])
def transfert_route():
    code = request.form.get('code')
    numero_dest = int(request.form.get('numero_dest'))
    montant = float(request.form.get('montant'))
    message = transfert_argent(numero_dest, montant,code)
    return generer_html(message)

@app.route('/supprimer/<int:numero>', methods=['POST'])
def supprimer_compte(numero):
    global liste_comptes
    liste_comptes = [c for c in liste_comptes if c['numero_comptes'] != numero]
    return generer_html(f"✅ Compte {numero} supprimé avec succès !")


# --------------------
# LANCEMENT
# --------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    print("Au revoir!")