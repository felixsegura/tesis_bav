from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from bs4 import BeautifulSoup

# Configuración del navegador y opciones
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--incognito")

# Iniciar el driver de Chrome
service = Service('/usr/bin/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)

# Función para hacer scroll hasta el final de la página
def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Espera 2 segundos para que carguen los nuevos tweets

# Navegar a la página de inicio de sesión de Twitter
driver.get('https://twitter.com/i/flow/login')

# Esperar hasta que los campos de inicio de sesión estén disponibles
try:
    print("Esperando que los elementos de inicio de sesión estén disponibles...")
    username = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.NAME, 'text'))
    )
    username.send_keys('felix_jss@hotmail.com')
    time.sleep(10)
    siguiente_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//span[text()="Next"]'))
    )
    siguiente_btn.click()

    password = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.NAME, 'password'))
    )
    password.send_keys('felix1.2')
    password.send_keys(Keys.RETURN)

    # Esperar a que se complete la autenticación
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//a[@href="/home"]'))
    )
    print("Inicio de sesión exitoso")

except Exception as e:
    print("Ocurrió un error durante el inicio de sesión:")
    print(e)
    driver.save_screenshot('error_login.png')
    driver.quit()
    exit()

# Extraer cookies de Selenium y transferirlas a requests
cookies = driver.get_cookies()
session = requests.Session()

for cookie in cookies:
    session.cookies.set(cookie['name'], cookie['value'])

# Ahora puedes usar requests con las cookies autenticadas
try:
    url = 'https://twitter.com/BAVARIA_OFICIAL'
    response = session.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        tweets = soup.find_all('article', {'role': 'article'})

        # Guardar los tweets en un archivo de texto
        with open('tweets_bavaria_with_responses.txt', 'w', encoding='utf-8') as f:
            for tweet in tweets:
                account_name = tweet.find('span', text=lambda x: x and '@' in x).text if tweet.find('span', text=lambda x: x and '@' in x) else "No cuenta"
                content = tweet.find('div', {'lang': True}).text if tweet.find('div', {'lang': True}) else "No contenido"
                date = tweet.find('time')['datetime'] if tweet.find('time') else "No fecha"
                f.write(f"Account: {account_name}\n")
                f.write(f"Tweet: {date}: {content}\n")
                print(f"Account: {account_name}")
                print(f"Tweet: {date}: {content}")
                f.write("\n")
        print("Tweets guardados en 'tweets_bavaria_with_responses.txt'")
    else:
        print(f"No se pudo acceder a la página. Estado: {response.status_code}")

except Exception as e:
    print("Ocurrió un error al intentar acceder a la página de Bavaria Oficial:")
    print(e)
    driver.save_screenshot('error_bavaria.png')

# Cerrar el navegador
driver.quit()
