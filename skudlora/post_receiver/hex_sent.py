from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def my_custom_view(request):
    return HttpResponse("<h1>Добро пожаловать в мою кастомную программу!</h1>")
