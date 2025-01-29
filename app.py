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

            if "Correo" in line or "Email" in line:
                data["Solicitado_por"]["Correo"] = lines[i+4] if i+4 < len(lines) else ""
        
        if "Entregar a:" in line:
            # Extraemos los datos correspondientes a "Entregar a" si encontramos la frase clave
            data["Entregar_a"]["Nombre"] = lines[i+1] if i+1 < len(lines) else ""
            data["Entregar_a"]["Telefono"] = lines[i+2] if i+2 < len(lines) else ""
            data["Entregar_a"]["Direccion"] = lines[i+3] if i+3 < len(lines) else ""
            data["Entregar_a"]["Notas"]  = lines[i+4] if i+4 < len(lines) else ""
    
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





# Importamos las librerías necesarias para nuestro proyecto
# from flask import Flask, render_template, request, redirect  # Agregamos redirect
# import os
# import easyocr
# from werkzeug.utils import secure_filename
# from pdf2image import convert_from_path
# import numpy as np
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# import webbrowser  # Importamos webbrowser para abrir la hoja de cálculo

# app = Flask(__name__)

# UPLOAD_FOLDER = 'static/uploaded_files'
# ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/')
# def index():
#     return render_template('index.html')

# def extract_key_data(text_data):
#     data = {
#         "Solicitado_por": {
#             "Numero": "",
#             "Nombre": "",
#             "Telefono": "",
#             "Correo": ""
#         },
#         "Entregar_a": {
#             "Nombre": "",
#             "Telefono": "",
#             "Direccion": "",
#             "Notas": ""
#         }
#     }
    
#     lines = text_data.split("\n")
    
#     for i, line in enumerate(lines):
#         if "Solicitado por:" in line:
#             data["Solicitado_por"]["Numero"] = lines[i+1] if i+1 < len(lines) else ""
#             data["Solicitado_por"]["Nombre"] = lines[i+2] if i+2 < len(lines) else ""
#             data["Solicitado_por"]["Telefono"] = lines[i+3] if i+3 < len(lines) else ""
#             data["Solicitado_por"]["Correo"] = lines[i+4] if i+4 < len(lines) else ""
        
#         if "Entregar a:" in line:
#             data["Entregar_a"]["Nombre"] = lines[i+1] if i+1 < len(lines) else ""
#             data["Entregar_a"]["Telefono"] = lines[i+2] if i+2 < len(lines) else ""
#             data["Entregar_a"]["Direccion"] = lines[i+3] if i+3 < len(lines) else ""
#             data["Entregar_a"]["Notas"] = lines[i+4] if i+4 < len(lines) else ""
    
#     return data

# def authenticate_google_sheets():
#     scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]
#     creds = ServiceAccountCredentials.from_json_keyfile_name("credenciales.json", scope)
#     client = gspread.authorize(creds)
    
#     print("Autenticación exitosa con Google Sheets.")
    
#     return client

# def create_or_open_sheet(client):
#     try:
#         sheet = client.open("DatosOCR").sheet1
#         print("Hoja de cálculo 'DatosOCR' abierta exitosamente.")
#     except gspread.exceptions.SpreadsheetNotFound:
#         print("Hoja no encontrada. Creando una nueva hoja.")
#         sheet = client.create("DatosOCR").sheet1
#     return sheet

# def save_data_to_sheet(sheet, extracted_data):
#     print("Guardando los siguientes datos en la hoja:")
#     print(extracted_data)

#     sheet.append_row([extracted_data["Solicitado_por"]["Numero"],
#                       extracted_data["Solicitado_por"]["Nombre"],
#                       extracted_data["Solicitado_por"]["Telefono"],
#                       extracted_data["Solicitado_por"]["Correo"],
#                       extracted_data["Entregar_a"]["Nombre"],
#                       extracted_data["Entregar_a"]["Telefono"],
#                       extracted_data["Entregar_a"]["Direccion"],
#                       extracted_data["Entregar_a"]["Notas"]])

#     print("Datos guardados exitosamente en la hoja de cálculo.")
    
#     # Abrir la hoja de cálculo en el navegador
#     sheet_url = sheet.url  # Obtener el URL de la hoja de cálculo
#     webbrowser.open(sheet_url)  # Abre el enlace en el navegador

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return render_template('error.html', message="No file part")
    
#     file = request.files['file']
    
#     if file.filename == '':
#         return render_template('error.html', message="No selected file")
    
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(filepath)
        
#         if filename.rsplit('.', 1)[1].lower() == 'pdf':
#             images = convert_from_path(filepath)
#             reader = easyocr.Reader(['en'])
#             text_data = ""
#             for image in images:
#                 image_np = np.array(image)
#                 result = reader.readtext(image_np)
#                 text_data += "\n".join([text[1] for text in result]) + "\n"
#         else:
#             reader = easyocr.Reader(['en'])
#             result = reader.readtext(filepath)
#             text_data = "\n".join([text[1] for text in result])
        
#         extracted_data = extract_key_data(text_data)
        
#         client = authenticate_google_sheets()
#         sheet = create_or_open_sheet(client)
#         save_data_to_sheet(sheet, extracted_data)
        
#         return render_template('result.html', data=extracted_data)
    
#     return render_template('error.html', message="Archivo no permitido")

# if __name__ == '__main__':
#     app.run(debug=True)





# from flask import Flask, render_template, request, redirect, url_for, session
# import os
# import easyocr
# from werkzeug.utils import secure_filename
# from pdf2image import convert_from_path
# import numpy as np
# import google_auth_oauthlib.flow
# import googleapiclient.discovery
# import googleapiclient.errors
# import json

# # Configuración de la aplicación
# app = Flask(__name__)
# app.secret_key = 'your_secret_key'
# UPLOAD_FOLDER = 'static/uploaded_files'
# ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Definimos los SCOPES de acceso para Google Sheets
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# # Definimos la ruta para verificar si el archivo subido tiene una extensión permitida
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# # Ruta para la página de inicio
# @app.route('/')
# def index():
#     return render_template('index.html')

# # Función para extraer los datos con OCR
# def extract_key_data(text_data):
#     data = {
#         "Solicitado_por": {
#             "Numero": "",
#             "Nombre": "",
#             "Telefono": "",
#             "Correo": ""
#         },
#         "Entregar_a": {
#             "Nombre": "",
#             "Telefono": "",
#             "Direccion": "",
#             "Notas": ""
#         }
#     }
#     lines = text_data.split("\n")
    
#     for i, line in enumerate(lines):
#         if "Solicitado por:" in line:
#             data["Solicitado_por"]["Numero"] = lines[i+1] if i+1 < len(lines) else ""
#             data["Solicitado_por"]["Nombre"] = lines[i+2] if i+2 < len(lines) else ""
#             data["Solicitado_por"]["Telefono"] = lines[i+3] if i+3 < len(lines) else ""
#             data["Solicitado_por"]["Correo"] = lines[i+4] if i+4 < len(lines) else ""
        
#         if "Entregar a:" in line:
#             data["Entregar_a"]["Nombre"] = lines[i+1] if i+1 < len(lines) else ""
#             data["Entregar_a"]["Telefono"] = lines[i+2] if i+2 < len(lines) else ""
#             data["Entregar_a"]["Direccion"] = lines[i+3] if i+3 < len(lines) else ""
#             data["Entregar_a"]["Notas"] = lines[i+4] if i+4 < len(lines) else ""
    
#     return data

# # Función para el flujo OAuth 2.0 de Google
# def get_google_sheets_service():
#     CLIENT_SECRETS_FILE = 'client_secrets.json'  # Archivo descargado desde la consola de Google
    
#     flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
#         CLIENT_SECRETS_FILE, SCOPES)
    
#     # Usa la URL pública de ngrok
#     flow.redirect_uri = "https://ocr-pdf-23dereek-1.onrender.com/oauth2callback"  # Usa la URL HTTPS

#     authorization_url, state = flow.authorization_url(access_type='offline')
#     session['state'] = state
#     return flow, authorization_url

# # Ruta para autorizar con Google
# @app.route('/authorize')
# def authorize():
#     flow, authorization_url = get_google_sheets_service()
#     return redirect(authorization_url)

# # Ruta de callback de Google OAuth 2.0
# @app.route('/oauth2callback')
# def oauth2callback():
#     flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
#         'client_secrets.json', SCOPES)
#     flow.redirect_uri = url_for('oauth2callback', _external=True)
    
#     authorization_response = request.url
#     flow.fetch_token(authorization_response=authorization_response)

#     credentials = flow.credentials
#     session['credentials'] = credentials_to_dict(credentials)
    
#     return redirect(url_for('upload_file'))

# # Convertir credenciales a formato dict para usarlas más tarde
# def credentials_to_dict(credentials):
#     return {
#         'token': credentials.token,
#         'refresh_token': credentials.refresh_token,
#         'token_uri': credentials.token_uri,
#         'client_id': credentials.client_id,
#         'client_secret': credentials.client_secret,
#         'scopes': credentials.scopes
#     }

# # Ruta para cargar el archivo y guardarlo en la hoja
# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return render_template('error.html', message="No file part")
    
#     file = request.files['file']
    
#     if file.filename == '':
#         return render_template('error.html', message="No selected file")
    
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(filepath)
        
#         # Procesamos el archivo con OCR
#         if filename.rsplit('.', 1)[1].lower() == 'pdf':
#             images = convert_from_path(filepath)
#             reader = easyocr.Reader(['en'])
#             text_data = ""
#             for image in images:
#                 image_np = np.array(image)
#                 result = reader.readtext(image_np)
#                 text_data += "\n".join([text[1] for text in result]) + "\n"
#         else:
#             reader = easyocr.Reader(['en'])
#             result = reader.readtext(filepath)
#             text_data = "\n".join([text[1] for text in result])
        
#         extracted_data = extract_key_data(text_data)

#         # Recuperamos las credenciales de la sesión
#         credentials = session.get('credentials')
#         if not credentials:
#             return redirect(url_for('authorize'))
        
#         # Crear un servicio para interactuar con la hoja de cálculo
#         service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)
#         sheet_id = 'your_sheet_id_here'  # Reemplaza con el ID de la hoja de cálculo

#         # Añadir los datos extraídos a la hoja de cálculo
#         range_ = 'Sheet1!A1'  # Cambia esto según la ubicación de tus datos
#         values = [
#             [extracted_data["Solicitado_por"]["Numero"],
#              extracted_data["Solicitado_por"]["Nombre"],
#              extracted_data["Solicitado_por"]["Telefono"],
#              extracted_data["Solicitado_por"]["Correo"],
#              extracted_data["Entregar_a"]["Nombre"],
#              extracted_data["Entregar_a"]["Telefono"],
#              extracted_data["Entregar_a"]["Direccion"],
#              extracted_data["Entregar_a"]["Notas"]]
#         ]
        
#         body = {'values': values}
#         result = service.spreadsheets().values().append(spreadsheetId=sheet_id,
#                                                         range=range_,
#                                                         valueInputOption="RAW", body=body).execute()

#         return render_template('result.html', data=extracted_data)

#     return render_template('error.html', message="Archivo no permitido")

# # Iniciar el servidor
# if __name__ == '__main__':
#     port = int(os.getenv("PORT", 5000))  # Usa el puerto que Render asigna automáticamente
#     app.run(host='0.0.0.0', port=port)
