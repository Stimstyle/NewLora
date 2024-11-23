document.addEventListener('DOMContentLoaded', function () {
    // Проверка состояния темы из localStorage
    if (localStorage.getItem('dark-mode') === 'true') {
      document.body.classList.add('dark-mode');
      document.getElementById('dark-mode-icon').style.display = 'none'; // Скрыть иконку ночного режима
      document.getElementById('light-mode-icon').style.display = 'inline'; // Показать иконку дневного режима
    }
  
    // Переключение ночного/дневного режима при клике
    document.querySelector('[data-widget="dark-mode"]').addEventListener('click', function (e) {
      e.preventDefault();
  
      // Переключение класса dark-mode на body
      document.body.classList.toggle('dark-mode');
  
      // Переключение видимости иконок
      if (document.body.classList.contains('dark-mode')) {
        document.getElementById('dark-mode-icon').style.display = 'none'; // Скрыть иконку ночного режима
        document.getElementById('light-mode-icon').style.display = 'inline'; // Показать иконку дневного режима
      } else {
        document.getElementById('dark-mode-icon').style.display = 'inline'; // Показать иконку ночного режима
        document.getElementById('light-mode-icon').style.display = 'none'; // Скрыть иконку дневного режима
      }
  
      // Сохраняем состояние в localStorage
      localStorage.setItem('dark-mode', document.body.classList.contains('dark-mode'));
    });
  });
  