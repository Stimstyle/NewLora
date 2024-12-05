from django.contrib import admin
from post_receiver.models import DeviceData, APIKey
from UserDash.models import DeviceGroup
from .models import DistrictGroup
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from .forms import DistrictGroupForm


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

class DeviceGroupForm(forms.ModelForm):
    devices = forms.ModelMultipleChoiceField(
        queryset=DeviceData.objects.all(),
        required=False,
        widget=FilteredSelectMultiple("Устройства", is_stacked=False)
    )

    class Meta:
        model = DeviceGroup
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DeviceGroupForm, self).__init__(*args, **kwargs)
        self.fields['devices'].help_text = "Выберите устройства, которые должны входить в эту группу."

@admin.register(DeviceGroup)
class DeviceGroupAdmin(admin.ModelAdmin):
    form = DeviceGroupForm
    list_display = ('group_name', 'address', 'latitude', 'longitude')
    search_fields = ('group_name', 'address')
    filter_horizontal = ('devices',)  # Для отображения многострочного выбора устройств

    # Указываем кастомный шаблон
    change_form_template = "admin/change_form.html"  # Путь: access_control/templates/admin/change_form.html
    add_form_template = "admin/change_form.html"

class DistrictGroupAdmin(admin.ModelAdmin):
    form = DistrictGroupForm  # Используем кастомную форму
    list_display = ('district_name', 'group_count')
    search_fields = ('district_name',)
    change_form_template = 'admin/change_form_dist.html'

    def group_count(self, obj):
        return obj.groups.count()
    group_count.short_description = "Кол-во групп"

admin.site.register(DistrictGroup, DistrictGroupAdmin)