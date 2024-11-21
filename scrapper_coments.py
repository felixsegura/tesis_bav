from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--incognito")

service = Service('/usr/bin/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)

def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

def extract_comments_from_tweet(driver):
    try:
        comments_section = driver.find_elements(By.XPATH, '//article[@role="article"]')
        comments = []

        for comment in comments_section:
            try:
                # Extraer el autor del comentario
                comment_author = comment.find_element(By.XPATH, './/span[contains(text(), "@")]').text
                
                # Extraer el texto del comentario
                comment_text = comment.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
                
                # Extraer la fecha del comentario
                comment_date = comment.find_element(By.XPATH, './/time').get_attribute('datetime')

                comments.append({
                    "author": comment_author,
                    "comment": comment_text,
                    "date": comment_date
                })

            except Exception as e:
                print(f"Error al extraer un comentario: {e}")
                continue

        return comments

    except Exception as e:
        print(f"Error al intentar extraer los comentarios: {e}")
        return []

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

def extract_comments_from_links(csv_file, output_file):
    with open(csv_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        links = [row['link'] for row in reader]

    all_comments = []
    
    for link in links:
        print(f"Visitando tweet: {link}")
        driver.get(link)
        time.sleep(5)  # Esperar a que cargue la página

        # Extraer comentarios
        comments = extract_comments_from_tweet(driver)
        if comments:
            for comment in comments:
                comment_data = {
                    "tweet_link": link,
                    "author": comment['author'],
                    "comment": comment['comment'],
                    "date": comment['date']
                }
                all_comments.append(comment_data)
                print(f"Comentario de {comment['author']} el {comment['date']}: {comment['comment']}")
        else:
            print(f"No se encontraron comentarios en {link}")

        scroll_to_bottom(driver)  # Hacer scroll para cargar más comentarios si es necesario

    # Guardar los comentarios en un archivo CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['tweet_link', 'author', 'comment', 'date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for comment_data in all_comments:
            writer.writerow(comment_data)

    # print(f"Comentarios guardados en '{output_file}'")

# Iniciar sesión en Twitter
login_to_twitter(driver, 'felix_jss@hotmail.com', 'felix1.2')

# Extraer comentarios de los tweets que están en el archivo 'tweets_21.csv'
extract_comments_from_links('tweets_21.csv', 'comentarios_tweets.csv')

# Cerrar el navegador
driver.quit()
