import warnings
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager  # Импорт ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Игнорировать предупреждение OpenSSL
warnings.filterwarnings("ignore", category=UserWarning, module='urllib3')

# Настройки
PAGES_TO_PARSE = 15
BASE_URL = 'https://qna.habr.com/search/users?q=bet88&page='

# Автоматическая установка драйвера
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

user_links = []

try:
    for page in range(1, PAGES_TO_PARSE + 1):
        driver.get(f"{BASE_URL}{page}")

        # Ожидание загрузки списка пользователей
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.content-list.content-list_cards-users"))
        )

        # Поиск всех ссылок на профили
        users = driver.find_elements(By.CSS_SELECTOR, 'h2.card__head-title > a[itemprop="url"]')

        # Сбор ссылок
        for user in users:
            href = user.get_attribute('href')
            if href not in user_links:
                user_links.append(href)

        print(f'Страница {page} обработана')
        time.sleep(1.5)  # Задержка для избежания блокировки

finally:
    driver.quit()

# Сохранение результатов
with open('user_links.txt', 'w') as f:
    f.write('\n'.join(user_links))

print(f'Всего собрано ссылок: {len(user_links)}')