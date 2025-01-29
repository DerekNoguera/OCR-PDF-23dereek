import easyocr

def extract_text_from_image(image_path):
    # Leer el texto de la imagen
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image_path)
    
    # Convertir resultado en texto plano
    text_data = "\n".join([text[1] for text in result])
    
    return text_data
