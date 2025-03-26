import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Креды для Хабра
ACCOUNT_USERNAME = "name@gmail.com"
ACCOUNT_PASSWORD = "password"

# URL для авторизации на Хабре
LOGIN_URL = "https://habr.com/kek/v1/auth/habrahabr/?back=/ru/feed/&hl=ru"

USER_MANAGE_URLS = [
   "https://habr.com/ru/cp2/user/RsT11/",

    # Тут мог быть ваш урл
]


def deactivate_user(driver, url, note):
    """Деактивирует пользователя по заданному URL и добавляет заметку."""
    try:
        driver.get(url)  # Переход на страницу управления пользователем

        # Ожидаем загрузки формы управления пользователем
        print(f"Ожидание загрузки формы для URL: {url}")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "user_form")))

        # Деактивация аккаунта: снимаем галочку с чекбокса "Аккаунт активирован"
        checkbox = driver.find_element(By.NAME, "active")
        if checkbox.is_selected():
            checkbox.click()

        # Проверяем доступность поля для заметки и добавляем текст
        note_area = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "admin-note")))
        driver.execute_script("arguments[0].style.display = 'block';", note_area)  # Разблокируем, если скрыто
        note_area.clear()  # Очищаем поле заметки перед вводом
        note_area.send_keys(note)

        # Сохраняем изменения
        save_button = driver.find_element(By.ID, "save")
        save_button.click()

        # Ожидаем, пока изменения сохранятся
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Изменения сохранены')]")))

        print(f"Аккаунт на URL {url} деактивирован и добавлена заметка: '{note}'")
    except Exception as e:
        print(f"Ошибка при обработке URL {url}: {e}")


def login_and_deactivate_users(note="спам в песочницу"):
    """Авторизация и деактивация пользователей по списку URL."""
    # Настройки Chrome для обхода Selenium-детекторов
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Инициализация браузера
    driver = uc.Chrome(options=options)

    try:
        driver.get(LOGIN_URL)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(ACCOUNT_USERNAME)
        driver.find_element(By.NAME, "password").send_keys(ACCOUNT_PASSWORD)

        # Проходим капчу вручную
        input("Пройдите капчу и нажмите Enter, когда будете готовы перейти к управлению пользователями...")

        # Обработка каждой страницы управления пользователями
        for url in USER_MANAGE_URLS:
            deactivate_user(driver, url, note)  # Обработка текущего пользователя

            # Подождем немного перед переходом к следующему пользователю
            time.sleep(2)

    finally:
        time.sleep(5)  # Ожидание перед закрытием браузера
        driver.quit()


# Запуск скрипта
if __name__ == "__main__":
    login_and_deactivate_users()