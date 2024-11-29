from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    """
    Добавляет класс к элементу формы.
    Пример использования:
    {{ form.field|add_class:"my-class" }}
    """
    return value.as_widget(attrs={'class': arg})
