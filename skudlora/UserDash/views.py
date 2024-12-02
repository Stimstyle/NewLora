from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta
from django.db.models import Q, Case, When, Value, CharField, Avg, Min, Max
from django.http import HttpResponse
from post_receiver.models import DeviceData, APIKey
from UserDash.models import Notification, DeviceGroup, EventNotification
from access_control.models import DevicePermission, DeviceGroupPermission
from django.contrib import messages
from urllib.parse import urlencode
import openpyxl
from openpyxl.utils import get_column_letter
import folium


@login_required
def index(request):
    query = request.GET.get('search', '')  # Получаем значение из строки поиска

    if request.user.is_superuser:
        # Суперпользователь видит все устройства
        devices = DeviceData.objects.all()
    else:
        # Обычный пользователь видит только устройства, к которым у него есть доступ
        # Получаем устройства, к которым у пользователя есть прямые разрешения
        user_devices = DeviceData.objects.filter(devicepermission__user=request.user)

        # Получаем группы устройств, к которым у пользователя есть разрешения
        device_groups_with_permission = DeviceGroup.objects.filter(devicegrouppermission__user=request.user)

        # Получаем устройства из этих групп
        devices_in_groups = DeviceData.objects.filter(device_groups__in=device_groups_with_permission)

        # Объединяем устройства из прямых разрешений и из групповых разрешений
        devices = (user_devices | devices_in_groups).distinct()

    # Применяем фильтр по адресу
    devices = devices.filter(address__icontains=query)

    online_count = 0
    offline_count = 0
    current_time = timezone.now()  # Текущее время

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
        if dev_eui:
            try:
                # Получаем устройство по DevEUI
                device = DeviceData.objects.get(dev_eui=dev_eui)
                
                # Проверяем, есть ли у пользователя доступ к этому устройству
                if request.user.is_superuser or \
                   DevicePermission.objects.filter(user=request.user, device=device).exists() or \
                   DeviceGroupPermission.objects.filter(user=request.user, device_group__devices=device).exists():
                    
                    # Создаем уведомление
                    Notification.objects.create(
                        message=f"Открытие двери по адресу {device.address} пользователем {request.user.username}",
                        user=request.user,
                        address=device.address,
                        dev_eui=dev_eui,  # Добавляем DevEUI в уведомление
                        is_read=False,  # Статус уведомления - непрочитано
                        notification_type='system'  # Тип уведомления
                    )
                else:
                    # Пользователь не имеет доступа к этому устройству
                    pass  # Можно вернуть сообщение об ошибке или игнорировать
            except DeviceData.DoesNotExist:
                pass

    paginator = Paginator(devices, 8)  # 10 устройств на странице
    page_number = request.GET.get('page', 1)  # Получаем номер страницы из параметра запроса
    page_devices = paginator.get_page(page_number)  # Извлекаем устройства для текущей страницы


    # Фильтруем устройства с валидными координатами
    devices_with_coords = devices.exclude(latitude__isnull=True).exclude(longitude__isnull=True)

    if devices_with_coords.exists():
        avg_lat = devices_with_coords.aggregate(Avg('latitude'))['latitude__avg']
        avg_lon = devices_with_coords.aggregate(Avg('longitude'))['longitude__avg']

        min_lat = devices_with_coords.aggregate(min_lat=Min('latitude'))['min_lat']
        max_lat = devices_with_coords.aggregate(max_lat=Max('latitude'))['max_lat']
        min_lon = devices_with_coords.aggregate(min_lon=Min('longitude'))['min_lon']
        max_lon = devices_with_coords.aggregate(max_lon=Max('longitude'))['max_lon']
    else:
        # Устанавливаем стандартные координаты, если устройств нет
        avg_lat, avg_lon = 0, 0
        min_lat, max_lat, min_lon, max_lon = -10, 10, -10, 10  # Примерные границы

    # Создание карты с помощью Folium
    folium_map = folium.Map(
        location=[avg_lat, avg_lon],
        zoom_start=12,
        attributionControl=False  # Отключаем стандартную атрибуцию
    )

    # Добавляем собственный TileLayer с кастомной атрибуцией
    folium.TileLayer(
        tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attr='© OpenStreetMap contributors | Ваш текст здесь',
        name='OpenStreetMap',
        control=False
    ).add_to(folium_map)

    # Добавление маркеров на карту
    for device in devices:
        if device.latitude and device.longitude:
            folium.Marker(
                location=[device.latitude, device.longitude],
                popup=f"{device.address} - {device.status}",
                icon=folium.Icon(color='green' if device.status == 'Онлайн' else 'red')
            ).add_to(folium_map)

    # Если есть устройства с координатами, устанавливаем границы карты
    if devices_with_coords.exists():
        folium_map.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

    # Преобразование карты в HTML
    map_html = folium_map._repr_html_()



    return render(request, 'index.html', {
        'devices': page_devices,
        'search_query': query,
        'total_devices': total_devices,  # Общее количество устройств
        'online_count': online_count,  # Количество онлайн-устройств
        'offline_count': offline_count,  # Количество оффлайн-устройств
        'map_html': map_html
    })



@login_required
def devices(request):
    query = request.GET.get('search', '')

    if request.user.is_superuser:
        # Суперпользователь видит все устройства
        devices = DeviceData.objects.all()
    else:
        # Обычный пользователь видит только устройства, к которым у него есть доступ
        # Получаем устройства, к которым у пользователя есть прямые разрешения
        user_devices = DeviceData.objects.filter(devicepermission__user=request.user)

        # Получаем группы устройств, к которым у пользователя есть разрешения
        device_groups_with_permission = DeviceGroup.objects.filter(devicegrouppermission__user=request.user)

        # Получаем устройства из этих групп
        devices_in_groups = DeviceData.objects.filter(device_groups__in=device_groups_with_permission)

        # Объединяем устройства из прямых разрешений и из групповых разрешений
        devices = (user_devices | devices_in_groups).distinct()

    # Применяем фильтр поиска, если он задан
    if query:
        devices = devices.filter(
            Q(address__icontains=query) |
            Q(dev_eui__icontains=query) |
            Q(description__icontains=query)
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
        new_device = DeviceData.objects.create(
            device_name=device_name,
            dev_eui=dev_eui,
            device_class=device_class,
            api_key=api_key,
            address=address,
            description=description
        )

        # Назначаем разрешение пользователю на новое устройство
        DevicePermission.objects.create(
            user=request.user,
            device=new_device,
            can_manage=True  # Установите в зависимости от ваших требований
        )

        return redirect('devices')

    current_time = timezone.now() + timedelta(hours=3)
    for device in devices:
        if device.time < current_time - timedelta(hours=1):
            device.status = "Оффлайн"
        else:
            device.status = "Онлайн"

        # Расчет уровней сигнала и батареи
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

    paginator = Paginator(devices, 50)  # 50 устройств на странице
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

    # Обработка действий пользователя через POST-запрос
    if request.method == "POST":
        notification_type = request.POST.get('notification_type', None)

        selected_notifications = request.POST.getlist('selected_notifications')

        if 'select_all' in request.POST:
            if request.POST['select_all'] == 'true':
                # Выбрать все уведомления после фильтрации
                selected_notifications = [str(notification.id) for notification in notifications]
            elif request.POST['select_all'] == 'false':
                # Отменить выбор всех уведомлений
                selected_notifications = []

        if 'delete_selected' in request.POST:
            # Удаляем выбранные уведомления
            if request.user.is_superuser:
                # Суперпользователь может удалять любые уведомления
                Notification.objects.filter(id__in=selected_notifications).delete()
            else:
                # Обычный пользователь может удалять только свои уведомления
                Notification.objects.filter(id__in=selected_notifications, user=request.user).delete()
            return redirect('notification')

        if 'mark_as_read' in request.POST:
            # Отмечаем выбранные уведомления как прочитанные
            if request.user.is_superuser:
                Notification.objects.filter(id__in=selected_notifications).update(is_read=True)
            else:
                Notification.objects.filter(id__in=selected_notifications, user=request.user).update(is_read=True)

        if 'notification_id' in request.POST:
            notification_id = request.POST.get('notification_id')
            try:
                if request.user.is_superuser:
                    notification = Notification.objects.get(id=notification_id)
                else:
                    notification = Notification.objects.get(id=notification_id, user=request.user)
                notification.is_read = True
                notification.save()
            except Notification.DoesNotExist:
                pass  # Уведомление не найдено или нет доступа

        # Сохраняем список выбранных уведомлений в сессии
        request.session['selected_notifications'] = selected_notifications

    # Теперь формируем queryset уведомлений в зависимости от того, является ли пользователь суперпользователем
    if request.user.is_superuser:
        # Суперпользователь видит все уведомления
        notifications = Notification.objects.all()
    else:
        # Обычный пользователь видит только свои уведомления
        notifications = Notification.objects.filter(user=request.user)

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

    # Фильтрация по типу уведомления
    notification_type = request.POST.get('notification_type', None)
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)

    # Сортируем уведомления по времени
    notifications = notifications.order_by('-timestamp')

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

def is_staff_or_superuser(user):
    return user.is_staff or user.is_superuser
def is_admin_or_arendator(user):
    return user.is_superuser or user.is_staff or user.groups.filter(name='Arendators').exists()



@user_passes_test(is_staff_or_superuser, login_url='access_denied')
def groups(request):
    if request.method == "POST":
        # Получаем данные из формы
        group_name = request.POST.get("group_name")
        address = request.POST.get("address")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        device_ids = request.POST.getlist("devices")  # Получаем список выбранных устройств

        print("POST данные:", request.POST)  # Для отладки

        # Проверяем корректность и обязательные поля
        if group_name and address:
            try:
                latitude = float(latitude) if latitude else None
                longitude = float(longitude) if longitude else None

                # Создаём новую группу
                group = DeviceGroup.objects.create(
                    group_name=group_name,
                    address=address,
                    latitude=latitude,
                    longitude=longitude
                )
                print(f"Группа создана: {group}")  # Отладка

                # Добавляем устройства в группу
                if device_ids:
                    devices = DeviceData.objects.filter(id__in=device_ids)  # Получаем устройства по ID
                    group.devices.set(devices)  # Устанавливаем устройства для группы
                    print(f"Устройства добавлены: {device_ids}")  # Отладка

                return redirect('groups')  # Перенаправление на страницу групп
            except ValueError as e:
                print(f"Ошибка при конвертации: {e}")
                return render(request, 'groups.html', {
                    'devices': DeviceData.objects.all(),
                    'error': "Некорректное значение для широты или долготы."
                })
            except Exception as e:
                print(f"Общая ошибка: {e}")
                return render(request, 'groups.html', {
                    'devices': DeviceData.objects.all(),
                    'error': f"Ошибка при сохранении данных: {e}"
                })

    # При GET-запросе просто показываем страницу с устройствами
    devices = DeviceData.objects.all()
    return render(request, 'groups.html', {'devices': devices})

@login_required
@user_passes_test(is_admin_or_arendator)
def event(request):
    if request.method == 'POST' and 'delete_selected' in request.POST:
        delete_ids = request.POST.getlist('delete_ids')
        if delete_ids:
            EventNotification.objects.filter(id__in=delete_ids).delete()
            messages.success(request, "Выбранные уведомления успешно удалены.")
        else:
            messages.warning(request, "Не выбрано ни одного уведомления для удаления.")
        return redirect('event')

    # Фильтрация уведомлений
    dev_eui = request.GET.get('dev_eui', '').strip()
    address = request.GET.get('address', '').strip()
    user_filter = request.GET.get('user', '').strip()
    notification_type = request.GET.get('notification_type', '').strip()
    start_date = request.GET.get('start_date', '').strip()
    start_time = request.GET.get('start_time', '').strip()
    end_date = request.GET.get('end_date', '').strip()
    end_time = request.GET.get('end_time', '').strip()
    items_per_page = request.GET.get('items_per_page', 25)
    page = request.GET.get('page')

    export_excel = request.GET.get('export_excel', 'false').lower() == 'true'

    notifications = EventNotification.objects.all()

    if dev_eui:
        notifications = notifications.filter(dev_eui__icontains=dev_eui)
    if address:
        notifications = notifications.filter(address__icontains=address)
    if is_admin_or_arendator(request.user) and user_filter:
        notifications = notifications.filter(user__username__icontains=user_filter)
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            if start_time:
                start_datetime_str = f"{start_date} {start_time}"
                start_datetime_obj = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M')
                notifications = notifications.filter(timestamp__gte=start_datetime_obj)
            else:
                notifications = notifications.filter(timestamp__gte=start_date_obj)
        except ValueError:
            messages.error(request, "Некорректный формат начальной даты или времени.")
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            if end_time:
                end_datetime_str = f"{end_date} {end_time}"
                end_datetime_obj = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M')
                notifications = notifications.filter(timestamp__lte=end_datetime_obj)
            else:
                notifications = notifications.filter(timestamp__lte=end_date_obj)
        except ValueError:
            messages.error(request, "Некорректный формат конечной даты или времени.")

    notifications = notifications.order_by('-timestamp')

    if export_excel:
        # Генерация Excel-файла
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Уведомления"

        # Заголовки столбцов
        headers = ['DevEUI', 'Адрес']
        if is_admin_or_arendator(request.user):
            headers.append('Пользователь')
        headers.extend(['Тип уведомления', 'Время'])

        ws.append(headers)

        # Добавление данных
        for notification in notifications:
            row = [
                notification.dev_eui,
                notification.address,
            ]
            if is_admin_or_arendator(request.user):
                row.append(notification.user.username)
            row.extend([
                notification.get_notification_type_display(),
                notification.timestamp.strftime('%Y-%m-%d %H:%M'),
            ])
            ws.append(row)

        # Автоматическая настройка ширины столбцов
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column_letter].width = adjusted_width

        # Подготовка HTTP-ответа
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=notifications.xlsx'
        wb.save(response)
        return response

    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(notifications, items_per_page)

    try:
        notifications_page = paginator.page(page)
    except PageNotAnInteger:
        notifications_page = paginator.page(1)
    except EmptyPage:
        notifications_page = paginator.page(paginator.num_pages)

    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']
    get_params = get_params.urlencode()

    current_page = notifications_page.number
    total_pages = paginator.num_pages
    start_index = max(current_page - 2, 1)
    end_index = min(current_page + 2, total_pages)
    page_range = range(start_index, end_index + 1)

    context = {
        'notifications': notifications_page,
        'dev_eui': dev_eui,
        'address': address,
        'user_filter': user_filter,
        'notification_type': notification_type,
        'start_date': start_date,
        'start_time': start_time,
        'end_date': end_date,
        'end_time': end_time,
        'items_per_page': int(items_per_page),
        'is_admin': is_admin_or_arendator(request.user),
        'get_params': get_params,
        'page_range': page_range,
    }

    return render(request, 'event.html', context)