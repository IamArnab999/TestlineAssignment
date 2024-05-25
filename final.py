from google.cloud import vision
import io
import cv2
import numpy as np

def analyze_image(image_path):
    client = vision.ImageAnnotatorClient()
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)
    return response

def extract_text(response):
    text_annotations = response.text_annotations
    extracted_texts = []
    for text in text_annotations:
        extracted_texts.append({
            'description': text.description,
            'bounding_poly': text.bounding_poly
        })
    return extracted_texts

def segment_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)
    
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    segments = []
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        segment = image[y:y+h, x:x+w]
        segments.append(segment)
    
    return segments

def generate_html(texts, segments):
    html_content = '<html><body>'
    
    for text in texts:
        html_content += f'<p>{text["description"]}</p>'
    
    for i, segment in enumerate(segments):
        segment_path = f'segment_{i}.png'
        cv2.imwrite(segment_path, segment)
        html_content += f'<img src="{segment_path}" />'
    
    html_content += '</body></html>'
    return html_content

def main(image_path):
    response = analyze_image(image_path)
    texts = extract_text(response)
    segments = segment_image(image_path)
    html_content = generate_html(texts, segments)
    
    with open('output.html', 'w') as html_file:
        html_file.write(html_content)
    print('HTML content generated and saved as output.html')

if __name__ == "__main__":
    main('imgwithtextpng')
