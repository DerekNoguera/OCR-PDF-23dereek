# from flask import Flask, render_template, request, send_from_directory
# import os
# import easyocr
# from werkzeug.utils import secure_filename

# app = Flask(__name__)

# # Configuración para subir archivos
# UPLOAD_FOLDER = 'static/uploaded_files'
# ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Verificar las extensiones de los archivos
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# # Ruta principal
# @app.route('/')
# def index():
#     return render_template('index.html')

# # Ruta para cargar y procesar archivos PDF
# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return "No file part"
    
#     file = request.files['file']
    
#     if file.filename == '':
#         return "No selected file"
    
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(filepath)
        
#         # Procesar el archivo con OCR
#         reader = easyocr.Reader(['en'])
#         result = reader.readtext(filepath)
        
#         # Extraer los datos de OCR
#         text_data = "\n".join([text[1] for text in result])
        
#         return f'<h1>Texto Detectado:</h1><pre>{text_data}</pre>'
    
#     return 'Archivo no permitido'

# if __name__ == '__main__':
#     app.run(debug=True)
from flask import Flask, render_template, request
import os
import easyocr
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuración para subir archivos
UPLOAD_FOLDER = 'static/uploaded_files'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Verificar las extensiones de los archivos
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Extraer datos clave de la imagen procesada
def extract_key_data(text_data):
    data = {
        "Solicitado_por": {
            "Numero": "",
            "Nombre": "",
            "Telefono": "",
            "Correo": ""
        },
        "Entregar_a": {
            "Nombre": "",
            "Telefono": "",
            "Direccion": "",
            "Notas": ""
        }
    }
    
    lines = text_data.split("\n")
    
    for i, line in enumerate(lines):
        if "Solicitado por:" in line:
            data["Solicitado_por"]["Numero"] = lines[i+1] if i+1 < len(lines) else ""
            data["Solicitado_por"]["Nombre"] = lines[i+2] if i+2 < len(lines) else ""
            data["Solicitado_por"]["Telefono"] = lines[i+3] if i+3 < len(lines) else ""
            data["Solicitado_por"]["Correo"] = lines[i+4] if i+4 < len(lines) else ""
        
        if "Entregar a:" in line:
            data["Entregar_a"]["Nombre"] = lines[i+1] if i+1 < len(lines) else ""
            data["Entregar_a"]["Telefono"] = lines[i+2] if i+2 < len(lines) else ""
            data["Entregar_a"]["Direccion"] = lines[i+3] if i+3 < len(lines) else ""
            data["Entregar_a"]["Notas"] = lines[i+4] if i+4 < len(lines) else ""
    
    return data

# Ruta para cargar y procesar archivos
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('error.html', message="No file part")
    
    file = request.files['file']
    
    if file.filename == '':
        return render_template('error.html', message="No selected file")
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Procesar el archivo con OCR
        reader = easyocr.Reader(['en'])
        result = reader.readtext(filepath)
        
        # Extraer el texto detectado
        text_data = "\n".join([text[1] for text in result])
        extracted_data = extract_key_data(text_data)
        
        return render_template('result.html', data=extracted_data)
    
    return render_template('error.html', message="Archivo no permitido")

if __name__ == '__main__':
    app.run(debug=True)
