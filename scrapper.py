from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

# Configuración del navegador Chrome
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--incognito")

service = Service('/usr/bin/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)

# Función para realizar scroll suave
def scroll_and_extract(driver, extracted_tweets, step=300, delay=0.5, max_scroll=3000):
    """
    Realiza un scroll suave en pequeños incrementos, extrayendo tweets después de cada paso.
    step: Cantidad de píxeles por cada desplazamiento.
    delay: Tiempo de espera entre cada desplazamiento (en segundos).
    max_scroll: Número máximo de píxeles que se desplazará en total.
    """
    current_scroll_position = 0
    end_scroll_position = driver.execute_script("return document.body.scrollHeight")
    
    while current_scroll_position < end_scroll_position and current_scroll_position < max_scroll:
        driver.execute_script(f"window.scrollBy(0, {step});")
        current_scroll_position += step
        time.sleep(delay)
        # Intentar extraer tweets después de cada desplazamiento
        extract_tweets(driver, extracted_tweets)

# Función para extraer los tweets
def extract_tweets(driver, extracted_tweets):
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//article[@role="article"]'))
        )
        tweets = driver.find_elements(By.XPATH, '//article[@role="article"]')
        new_tweets = []

        for tweet in tweets:
            try:
                # Extraer el nombre de la cuenta
                account_name = tweet.find_element(By.XPATH, './/span[contains(text(), "@")]').text
            except Exception:
                account_name = "No account name"

            try:
                # Extraer la fecha del tweet
                date = tweet.find_element(By.XPATH, './/time').get_attribute('datetime')
            except Exception:
                date = "No date"

            try:
                # Extraer el enlace del tweet
                tweet_link = tweet.find_element(By.XPATH, './/time/parent::a').get_attribute('href')
            except Exception:
                tweet_link = "No link"

            try:
                # Extraer el contenido del tweet
                tweet_content = tweet.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
            except Exception:
                tweet_content = "No content"

            tweet_data = {
                "account_name": account_name,
                "date": date,
                "link": tweet_link,
                "content": tweet_content
            }

            if tweet_data not in extracted_tweets:  # Evitar agregar tweets duplicados
                extracted_tweets.append(tweet_data)
                new_tweets.append(tweet_data)

        return new_tweets

    except Exception as e:
        print(f"Error al extraer tweets: {e}")
        return None

# Función para iniciar sesión en Twitter
def login_to_twitter(driver, username, password):
    driver.get('https://twitter.com/i/flow/login')
    try:
        print("Esperando que los elementos de inicio de sesión estén disponibles...")
        time.sleep(3)
        username_input = WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.NAME, 'text'))
        )
        username_input.send_keys(username)

        time.sleep(2)
        siguiente_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//span[text()="Next"]'))
        )
        siguiente_btn.click()

        time.sleep(3)
        password_input = WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.NAME, 'password'))
        )
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)

        time.sleep(5)
        WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, '//a[@href="/home"]'))
        )
        print("Inicio de sesión exitoso")
    except Exception as e:
        print("Ocurrió un error durante el inicio de sesión:")
        print(e)
        driver.save_screenshot('error_login.png')
        driver.quit()
        exit()

# Función para extraer tweets desde las cuentas
def extract_tweets_from_accounts(accounts, extracted_tweets):
    for account in accounts:
        try:
            print(f"Navegando a la página de {account}...")
            driver.get(account)

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//article[@role="article"]'))
            )
            print(f"Página {account} cargada correctamente")

            max_scrolls = 10
            scroll_count = 0

            while scroll_count < max_scrolls:
                # Hacer scroll suave y extraer tweets después de cada desplazamiento
                scroll_and_extract(driver, extracted_tweets)
                scroll_count += 1

        except Exception as e:
            print(f"Ocurrió un error al intentar acceder a la página {account}:")
            print(e)
            driver.save_screenshot(f'error_{account}.png')

# Inicio de sesión
login_to_twitter(driver, 'felix_jss@hotmail.com', 'felix1.2')

# Lista de cuentas de Twitter para extraer tweets
twitter_accounts = [
    # "https://x.com/CervezaAguila",
    "https://x.com/CervezaPoker"
    # "https://x.com/Club_Colombia",
    # "https://x.com/BAVARIA_OFICIAL"
]
extracted_tweets = []
extract_tweets_from_accounts(twitter_accounts, extracted_tweets)

# Guardar los tweets en un archivo CSV
with open('tweets_2.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['account_name', 'date', 'link', 'content']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for tweet in extracted_tweets:
        writer.writerow(tweet)

print("Todos los tweets guardados en 'tweets.csv'")

driver.quit()
