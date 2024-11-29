# access_control/views.py

from django.shortcuts import render, redirect
from .forms import DeviceForm, DevicePermissionForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from access_control.models import Device, User, DevicePermission
from django.contrib import messages
from post_receiver.models import DeviceData
from django.contrib.admin.sites import site
from django.core.paginator import Paginator
from django.db.models import Q
from UserDash.models import DeviceGroup
from .models import DeviceGroupPermission


def home(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)  # Вход пользователя
            if user.is_staff:  # Проверяем, является ли пользователь администратором
                return redirect('/admin/')
            else:
                return redirect('user_dashboard')  # Перенаправляем на пользовательскую страницу
        else:
            messages.error(request, 'Неверный логин или пароль.')  # Выводим сообщение об ошибке

    return render(request, 'home.html')


@login_required
def user_dashboard(request):
    return render(request, 'user_dashboard.html')



# Представление для создания устройства
@login_required
def create_device(request):
    if request.method == 'POST':
        device_form = DeviceForm(request.POST)
        permission_form = DevicePermissionForm(request.POST)
        if device_form.is_valid() and permission_form.is_valid():
            # Сохраняем устройство
            device = device_form.save()
            # Сохраняем разрешение
            permission = permission_form.save(commit=False)
            permission.device = device  # Привязываем разрешение к устройству
            permission.save()
            return redirect('device_list')  # Перенаправляем на список устройств
    else:
        device_form = DeviceForm()
        permission_form = DevicePermissionForm()

    return render(request, 'create_device.html', {
        'device_form': device_form,
        'permission_form': permission_form
    })
    
@login_required
def device_list(request):
    devices = Device.objects.all()
    return render(request, 'device_list.html', {'devices': devices})


@login_required
def device_permissions(request):
    search_query = request.GET.get('search', '').strip()
    items_per_page = int(request.GET.get('items_per_page', 25))

    devices = DeviceData.objects.all()
    users = User.objects.all()

    if search_query:
        devices = devices.filter(Q(dev_eui__icontains=search_query) | Q(address__icontains=search_query))

    paginator = Paginator(devices, items_per_page)
    page = request.GET.get('page')
    devices = paginator.get_page(page)

    if request.method == 'POST':
        selected_notifications = request.POST.getlist('selected_notifications')
        user_id = request.POST.get('user_id')

        print("Selected user ID from POST:", user_id)  # Выводим ID пользователя из запроса
        print("Selected notifications:", selected_notifications)  # Выводим ID выбранных уведомлений

        if not user_id:
            messages.error(request, "Пожалуйста, выберите пользователя.")
        if not selected_notifications:
            messages.error(request, "Пожалуйста, выберите хотя бы одно устройство.")

        if user_id and selected_notifications:
            try:
                user = User.objects.get(id=user_id)
                for notification_id in selected_notifications:
                    notification = DeviceData.objects.get(id=notification_id)
                    try:
                        DevicePermission.objects.update_or_create(
                            user=user,
                            device=notification,
                            defaults={'can_manage': True},
                        )
                    except Exception as e:
                        messages.error(request, f"Ошибка при сохранении разрешений для устройства {notification_id}: {str(e)}")
                        return redirect('device_permissions')
                return redirect('device_permissions')
            except User.DoesNotExist:
                messages.error(request, "Пользователь не найден.")
            except DeviceData.DoesNotExist:
                messages.error(request, "Некоторые устройства не найдены.")
            except Exception as e:
                messages.error(request, f"Ошибка: {str(e)}")

    selected_notifications = DevicePermission.objects.filter(user__in=users).values_list('device_id', flat=True)
    available_apps = site.each_context(request).get("available_apps", [])
    return render(request, 'admin/device_permissions.html', {
        'devices': devices,
        'users': users,
        'selected_notifications': selected_notifications,
        'items_per_page': items_per_page,
        'search_query': search_query,
        'paginator': paginator,
        'available_apps': available_apps,
    })


@login_required
def edit_device_permissions(request):
    # Получаем параметры из GET-запроса
    search_query = request.GET.get('search', '').strip()
    items_per_page = int(request.GET.get('items_per_page', 25))
    page_number = request.GET.get('page')
    user_search_query = request.GET.get('user_search', '').strip()

    # Поиск пользователей
    if user_search_query:
        users = User.objects.filter(
            Q(username__icontains=user_search_query) |
            Q(first_name__icontains=user_search_query) |
            Q(last_name__icontains=user_search_query)
        )
    else:
        users = User.objects.all()

    # Получаем выбранного пользователя
    user_id = request.GET.get('user_id') or request.POST.get('user_id')
    selected_user = None
    user_permissions = []

    if user_id:
        try:
            selected_user = User.objects.get(id=user_id)
            user_permissions = DevicePermission.objects.filter(user=selected_user).values_list('device_id', flat=True)
        except User.DoesNotExist:
            messages.error(request, 'Пользователь не найден.')

    # Получаем список устройств с учетом поиска
    devices = DeviceData.objects.all()
    if search_query:
        devices = devices.filter(Q(dev_eui__icontains=search_query) | Q(address__icontains=search_query))

    # Пагинация устройств
    paginator = Paginator(devices, items_per_page)
    devices = paginator.get_page(page_number)

    if request.method == 'POST' and 'save_permissions' in request.POST:
        selected_devices = request.POST.getlist('selected_devices')

        if selected_user:
            # Удаляем все существующие разрешения для этого пользователя
            DevicePermission.objects.filter(user=selected_user).delete()

            # Добавляем новые разрешения
            for device_id in selected_devices:
                try:
                    device = DeviceData.objects.get(id=device_id)
                    DevicePermission.objects.create(user=selected_user, device=device, can_manage=True)
                except DeviceData.DoesNotExist:
                    messages.error(request, f'Устройство с ID {device_id} не найдено.')
            messages.success(request, 'Разрешения успешно обновлены.')
            # Сохраняем параметры поиска при перенаправлении
            return redirect(f'{request.path}?user_id={selected_user.id}&search={search_query}&items_per_page={items_per_page}&page={devices.number}&user_search={user_search_query}')
        else:
            messages.error(request, 'Пожалуйста, выберите пользователя.')

    # Добавляем available_apps в контекст
    available_apps = site.each_context(request).get("available_apps", [])

    context = {
        'users': users,
        'devices': devices,
        'selected_user': selected_user,
        'user_permissions': user_permissions,
        'items_per_page': items_per_page,
        'search_query': search_query,
        'user_search_query': user_search_query,
        'available_apps': available_apps,
    }

    return render(request, 'admin/edit_device_permissions.html', context)

@login_required
def edit_device_group_permissions(request):
    # Получаем параметры из GET-запроса
    search_query = request.GET.get('search', '').strip()
    items_per_page = int(request.GET.get('items_per_page', 25))
    page_number = request.GET.get('page')
    user_search_query = request.GET.get('user_search', '').strip()

    # Поиск пользователей
    if user_search_query:
        users = User.objects.filter(
            Q(username__icontains=user_search_query) |
            Q(first_name__icontains=user_search_query) |
            Q(last_name__icontains=user_search_query)
        )
    else:
        users = User.objects.all()

    # Получаем выбранного пользователя
    user_id = request.GET.get('user_id') or request.POST.get('user_id')
    selected_user = None
    user_group_permissions = []

    if user_id:
        try:
            selected_user = User.objects.get(id=user_id)
            user_group_permissions = DeviceGroupPermission.objects.filter(user=selected_user).values_list('device_group_id', flat=True)
        except User.DoesNotExist:
            messages.error(request, 'Пользователь не найден.')

    # Получаем список групп устройств с учетом поиска
    device_groups = DeviceGroup.objects.all()
    if search_query:
        device_groups = device_groups.filter(
            Q(group_name__icontains=search_query) |
            Q(address__icontains=search_query)
        )
        # Предварительная загрузка связанных устройств
    device_groups = device_groups.prefetch_related('devices')    

    # Пагинация групп устройств
    paginator = Paginator(device_groups, items_per_page)
    device_groups = paginator.get_page(page_number)

    if request.method == 'POST' and 'save_permissions' in request.POST:
        selected_groups = request.POST.getlist('selected_groups')

        if selected_user:
            # Удаляем все существующие разрешения для этого пользователя
            DeviceGroupPermission.objects.filter(user=selected_user).delete()

            # Добавляем новые разрешения
            for group_id in selected_groups:
                try:
                    device_group = DeviceGroup.objects.get(id=group_id)
                    DeviceGroupPermission.objects.create(user=selected_user, device_group=device_group, can_manage=True)
                except DeviceGroup.DoesNotExist:
                    messages.error(request, f'Группа устройств с ID {group_id} не найдена.')
            messages.success(request, 'Разрешения успешно обновлены.')
            # Сохраняем параметры поиска при перенаправлении
            return redirect(f'{request.path}?user_id={selected_user.id}&search={search_query}&items_per_page={items_per_page}&page={device_groups.number}&user_search={user_search_query}')
        else:
            messages.error(request, 'Пожалуйста, выберите пользователя.')

    # Добавляем available_apps в контекст
    available_apps = site.each_context(request).get("available_apps", [])

    context = {
        'users': users,
        'device_groups': device_groups,
        'selected_user': selected_user,
        'user_group_permissions': user_group_permissions,
        'items_per_page': items_per_page,
        'search_query': search_query,
        'user_search_query': user_search_query,
        'available_apps': available_apps,
    }

    return render(request, 'admin/edit_device_group_permissions.html', context)


@login_required
def edit_devices_in_group(request):
    # Получаем параметры из GET-запроса
    search_query = request.GET.get('search', '').strip()
    items_per_page = int(request.GET.get('items_per_page', 25))
    page_number = request.GET.get('page')
    group_search_query = request.GET.get('group_search', '').strip()

    # Поиск групп устройств
    if group_search_query:
        device_groups = DeviceGroup.objects.filter(
            Q(group_name__icontains=group_search_query) |
            Q(address__icontains=group_search_query)
        )
    else:
        device_groups = DeviceGroup.objects.all()

    # Получаем выбранную группу устройств
    group_id = request.GET.get('group_id') or request.POST.get('group_id')
    selected_group = None
    group_devices = []

    if group_id:
        try:
            selected_group = DeviceGroup.objects.get(id=group_id)
            group_devices = selected_group.devices.values_list('id', flat=True)
        except DeviceGroup.DoesNotExist:
            messages.error(request, 'Группа устройств не найдена.')

    # Получаем список устройств с учетом поиска
    devices = DeviceData.objects.all()
    if search_query:
        devices = devices.filter(
            Q(dev_eui__icontains=search_query) |
            Q(address__icontains=search_query)
        )

    # Пагинация устройств
    paginator = Paginator(devices, items_per_page)
    devices = paginator.get_page(page_number)

    if request.method == 'POST' and 'save_devices' in request.POST:
        selected_devices = request.POST.getlist('selected_devices')

        if selected_group:
            # Обновляем устройства в группе
            devices_to_add = DeviceData.objects.filter(id__in=selected_devices)
            selected_group.devices.set(devices_to_add)
            messages.success(request, 'Состав группы успешно обновлен.')
            # Перенаправляем на ту же страницу с сохранением параметров
            return redirect(f'{request.path}?group_id={selected_group.id}&search={search_query}&items_per_page={items_per_page}&page={devices.number}&group_search={group_search_query}')
        else:
            messages.error(request, 'Пожалуйста, выберите группу устройств.')
    # Добавляем available_apps в контекст
    available_apps = site.each_context(request).get("available_apps", [])
    context = {
        'device_groups': device_groups,
        'devices': devices,
        'selected_group': selected_group,
        'group_devices': group_devices,
        'items_per_page': items_per_page,
        'search_query': search_query,
        'group_search_query': group_search_query,
        'available_apps': available_apps,
    }

    return render(request, 'admin/edit_devices_in_group.html', context)