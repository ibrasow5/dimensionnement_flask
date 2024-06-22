from flask import Flask, render_template, request, jsonify, send_file
import math
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle

app = Flask(__name__)

# Route principale pour l'interface web
@app.route('/')
def index():
    return render_template('index.html')

# Route pour ouvrir la carte interactive
@app.route('/open_map')
def open_map():
    return render_template('map.html')

# Route pour calculer la distance et renvoyer le résultat
@app.route('/calculate_distance', methods=['POST'])
def calculate_distance():
    data = request.get_json()
    lat1 = float(data['lat1'])
    lon1 = float(data['lon1'])
    lat2 = float(data['lat2'])
    lon2 = float(data['lon2'])
    
    # Calculer la distance entre les deux points
    distance_km = calculate_distance_between_points(lat1, lon1, lat2, lon2)
    
    return jsonify({'distance_km': distance_km})

# Fonction pour calculer la distance entre deux points
def calculate_distance_between_points(lat1, lon1, lat2, lon2):
    # Utilisez ici une formule mathématique ou une API de cartographie pour calculer la distance réelle
    # Exemple simplifié avec la formule de Haversine pour une estimation
    radius = 6371  # Rayon de la Terre en km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance_km = radius * c
    return distance_km

# Route pour le calcul de la puissance reçue et affichage du graphique
@app.route('/calculate_power', methods=['POST'])
def calculate_power():
    data = request.get_json()
    Pt = float(data['Pt'])
    d = float(data['d'])
    f = float(data['f'])
    Le = float(data['Le'])
    Gt = float(data['Gt'])
    Gr = float(data['Gr'])
    
    distances = [i for i in range(1, int(d) + 1)]
    puissances_recues = []
    for dist in distances:
        lp_db = 20 * (math.log10(dist) + math.log10(f)) + 32.44
        Pr = Pt + Gt + Gr - lp_db - Le
        puissances_recues.append(Pr)
    
    # Générer le graphique et le renvoyer en tant qu'image
    img = generate_plot(distances, puissances_recues)
    return send_file(img, mimetype='image/png')

# Fonction pour générer le graphique de puissance reçue
def generate_plot(distances, puissances_recues):
    plt.figure(figsize=(10, 6))
    plt.plot(distances, puissances_recues, marker='o')
    plt.title('Puissance Reçue en fonction de la Distance')
    plt.xlabel('Distance (km)')
    plt.ylabel('Puissance Reçue (dBm)')
    plt.grid(True)
    
    # Convertir le graphique en image BytesIO pour l'envoi
    img = BytesIO()
    plt.savefig(img)
    img.seek(0)
    plt.close()
    
    return img

# Route pour générer le rapport PDF
@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    data = request.get_json()
    Pt = float(data['Pt'])
    d = float(data['d'])
    f = float(data['f'])
    Le = float(data['Le'])
    Gt = float(data['Gt'])
    Gr = float(data['Gr'])
    Pr = float(data['Pr'])
    
    # Générer et renvoyer le rapport PDF
    pdf = generate_report(Pt, d, f, Le, Gt, Gr, Pr)
    return send_file(pdf, attachment_filename='rapport.pdf', as_attachment=True)

# Fonction pour générer le rapport PDF
def generate_report(Pt, d, f, Le, Gt, Gr, Pr):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Titre du document
    title = Paragraph("Rapport de Calcul de Puissance Reçue", ParagraphStyle(name='TitleStyle',
                         fontSize=18, alignment=1, spaceAfter=20))
    elements.append(title)

    # Tableau des paramètres
    data = [
        ["Paramètre", "Valeur"],
        ["Puissance de Transmission (dBm)", Pt],
        ["Distance de Transmission (km)", d],
        ["Fréquence (MHz)", f],
        ["Pertes d'Équipements (dB)", Le],
        ["Gain de l'Antenne de Transmission (dB)", Gt],
        ["Gain de l'Antenne de Réception (dB)", Gr],
        ["Puissance reçue (dBm)", f"{Pr:.2f}"]
    ]

    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    table = Table(data)
    table.setStyle(table_style)
    elements.append(table)

    # Générer le PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

if __name__ == '__main__':
    app.run(debug=True)

