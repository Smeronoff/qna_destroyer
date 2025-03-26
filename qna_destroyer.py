import json
import os
import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains


# Настройки
COOKIES_FILE = "cookies.json"
USER_LINKS_FILE = "user_links.txt"
LOGIN_URL = "https://qna.habr.com/auth/in"

def human_like_delay():
    """Добавляет случайную задержку для имитации поведения человека."""
    time.sleep(random.uniform(0.5, 2.0))

def save_cookies(driver):
    """Сохраняет куки в файл."""
    with open(COOKIES_FILE, "w") as f:
        json.dump(driver.get_cookies(), f)

def load_cookies(driver):
    """Загружает куки из файла, если они есть."""
    if os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, "r") as f:
            cookies = json.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        return True
    return False

def manual_login(driver):
    """Просит пользователя авторизоваться вручную."""
    driver.get(LOGIN_URL)
    print("Пожалуйста, выполните авторизацию вручную...")
    input("Нажмите Enter после успешной авторизации...")
    save_cookies(driver)

def check_auth(driver):
    """Проверяет, выполнена ли авторизация, по наличию блока профиля."""
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#js-canvas > aside > section.user-panel > div.user-panel_head > div > a"))
        )
        print("✅ Авторизация успешно подтверждена.")
        return True
    except TimeoutException:
        print("❌ Не удалось войти в аккаунт!")
        return False

def delete_user_flow(driver, user_url):
    """Удаляет пользователя по переданной ссылке."""
    try:
        print(f"🔄 Открываю профиль: {user_url}")
        driver.get(user_url)
        human_like_delay()

        # Ожидание кнопки "Меню" (три точки) и клик по ней
        print("🔹 Ожидание кнопки 'Меню'")
        menu_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn_more"))
        )
        driver.execute_script("arguments[0].click();", menu_button)
        human_like_delay()

        # Ожидание загрузки выпадающего меню
        print("🔹 Ожидание загрузки выпадающего меню")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.dropdown__menu"))
        )

        # Клик по кнопке "Настроить" (ссылка в админку)
        print("🔹 Переход в админку")
        options_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'cpanel:user')]"))
        )
        driver.execute_script("arguments[0].click();", options_button)
        human_like_delay()

        # Поиск нужного элемента
        driver.refresh()
        time.sleep(3)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//a[@href='#sanctions']"))
        )
        sanctions_tab = driver.find_elements(By.XPATH, "//a[@href='#sanctions']")
        print(f"Найдено элементов: {len(sanctions_tab)}")

        # Клик по "Санкции"
        print("🔹 Кликаю на 'Санкции'")
        try:
            # Находим ссылку "Санкции"
            driver.execute_script("window.location.hash = '#sanctions';")
            sanctions_tab.click()
            sanctions_tab = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[@href='#sanctions']"))
            )

            actions = ActionChains(driver)
            actions.move_to_element(sanctions_tab).click().perform()  # Наводим и кликаем

        except TimeoutException:
            print("❌ Ошибка: Ссылка 'Санкции' не найдена.")
            print("🔎 HTML страницы:", driver.page_source)
        except Exception as e:
            print(f"❌ Ошибка при клике по санкциям: {str(e)}")

        # Клик по кнопке "Удалить"
        print("🔹 Ожидание кнопки 'Удалить'")
        delete_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "ban_button"))
        )

        # Скроллим к кнопке, чтобы она была видна на экране
        driver.execute_script("arguments[0].scrollIntoView();", delete_button)
        time.sleep(1)  # Даем странице немного времени на подгрузку

        # Кликаем по кнопке
        delete_button.click()
        print("✅ Клик по кнопке 'Удалить пользователя' выполнен.")

        # Подтверждение pop-up
        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print(f"⚠️ Попап: {alert.text}")
            alert.accept()
            print("✅ Pop-up успешно подтвержден.")
        except:
            print("❌ Pop-up не появился!")

        print(f"✅ Пользователь {user_url} успешно удален.")
        return True

    except TimeoutException as e:
        print(f"❌ Timeout при удалении {user_url}: {str(e)}")
        return False
    except NoSuchElementException as e:
        print(f"❌ Элемент не найден при удалении {user_url}: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Неизвестная ошибка при удалении {user_url}: {str(e)}")
        return False

def main():
    """Основная логика скрипта."""
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")

    driver = uc.Chrome(options=options)

    try:
        # Проверка наличия файла со ссылками
        if not os.path.exists(USER_LINKS_FILE):
            print(f"❌ Файл {USER_LINKS_FILE} не найден!")
            exit(1)

        # Загружаем куки
        driver.get("https://qna.habr.com/")
        if not load_cookies(driver):
            print("⚠️ Куки не найдены, выполняется ручная авторизация.")
            manual_login(driver)
        else:
            print("✅ Куки загружены, обновляем страницу.")
            driver.refresh()

        # Проверяем, авторизован ли пользователь
        if not check_auth(driver):
            print("❌ Скрипт завершен из-за ошибки авторизации.")
            exit(1)

        # Читаем ссылки из файла
        with open(USER_LINKS_FILE, "r") as f:
            user_links = [line.strip() for line in f.readlines() if line.strip()]

        print(f"🔹 Загружено {len(user_links)} ссылок:")
        for link in user_links:
            print(link)

        # Обработка пользователей
        for idx, user_url in enumerate(user_links, 1):
            print(f"🔄 Обработка пользователя {idx}/{len(user_links)}: {user_url}")
            delete_user_flow(driver, user_url)
            time.sleep(3)

    except Exception as e:
        print(f"❌ Критическая ошибка: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
