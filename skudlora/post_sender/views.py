import requests
from django.http import JsonResponse

def send_post_request(request):
    # Пример данных для отправки
    url = 'http://example.com/api'
    data = {
        'key1': 'value1',
        'key2': 'value2',
    }

    try:
        response = requests.post(url, data=data)
        response.raise_for_status()  # Проверка на успешный статус

        return JsonResponse({'status': 'success', 'response': response.json()})
    except requests.exceptions.RequestException as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
