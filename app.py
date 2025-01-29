# Importamos las librerías necesarias para nuestro proyecto
from flask import Flask, render_template, request  # Para crear la aplicación web con Flask y renderizar plantillas HTML
import os  # Para interactuar con el sistema de archivos (manejar rutas y directorios)
import easyocr  # Librería para realizar el reconocimiento óptico de caracteres (OCR)
from werkzeug.utils import secure_filename  # Para asegurarnos de que los nombres de archivo sean seguros
from pdf2image import convert_from_path  # Para convertir archivos PDF a imágenes
import numpy as np  # Librería para manejar matrices, útil para convertir imágenes a arrays

# Creamos la aplicación de Flask
app = Flask(__name__)

# Configuraciones de la aplicación:
UPLOAD_FOLDER = 'static/uploaded_files'  # Definimos la carpeta donde se guardarán los archivos subidos
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}  # Extensiones de archivos permitidos para subir
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Asignamos la ruta del folder donde se guardarán los archivos

# Función para verificar si el archivo subido tiene una extensión permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    # Verifica si el archivo tiene extensión y si esta está permitida

# Ruta principal, que renderiza la página de inicio
@app.route('/')
def index():
    return render_template('index.html')  # Devuelve la plantilla HTML de la página de inicio

# Función para extraer los datos clave de un texto OCR
def extract_key_data(text_data):
    # Definimos una estructura base para los datos que queremos extraer
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
    
    # Dividimos el texto OCR en líneas para procesarlo
    lines = text_data.split("\n")
    
    # Recorremos las líneas para extraer la información específica
    for i, line in enumerate(lines):
        if "Solicitado por:" in line:
            # Extraemos los datos correspondientes a "Solicitado por" si encontramos la frase clave
            data["Solicitado_por"]["Numero"] = lines[i+1] if i+1 < len(lines) else ""
            data["Solicitado_por"]["Nombre"] = lines[i+2] if i+2 < len(lines) else ""
            data["Solicitado_por"]["Telefono"] = lines[i+3] if i+3 < len(lines) else ""
            data["Solicitado_por"]["Correo"] = lines[i+4] if i+4 < len(lines) else ""
        
        if "Entregar a:" in line:
            # Extraemos los datos correspondientes a "Entregar a" si encontramos la frase clave
            data["Entregar_a"]["Nombre"] = lines[i+1] if i+1 < len(lines) else ""
            data["Entregar_a"]["Telefono"] = lines[i+2] if i+2 < len(lines) else ""
            data["Entregar_a"]["Direccion"] = lines[i+3] if i+3 < len(lines) else ""
            data["Entregar_a"]["Notas"] = lines[i+4] if i+4 < len(lines) else ""
    
    return data  # Retornamos los datos extraídos

# Ruta para cargar y procesar archivos
@app.route('/upload', methods=['POST'])
def upload_file():
    # Verificamos que se haya subido un archivo
    if 'file' not in request.files:
        return render_template('error.html', message="No file part")
    
    file = request.files['file']
    
    # Verificamos que el archivo tenga un nombre válido
    if file.filename == '':
        return render_template('error.html', message="No selected file")
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Procesamos el archivo con OCR
        if filename.rsplit('.', 1)[1].lower() == 'pdf':
            images = convert_from_path(filepath)
            reader = easyocr.Reader(['en'])
            text_data = ""
            for image in images:
                image_np = np.array(image)
                result = reader.readtext(image_np)
                text_data += "\n".join([text[1] for text in result]) + "\n"
        else:
            reader = easyocr.Reader(['en'])
            result = reader.readtext(filepath)
            text_data = "\n".join([text[1] for text in result])
        
        extracted_data = extract_key_data(text_data)
        
        # Retornamos la plantilla con los datos extraídos
        return render_template('result.html', data=extracted_data)
    
    return render_template('error.html', message="Archivo no permitido")


# Iniciamos el servidor de la aplicación en modo debug (útil para desarrollo)
if __name__ == '__main__':
    app.run(debug=True)
