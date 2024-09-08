from flask import Flask, render_template_string, request, send_file
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

app = Flask(__name__)

# Template HTML pour le formulaire
form_template = '''
<!doctype html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Formulaire de Réservation</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            width: 400px;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        input, select {
            width: 100%;
            padding: 10px;
            margin-bottom: 16px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        input[type="submit"] {
            background: #28a745;
            color: #fff;
            border: none;
            cursor: pointer;
            font-size: 16px;
        }
        input[type="submit"]:hover {
            background: #218838;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Formulaire de Réservation</h1>
        <form method="post" action="{{ url_for('submit_form') }}">
            <label for="nom">Nom :</label>
            <input type="text" id="nom" name="nom" required>
            
            <label for="prenom">Prénom :</label>
            <input type="text" id="prenom" name="prenom" required>
            
            <label for="age">Âge :</label>
            <input type="number" id="age" name="age" required>
            
            <label for="situation">Situation :</label>
            <select id="situation" name="situation" required>
                <option value="célibataire">Célibataire</option>
                <option value="marié">Marié</option>
                <option value="divorcé">Divorcé</option>
                <option value="veuf">Veuf</option>
            </select>
            
            <label for="date">Date de réservation :</label>
            <input type="date" id="date" name="date" required>
            
            <input type="submit" value="Envoyer">
        </form>
    </div>
</body>
</html>
'''

# Route pour afficher le formulaire
@app.route('/')
def index():
    return render_template_string(form_template)

# Route pour traiter les données du formulaire
@app.route('/submit', methods=['POST'])
def submit_form():
    nom = request.form.get('nom', '')
    prenom = request.form.get('prenom', '')
    age = request.form.get('age', '')
    situation = request.form.get('situation', '')
    date = request.form.get('date', '')

    # Créer un objet en mémoire pour le PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Ajouter un titre en bleu
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(HexColor("#0000FF"))  # Bleu
    c.drawString(72, height - 72, "Réservation Confirmée")
    
    # Ajouter des données au PDF
    c.setFont("Helvetica", 12)
    c.setFillColor(HexColor("#000000"))  # Noir
    c.drawString(72, height - 100, f"Nom: {nom}")
    c.drawString(72, height - 128, f"Prénom: {prenom}")
    c.drawString(72, height - 156, f"Âge: {age}")
    c.drawString(72, height - 184, f"Situation: {situation}")
    c.drawString(72, height - 212, f"Date de réservation: {date}")

    # Ajouter un message de confirmation
    c.setFont("Helvetica-Oblique", 12)
    c.drawString(72, height - 240, "Merci de votre réservation. Nous vous attendons avec impatience!")

    # Finaliser le PDF
    c.showPage()
    c.save()

    # Retourner le fichier PDF en réponse
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='reservation.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
