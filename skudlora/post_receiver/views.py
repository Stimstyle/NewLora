from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # Для отключения проверки CSRF (если требуется)
from post_receiver.models import DeviceData, APIKey    # Импортируем модель из того же приложения
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin.sites import site
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
import json
import random
import requests

@csrf_exempt  # Уберите эту строку, если CSRF-токен используется
def handle_post_request(request):
    if request.method == 'POST':
        # Получаем данные из тела запроса как JSON
        try:
            data = json.loads(request.body.decode('utf-8'))  # Декодируем и преобразуем JSON в словарь
        except json.JSONDecodeError:
            return JsonResponse({"error": "Некорректный JSON"}, status=400)

        # Извлекаем нужные поля из JSON
        device_name = data.get("deviceName")
        dev_eui = data.get("devEUI")
        payload_data = str(data.get("data"))
        time = data.get("time")
        
        # Для rxInfo (если это список, можно взять первый элемент)
        rssi = data.get("rxInfo", [{}])[0].get("rssi")
        lo_ra_snr = data.get("rxInfo", [{}])[0].get("loRaSNR")

        # Логика обработки данных
        print(f"deviceName: {device_name}")
        print(f"devEUI: {dev_eui}")
        print(f"data: {payload_data}")
        print(f"time: {time}")
        print(f"rssi: {rssi}")
        print(f"loRaSNR: {lo_ra_snr}")

        # Проверка на существование записи с таким deviceName и dev_eui
        device_data = DeviceData.objects.filter(device_name=device_name, dev_eui=dev_eui).first()

        if device_data:
            # Если запись существует, обновляем данные
            device_data.device_name = device_name
            device_data.data = payload_data
            device_data.time = time
            device_data.rssi = rssi
            device_data.lo_ra_snr = lo_ra_snr
            device_data.save()
            print(f"Устройство с deviceName '{device_name}' и devEUI '{dev_eui}' обновлено.")
        else:
            # Если запись не найдена, выводим ошибку в командной строке
            print(f"Ошибка: Устройство с deviceName '{device_name}' и devEUI '{dev_eui}' не найдено в базе данных.")
            return JsonResponse({"error": f"Устройство с deviceName '{device_name}' и devEUI '{dev_eui}' не найдено в базе данных."}, status=404)

        # Возвращаем ответ с извлечёнными данными
        return JsonResponse({
            "status": "success",
            "deviceName": device_name,
            "devEUI": dev_eui,
            "data": payload_data,
            "time": time,
            "rssi": rssi,
            "loRaSNR": lo_ra_snr,
        })
    else:
        return JsonResponse({"error": "Только POST-запросы поддерживаются"}, status=405)

 # Декоратор для ограничения доступа только для администраторов
@staff_member_required
def hex_sent_view(request):
    # Получаем параметры поиска и настройки количества элементов на странице
    search_query = request.GET.get('search', '')
    items_per_page = int(request.GET.get('items_per_page', 10))

    # Фильтруем устройства по поисковому запросу
    devices = DeviceData.objects.all()
    if search_query:
        # Используем Q для комбинирования условий с логическим "или"
        devices = devices.filter(
            Q(dev_eui__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Пагинация
    paginator = Paginator(devices, items_per_page)
    page_number = request.GET.get('page')
    devices = paginator.get_page(page_number)

    # Формируем контекст для шаблона
    context = {
        'devices': devices,
        'items_per_page': items_per_page,
        "available_apps": site.each_context(request).get("available_apps")  # Получаем доступные приложения
    }

    # Рендерим шаблон
    return render(request, 'admin/hex_sent_page.html', context)


def send_post_request_ernets(dev_eui, flush_downlink_queue, payload_hex):
    try:
        # Получаем объект устройства, используя dev_eui
        device = DeviceData.objects.get(dev_eui=dev_eui)

        # Получаем связанный API ключ для этого устройства
        # Предполагаем, что у вас есть связь между устройством и API ключом через модель
        api_key = device.api_key.api_key  # Получаем ключ API, связанный с устройством

    except DeviceData.DoesNotExist:
        return {'error': 'Device with the given DevEUI not found'}

    except APIKey.DoesNotExist:
        return {'error': 'API key for the device not found'}

    # Формируем URL с devEUI
    url = f"https://ernet.ertelecom.ru/api/devices/{dev_eui}/queue/actilitystyle"
    
    # Заголовки для запроса
    headers = {
        'Authorization': api_key,  # Используем Bearer для авторизации
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    # Тело POST запроса
    data = {
        'confirmDownlink': False,
        'flushDownlinkQueue': flush_downlink_queue,  # выбираем true или false
        'targetPorts': str(random.randint(1, 222)),  # Генерируем случайное число от 1 до 222
        'payloadHex': payload_hex,  # передаем payload
    }
    print("Sending POST request with the following data:")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {data}")
    # Отправляем POST запрос
    response = requests.post(url, headers=headers, json=data)

    print(f"Response Status Code: {response.status_code}")
    print(f"Response Content: {response.text}")
    # Проверка на успешность запроса
    if response.status_code == 200:
        return response.json()  # Возвращаем ответ в случае успешного запроса
    else:
        return {'error': 'Request failed', 'status_code': response.status_code}


def parser(request):
    if request.method == 'POST':
        # Получаем данные из POST-запроса
        dev_eui = request.POST.get('dev_eui')
        hex_value = request.POST.get('payload_hex')
        api_key_id = request.POST.get('api_key_id')  # Новый параметр
        flush_downlink_queue = True  # Статичное значение, либо можете изменить логику
        provider_name = None 

        if api_key_id and api_key_id.isdigit():
            try:
                # Пробуем получить объект APIKey по ID
                provider_name = APIKey.objects.filter(id=api_key_id).values_list('provider_name', flat=True).first()
            except APIKey.DoesNotExist:
                # Если объект не найден, просто оставляем api_key = None
                pass
                
        # Выводим содержимое POST-запроса в консоль
        print("Received POST data:")
        print(f"dev_eui: {dev_eui}")
        print(f"hex_value: {hex_value}")
        print(f"provider_name: {provider_name}")  # Выводим api_key_id
        print(f"flush_downlink_queue: {flush_downlink_queue}")

        if provider_name == "ER-NET":
            send_post_request_ernets(dev_eui, flush_downlink_queue, hex_value) 

        # После обработки данных, редиректим пользователя обратно на ту же страницу
        return redirect('hex_sent')  # Здесь hex_sent — это путь, который будет повторно загружен

    # Если запрос не POST
    return redirect('hex_sent')  # Здесь hex_sent — это путь, который будет повторно загружен
