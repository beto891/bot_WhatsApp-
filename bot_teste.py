import os
import time
import requests
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Configurações
download_folder = "Checking de fotos"  # Pasta onde as fotos serão salvas

# Dicionário de palavras-chave e IDs correspondentes
id_mapping = {
    "foto1": "609",  # Substitua pelas suas palavras-chave e IDs
    "foto2": "766"
}

# Cria a pasta de downloads se não existir
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

# Inicializa o WebDriver com undetected-chromedriver
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = uc.Chrome(options=options)

driver.get("https://web.whatsapp.com")

# Aguarde o usuário escanear o código QR
input("Pressione Enter após escanear o código QR")

# Acessa o grupo pelo nome
group_name = "Rotas diárias"  # Substitua pelo nome do seu grupo
search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"]')
search_box.click()
search_box.send_keys(group_name)
search_box.send_keys(Keys.ENTER)

# Aguarda o carregamento do grupo
time.sleep(5)

# Função para baixar imagens
def download_images(image_urls, group_id):
    # Cria a pasta para o ID se não existir
    id_folder = os.path.join(download_folder, f"ID_{group_id}")
    if not os.path.exists(id_folder):
        os.makedirs(id_folder)

    for index, image_url in enumerate(image_urls):
        image_data = requests.get(image_url).content
        image_path = os.path.join(id_folder, f"{group_id}_image_{index + 1}.jpg")
        
        with open(image_path, 'wb') as f:
            f.write(image_data)

# Loop para monitorar mensagens
last_message_count = 0  # Contador de mensagens para detectar novas mensagens
try:
    while True:
        # Obtém as mensagens do grupo
        messages = driver.find_elements(By.XPATH, '//div[contains(@class, "message-in")]')  # Ajuste o XPath conforme necessário

        # Verifica se há novas mensagens
        if len(messages) > last_message_count:
            last_message_count = len(messages)  # Atualiza o contador de mensagens

            for message in messages:
                message_text = message.text
                
                # Verifica se a mensagem contém uma palavra-chave
                for keyword, group_id in id_mapping.items():
                    if keyword in message_text:
                        print(f"Palavra-chave '{keyword}' encontrada. ID correspondente: {group_id}")

                        # Usa regex para encontrar IDs na mensagem
                        ids_found = re.findall(r'\b\d+\b', message_text)  # Encontra todos os números na mensagem
                        for found_id in ids_found:
                            if found_id in id_mapping.values():
                                print(f"ID encontrado: {found_id}")

                                # Encontra todas as imagens na conversa
                                images = driver.find_elements(By.XPATH, '//img[contains(@src, "data:image/jpeg")]')
                                image_urls = [image.get_attribute('src') for image in images]

                                # Baixa as imagens
                                download_images(image_urls, found_id)
                                print(f"Imagens salvas na pasta: {os.path.join(download_folder, f'ID_{found_id}')}")
        
        time.sleep(2)  # Aguarda um pouco antes de verificar novamente

except KeyboardInterrupt:
    print("Bot encerrado.")
finally:
    # Fecha o WebDriver
    driver.quit()