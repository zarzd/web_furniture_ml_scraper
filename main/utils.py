import requests
from bs4 import BeautifulSoup
import spacy
import os
import re

model_path = os.path.join(os.path.dirname(__file__), '..', 'ml', 'output', 'model-best')
nlp = spacy.load(model_path)


def get_html_requests(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return None


def clean_text(text):
    """Удаляет лишние пробелы, табуляции и специальные символы из текста."""
    text = re.sub(r'\s+', ' ', text)  # Заменяем все пробельные символы на один пробел
    return text.strip()


def extract_product_names(url):
    """Извлекает текст из вложенных тегов, игнорируя родительские, для последующей ручной разметки."""
    html_content = get_html_requests(url)
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')

    for script in soup(["script", "style", "meta", "noscript"]):
        script.extract()

    unique_texts = set()
    text_blocks = []

    TAGS_TO_EXTRACT = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'p', 'li', 'div', 'span', 'a',
        'strong', 'b', 'em', 'i',
        'table', 'tr', 'td', 'th',
        'dl', 'dt', 'dd'
    ]

    def extract_inner_text(tag):
        if not tag.find(TAGS_TO_EXTRACT):
            text = tag.get_text(separator=" ", strip=True)
            text = clean_text(text)
            if text and text not in unique_texts:
                unique_texts.add(text)
                text_blocks.append(text)
        else:
            for inner_tag in tag.find_all(TAGS_TO_EXTRACT, recursive=False):
                extract_inner_text(inner_tag)

    for tag in soup.find_all(TAGS_TO_EXTRACT):
        extract_inner_text(tag)

    return text_blocks


def product_detection_model(url):
    texts = extract_product_names(url)
    detected_products = []

    for text in texts:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == 'PRODUCT':
                detected_products.append(ent.text.lower())

    return list(set(detected_products))
