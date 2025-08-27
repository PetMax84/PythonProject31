# lighting_scrapy_csv_fixed_v2

Исправленный проект Scrapy для divan.ru, совместимый с w3lib 2.3.1
(без использования remove_query).

**Как использовать**:
1. Создать и активировать виртуальное окружение:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. Установить зависимости: `pip install -r requirements.txt`
3. Запустить спайдер:
   ```bash
   scrapy runspider spiders/divan_spider.py
   ```
4. Результаты будут в `results.csv`.
