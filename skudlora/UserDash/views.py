from django.shortcuts import render, redirect
from post_receiver.models import DeviceData, APIKey
from UserDash.models import Notification
from datetime import timedelta
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q  # Для фильтрации
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    query = request.GET.get('search', '')  # Получаем значение из строки поиска
    devices = DeviceData.objects.filter(
        Q(address__icontains=query)  # Фильтрация по адресу (регистронезависимо)
    )
    online_count = 0
    offline_count = 0
    current_time = timezone.now()  + timedelta(hours=3)  # Текущее время
    for device in devices:
        # Проверяем, если время устройства прошло больше чем 1 час
        if device.time < current_time - timedelta(hours=1):
            device.status = "Оффлайн"
        else:
            device.status = "Онлайн"  
            online_count += 1  
    total_devices = devices.count()
    offline_count = total_devices - online_count  # Количество оффлайн-устройств

    if request.method == "POST":
        dev_eui = request.POST.get('dev_eui')  # Получаем DevEUI из формы
        current_time = timezone.now()   # Получаем текущее время сервера
        if dev_eui:
            try:
                # Получаем устройство по DevEUI
                device = DeviceData.objects.get(dev_eui=dev_eui)
                
                # Создаем уведомление
                Notification.objects.create(
                    message=f"Открытие двери по адресу {device.address} пользователем {request.user.username}",
                    user=request.user,
                    address=device.address,
                    dev_eui=dev_eui,  # Добавляем DevEUI в уведомление
                    is_read=False,  # Статус уведомления - непрочитано
                    notification_type='system'  # Тип уведомления
                )
                print(f"Уведомление создано для устройства {device.device_name}")
            except DeviceData.DoesNotExist:
                print(f"Устройство с DevEUI {dev_eui} не найдено")
    for device in devices:
        print(f"Время устройства {device.device_name}: {device.time}, Статус: {device.status}")
    paginator = Paginator(devices, 10)  # 1 устройство на странице
    page_number = request.GET.get('page', 1)  # Получаем номер страницы из параметра запроса
    page_devices = paginator.get_page(page_number)  # Извлекаем устройства для текущей страницы

    return render(request, 'index.html', {
        'devices': page_devices,
        'search_query': query,
        'total_devices': total_devices,  # Общее количество устройств
        'online_count': online_count,  # Количество онлайн-устройств
        'offline_count': offline_count  # Количество оффлайн-устройств
    })

@login_required
def devices(request):
    # Логика поиска (если нужно)
    query = request.GET.get('search', '')
    devices = DeviceData.objects.all()

    if query:
        devices = devices.filter(
            Q(address__icontains=query) |  # Поиск по адресу
            Q(dev_eui__icontains=query) |  # Поиск по DevEUI
            Q(description__icontains=query)  # Поиск по описанию
        )

        # Обработка добавления устройства
    if request.method == 'POST':
        device_name = request.POST.get('device_name')
        dev_eui = request.POST.get('dev_eui')
        device_class = request.POST.get('device_class')
        api_key_id = request.POST.get('api_key')
        address = request.POST.get('address')
        description = request.POST.get('description')

        api_key = APIKey.objects.get(id=api_key_id) if api_key_id else None

        # Создание и сохранение нового устройства
        DeviceData.objects.create(
            device_name=device_name,
            dev_eui=dev_eui,
            device_class=device_class,
            api_key=api_key,
            address=address,
            description=description
        )
        return redirect('devices')

    current_time = timezone.now() + timedelta(hours=3)
    for device in devices:
        if device.time < current_time - timedelta(hours=1):
            device.status = "Оффлайн"
        else:
            device.status = "Онлайн"

        if device.rssi is not None:
            if device.rssi <= -120:
                device.bar_width = 10
            elif device.rssi <= -105:
                device.bar_width = round(((device.rssi + 120) / 15 * 20) + 10)
            elif device.rssi <= -90:
                device.bar_width = round(((device.rssi + 105) / 15 * 20) + 30)
            elif device.rssi <= -75:
                device.bar_width = round(((device.rssi + 90) / 15 * 30) + 50)
            else:
                device.bar_width = 100  # Уровень по умолчанию для rssi > -75
        else:
            device.bar_width = 0  # Если rssi == None, ставим 0
            
        if device.lo_ra_snr is not None:
            if device.lo_ra_snr <= -10:
                device.snr_bar_width = 10
            elif device.lo_ra_snr <= 0:
                device.snr_bar_width = round(((device.lo_ra_snr + 10) / 10) * 30) + 10
            elif device.lo_ra_snr <= 5:
                device.snr_bar_width = round(((device.lo_ra_snr) / 5) * 40) + 40
            elif device.lo_ra_snr <= 10:
                device.snr_bar_width = round(((device.lo_ra_snr - 5) / 5) * 20) + 80
            else:
                device.snr_bar_width = 100  # Отличный сигнал
        else:
            device.snr_bar_width = 0  # Если SNR == None, ставим 0
        if device.battery_level is not None:
            device.battery_bar_width = round(device.battery_level)  # Преобразуем уровень батареи напрямую в ширину
        else:
            device.battery_bar_width = 0  # Если battery_level == None, ставим 0
        print(f"bar_SNR: {device.battery_bar_width}")    

    paginator = Paginator(devices, 50)  # 10 устройств на странице
    page_number = request.GET.get('page', 1)
    page_devices = paginator.get_page(page_number)

    api_keys = APIKey.objects.all()  # Получаем все доступные API ключи
    return render(request, 'devices.html', {
        'devices': page_devices, 
        'search_query': query, 
        'api_keys': api_keys,  # Для отображения API ключей в форме
    })



from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from datetime import timedelta
from django.utils import timezone

from datetime import timedelta
from django.utils import timezone

@login_required
def notification(request):
    # Получаем все уведомления, отсортированные по времени
    notifications = Notification.objects.all().order_by('-timestamp')

    notification_type = None  # Инициализируем переменную для типа уведомлений
    
    # Получаем значение для items_per_page, если оно задано, или 25 по умолчанию
    items_per_page = request.POST.get('items_per_page', request.session.get('items_per_page', 25))
    
    # Проверяем, что items_per_page - это число, если нет, используем 25
    try:
        items_per_page = int(items_per_page)
    except ValueError:
        items_per_page = 25

    # Если значение items_per_page было отправлено, сохраняем его в сессии для будущих запросов
    request.session['items_per_page'] = items_per_page

    # Инициализация фильтра по времени
    time_range = request.POST.get('time_range', 'all')  # Значение по умолчанию - "всё время"

    # Фильтрация уведомлений по времени
    current_time = timezone.now()
    if time_range == 'day':
        notifications = notifications.filter(timestamp__gte=current_time - timedelta(days=1))
    elif time_range == 'week':
        notifications = notifications.filter(timestamp__gte=current_time - timedelta(weeks=1))
    elif time_range == 'month':
        notifications = notifications.filter(timestamp__gte=current_time - timedelta(days=30))
    elif time_range == 'year':
        notifications = notifications.filter(timestamp__gte=current_time - timedelta(days=365))

    # Обработка действий пользователя через POST-запрос
    if request.method == "POST":
        notification_type = request.POST.get('notification_type', None)
        if notification_type:
            notifications = notifications.filter(notification_type=notification_type)

        selected_notifications = request.POST.getlist('selected_notifications')
        if 'select_all' in request.POST:
            if request.POST['select_all'] == 'true':
                # Выбрать все уведомления
                selected_notifications = [notification.id for notification in notifications]
            elif request.POST['select_all'] == 'false':
                # Отменить все уведомления
                selected_notifications = []
        
        if 'delete_selected' in request.POST:
            # Удаляем выбранные уведомления
            Notification.objects.filter(id__in=selected_notifications).delete()
            return redirect('notification')
        if 'mark_as_read' in request.POST:
            # Отмечаем выбранные уведомления как прочитанные
            Notification.objects.filter(id__in=selected_notifications).update(is_read=True)
        if 'notification_id' in request.POST:
            notification_id = request.POST.get('notification_id')
            notification = Notification.objects.get(id=notification_id)
            notification.is_read = True
            notification.save()

        # Сохраняем список выбранных уведомлений в сессии
        request.session['selected_notifications'] = selected_notifications

    paginator = Paginator(notifications, items_per_page)
    page_number = request.GET.get('page')  # Номер текущей страницы
    page_obj = paginator.get_page(page_number)

    selected_notifications = request.session.get('selected_notifications', [])
    return render(request, 'notification.html', {
        'notifications': page_obj,
        'selected_notifications': selected_notifications,
        'notification_type': notification_type,
        'items_per_page': items_per_page,
        'time_range': time_range,  # Передаём выбранное значение времени в шаблон
        'page_range': page_obj.paginator.page_range,
    })

@login_required
def groups(request):
    # Получаем все устройства
    devices = DeviceData.objects.all()
    return render(request, 'groups.html', {'devices': devices})