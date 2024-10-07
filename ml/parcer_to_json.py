import requests
from bs4 import BeautifulSoup
import re
import json
import csv


def get_html(url):
    """Отправляет HTTP-запрос и возвращает HTML-код страницы."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении страницы: {e}")
        return None


def clean_text(text):
    """Удаляет лишние пробелы, табуляции и специальные символы из текста."""
    # Удаление всех многократных пробелов, табуляций и переносов строк
    text = re.sub(r'\s+', ' ', text)  # Заменяем все пробельные символы на один пробел
    return text.strip()


def parse_html_for_annotation(html_content):
    """Извлекает текст из вложенных тегов, игнорируя родительские, для последующей ручной разметки."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Удаляем ненужные теги <script>, <style>, <meta>, <noscript>
    for script in soup(["script", "style", "meta", "noscript"]):
        script.extract()

    unique_texts = set()
    text_blocks = []

    TAGS_TO_EXTRACT = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',  # Заголовки
        'p', 'li', 'div', 'span', 'a',  # Основные текстовые блоки
        'strong', 'b', 'em', 'i',  # Выделенный текст
        'table', 'tr', 'td', 'th',  # Таблицы
        'dl', 'dt', 'dd'  # Описательные списки
    ]

    def extract_inner_text(tag):
        """Рекурсивная функция для извлечения текста только из вложенных элементов"""
        # Если элемент не содержит других тегов
        if not tag.find(TAGS_TO_EXTRACT):
            text = tag.get_text(separator=" ", strip=True)
            text = clean_text(text)  # Очищаем текст
            if text and text not in unique_texts:
                unique_texts.add(text)
                text_blocks.append(text)
        else:

            for inner_tag in tag.find_all(TAGS_TO_EXTRACT, recursive=False):
                extract_inner_text(inner_tag)

    for tag in soup.find_all(TAGS_TO_EXTRACT):
        extract_inner_text(tag)

    return text_blocks


def process_urls(urls, output_file):
    """Обрабатывает список URL и сохраняет результаты в JSON в нужном формате."""
    results = []
    id_counter = 1

    for url in urls:
        print(f"Обрабатываю URL: {url}")
        html = get_html(url)

        if html:
            tokenized_sentences = parse_html_for_annotation(html)
            for sentence in tokenized_sentences:
                results.append({
                    "id": id_counter,
                    "data": {
                        "text": sentence
                    }
                })
                id_counter += 1

    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(results, file, ensure_ascii=False, indent=4)

    print(f"Результаты сохранены в файл {output_file}")


def read_urls_from_csv(csv_file):
    """Читает URL из CSV-файла, где каждая строка содержит полный URL в одной колонке."""
    urls = []
    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                if len(row) < 1:
                    print(f"Пропущена пустая строка: {row}")
                    continue
                url = row[0].strip()
                if url:
                    urls.append(url)
                else:
                    print(f"Пропущена строка с пустым URL: {row}")
    except FileNotFoundError:
        print(f"Файл {csv_file} не найден.")
    return urls


csv_file = 'data//URL_list.csv'
urls = read_urls_from_csv(csv_file)

if urls:
    output_file = 'extracted_products_1.json'
    process_urls(urls, output_file)
