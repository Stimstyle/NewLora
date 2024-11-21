from django.contrib import admin
from post_receiver.models import DeviceData, APIKey


class DeviceDataAdmin(admin.ModelAdmin):
    # Отображать только нужные поля в списке записей
    list_display = ('dev_eui','device_name', 'device_class', 'api_key', 'address', 'description')

    # Указываем, какие поля доступны при добавлении/редактировании
    fields = ('device_name', 'dev_eui', 'device_class', 'api_key', 'address', 'description')

    # Добавляем поиск по именам устройств и dev_eui
    search_fields = ('device_name', 'dev_eui')

    # Добавляем фильтр по классам устройств
    list_filter = ('device_class',)

admin.site.register(DeviceData, DeviceDataAdmin)

class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('provider_name', 'key_name')  # Показывать только необходимые поля
    search_fields = ('provider_name', 'key_name')
admin.site.register(APIKey, APIKeyAdmin)