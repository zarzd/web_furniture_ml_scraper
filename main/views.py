from django.shortcuts import render
from .forms import UrlForm
from .utils import product_detection_model  # Эта функция будет извлекать названия продуктов


def extract_products(request):
    if request.method == 'POST':
        form = UrlForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            products = product_detection_model(url)  # Логика парсинга сайта
            return render(request, 'result.html', {'products': products, 'url': url})
    else:
        form = UrlForm()

    return render(request, 'index.html', {'form': form})
