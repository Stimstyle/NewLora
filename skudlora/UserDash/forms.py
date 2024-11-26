from django import forms
from post_receiver.models import DeviceData

class DeviceDataForm(forms.ModelForm):
    class Meta:
        model = DeviceData
        fields = ['device_name', 'dev_eui', 'device_class', 'api_key', 'address', 'description']
        widgets = {
            'device_name': forms.PasswordInput(attrs={'placeholder': 'Введите пароль'}),
            'dev_eui': forms.TextInput(attrs={'placeholder': 'Введите DevEUI'}),
            'device_class': forms.Select(),
            'api_key': forms.Select(),
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Введите адрес установки'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Введите описание'}),
        }
