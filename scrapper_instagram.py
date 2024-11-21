from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
from selenium_stealth import stealth


chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--incognito")

service = Service('/usr/bin/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)


stealth(driver,
    languages=["en-US", "en"],
    vendor="Google Inc.",
    platform="Win32",
    webgl_vendor="Intel Inc.",
    renderer="Intel Iris OpenGL Engine",
    fix_hairline=True,
)

def scroll_to_bottom(driver):
    """Función para hacer scroll hasta el fondo de la página."""
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(15)

def extract_instagram_posts(driver, extracted_posts):
    """Función para extraer enlaces y descripciones de publicaciones de una cuenta de Instagram."""
    time.sleep(3)
    posts = driver.find_elements(By.XPATH, '//div[contains(@class, "x9f619")]//a')
    new_posts = []

    for post in posts:
        try:
            post_link = post.get_attribute('href')
            img = post.find_element(By.XPATH, './/img')
            img_url = img.get_attribute('src')
            img_alt = img.get_attribute('alt')

            post_data = {
                "link": post_link,
                "image_url": img_url,
                "description": img_alt
            }

            if post_data not in extracted_posts:
                extracted_posts.append(post_data)
                new_posts.append(post_data)

        except Exception as e:
            print("Error al extraer una publicación:", e)
            continue

    return new_posts

def login_to_instagram(driver, username, password):
    """Función para iniciar sesión en Instagram."""
    driver.get('https://www.instagram.com/accounts/login/')
    try:
        print("Esperando que los elementos de inicio de sesión estén disponibles...")
        time.sleep(3)
        username_input = WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        password_input = driver.find_element(By.NAME, 'password')

        username_input.send_keys(username)
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)

        time.sleep(5)
        WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, '//a[@href="/"]'))
        )
        print("Inicio de sesión exitoso")
    except Exception as e:
        print("Ocurrió un error durante el inicio de sesión:")
        print(e)
        driver.save_screenshot('error_login.png')
        driver.quit()
        exit()

# Lista de cuentas de Instagram a extraer
instagram_accounts = [
    "https://www.instagram.com/bavaria_colombia/",
    "https://www.instagram.com/cervezapoker/",
    "https://www.instagram.com/cervezaaguila/",
    "https://www.instagram.com/clubcolombia/"
]

def extract_posts_from_accounts(accounts, extracted_posts):
    """Función para extraer posts de varias cuentas de Instagram."""
    for account in accounts:
        try:
            print(f"Navegando a la página de {account}...")
            driver.get(account)
            time.sleep(10)

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "x9f619")]'))
            )
            print(f"Página {account} cargada correctamente")

            max_scrolls = 80
            scroll_count = 0

            while scroll_count < max_scrolls:
                new_posts = extract_instagram_posts(driver, extracted_posts)
                if new_posts:
                    print(f"Se extrajeron {len(new_posts)} nuevos posts en el scroll {scroll_count + 1}")
                else:
                    print(f"No se encontraron nuevos posts en el scroll {scroll_count + 1}")

                scroll_to_bottom(driver)
                scroll_count += 1

        except Exception as e:
            print(f"Ocurrió un error al intentar acceder a la página {account}:")
            print(e)
            driver.save_screenshot(f'error_{account}.png')


login_to_instagram(driver, 'felixsegura@javeriana.edu.co', 'Felix123')


extracted_posts = []


extract_posts_from_accounts(instagram_accounts, extracted_posts)

with open('posts_instagram.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['link', 'image_url', 'description']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for post in extracted_posts:
        writer.writerow(post)

print("Todos los posts guardados en 'posts_instagram.csv'")

driver.quit()
