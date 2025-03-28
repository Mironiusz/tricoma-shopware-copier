import time
import logging
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# Konfiguracja logowania (możesz dostosować, by logi były wspólne dla całego projektu)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_fresh_element(driver, by, value, timeout=10, retries=3):
    """Próbuje kilka razy pobrać element, aby uniknąć błędu stale element reference."""
    attempt = 0
    while attempt < retries:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except StaleElementReferenceException:
            attempt += 1
            logging.warning("StaleElementReferenceException przy pobieraniu elementu %s, próba %d", value, attempt)
    raise Exception(f"Nie udało się pobrać elementu {value} po {retries} próbach.")

def init_driver():
    logging.info("Inicjalizacja Firefoksa z geckodriverem i dedykowanym profilem.")
    service = Service('./geckodriver.exe')
    options = Options()
    options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
    profile_path = r"C:\Users\Rafał\AppData\Roaming\Mozilla\Firefox\Profiles\52fg9yry.kopiowanie"
    options.profile = profile_path
    driver = webdriver.Firefox(service=service, options=options)
    return driver

def wait_for_login(driver):
    logging.info("Przeglądarka uruchomiona. Otwieram CRM.")
    # Otwórz CRM w pierwszej zakładce
    driver.get("https://adcl8198889.tricoma-netzwerk.de/cmssystem/")

    # Otwórz sklep w nowej zakładce
    driver.execute_script("window.open('https://noi-shop.ultra-media.de/admin#/sw/dashboard/index', '_blank');")

    # Wyświetl uchwyty otwartych zakładek (opcjonalnie)
    tabs = driver.window_handles
    logging.info("Otwartych zakładek: %s", tabs)

    # Teraz użytkownik musi zalogować się w obu stronach
    input("Zaloguj się w obu stronach (CRM i Sklep) oraz przejdź do wybranego produktu w CRM, następnie naciśnij Enter...")

def switch_to_crm(driver):
    """
    Przełącza widok na pierwszą zakładkę (CRM).
    """
    tabs = driver.window_handles
    if len(tabs) >= 1:
        driver.switch_to.window(tabs[0])
        logging.info("Przełączono na zakładkę CRM.")
    else:
        logging.error("Brak otwartych zakładek do przełączenia (CRM).")

def switch_to_product_iframe(driver):
    driver.switch_to.default_content()
    logging.info("Przełączam się na iframe z id 'contentframeprodukte'.")
    product_iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "contentframeprodukte"))
    )
    driver.switch_to.frame(product_iframe)
    logging.info("Przełączono na iframe produktu.")

def wait_for_product_page(driver):
    logging.info("Czekam na załadowanie strony produktu (szukam elementów o id 'feld44') wewnątrz iframe.")
    try:
        WebDriverWait(driver, 30).until(lambda d: len(d.find_elements(By.XPATH, "//*[@id='feld44']")) > 0)
        fields = driver.find_elements(By.XPATH, "//*[@id='feld44']")
        logging.info("Znaleziono %d elementów o id 'feld44'.", len(fields))
        return fields[0]
    except Exception as e:
        logging.error("Nie udało się znaleźć elementów o id 'feld44': %s", e)
        raise

def fill_product_data(driver):
    try:
        logging.info("Uzupełniam pole 'feld93' wartością 'Stck'.")
        feld93 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "feld93")))
        feld93.clear()
        feld93.send_keys("Stck")
        logging.info("Pole 'feld93' ustawione.")
    except Exception as e:
        logging.error("Błąd przy uzupełnianiu pola 'feld93': %s", e)

    try:
        logging.info("Uzupełniam pole 'feld94_vorne' wartością '1'.")
        feld94 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "feld94_vorne")))
        feld94.clear()
        feld94.send_keys("1")
        logging.info("Pole 'feld94_vorne' ustawione.")
    except Exception as e:
        logging.error("Błąd przy uzupełnianiu pola 'feld94_vorne': %s", e)

    try:
        logging.info("Ustawiam select 'feld99' na wartość '124'.")
        feld99 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "feld99")))
        select_feld99 = Select(feld99)
        select_feld99.select_by_value("124")
        logging.info("Select 'feld99' ustawiony.")
    except Exception as e:
        logging.error("Błąd przy ustawianiu selecta 'feld99': %s", e)

def click_save(driver):
    try:
        logging.info("Klikam przycisk zapisu.")
        save_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input.Buttonspeichern[name='feldspeichern']"))
        )
        save_button.click()
        logging.info("Przycisk zapisu kliknięty.")
    except Exception as e:
        logging.error("Błąd przy klikaniu przycisku zapisu: %s", e)

def get_product_details(driver):
    product_data = {}
    try:
        logging.info("Pobieram numer produktu z pola 'feld44' (odświeżając element).")
        new_field = get_fresh_element(driver, By.XPATH, "//*[@id='feld44']", timeout=10)
        artikelnummer = new_field.get_attribute("value")
        product_data["artikelnummer"] = artikelnummer
        logging.info("Numer produktu: %s", artikelnummer)
    except Exception as e:
        logging.error("Błąd przy pobieraniu numeru produktu: %s", e)

    try:
        logging.info("Pobieram wartość opakowania z pola 'feld82_vorne'.")
        verpackungseinheit = driver.find_element(By.ID, "feld82_vorne").get_attribute("value")
        product_data["verpackungseinheit"] = verpackungseinheit
        logging.info("Opakowanie: %s", verpackungseinheit)
    except Exception as e:
        logging.error("Błąd przy pobieraniu opakowania: %s", e)

    try:
        logging.info("Pobieram opis produktu z iframe edytora (tri_editor_feld42_ifr).")
        desc_iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "tri_editor_feld42_ifr"))
        )
        driver.switch_to.frame(desc_iframe)
        body_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        beschreibung = body_elem.get_attribute("innerHTML")
        product_data["beschreibung"] = beschreibung
        logging.info("Opis produktu pobrany.")
        driver.switch_to.parent_frame()
    except Exception as e:
        logging.error("Błąd przy pobieraniu opisu produktu z iframe: %s", e)
        product_data["beschreibung"] = ""
    return product_data

def handle_language_popup(driver, product_data):
    try:
        logging.info("Klikam przycisk wyboru języka (alt='Sprachwahl').")
        lang_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//img[@alt='Sprachwahl']"))
        )
        lang_button.click()
        logging.info("Przycisk wyboru języka kliknięty.")
    except Exception as e:
        logging.error("Błąd przy klikaniu przycisku wyboru języka: %s", e)

    logging.info("Powracam do głównego kontekstu (default_content).")
    driver.switch_to.default_content()

    try:
        logging.info("Czekam na pojawienie się iframe popupu językowego (id='contentframeSprache').")
        lang_iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "contentframeSprache"))
        )
        driver.switch_to.frame(lang_iframe)
        logging.info("Przełączono na iframe popupu językowego.")
    except Exception as e:
        logging.error("Błąd przy przełączaniu na iframe popupu językowego: %s", e)
        raise

    try:
        logging.info("Pobieram zawartość pól tytułów w popupie.")
        titel_fr_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "titel_FRA"))
        )
        product_data["titel_FRA"] = titel_fr_elem.get_attribute("value")
        logging.info("Zawartość pola 'titel_FRA': %s", product_data["titel_FRA"])

        titel_eng_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "titel_GBR"))
        )
        product_data["titel_GBR"] = titel_eng_elem.get_attribute("value")
        logging.info("Zawartość pola 'titel_GBR': %s", product_data["titel_GBR"])
    except Exception as e:
        logging.error("Błąd przy pobieraniu danych z popupu (iframe): %s", e)

    logging.info("Powracam do głównego kontekstu (default_content) w celu zamknięcia popupu.")
    driver.switch_to.default_content()

    try:
        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div#window_Sprache img.window_close"))
        )
        driver.execute_script("arguments[0].click();", close_button)
        logging.info("Kliknięto przycisk zamknięcia popupu (X) w głównym dokumencie.")
    except Exception as e:
        logging.error("Błąd przy zamykaniu popupu: %s", e)
    driver.switch_to.default_content()
    logging.info("Powrót do głównego kontekstu po operacjach w popupie.")

def click_sonstige_preise(driver):
    logging.info("Przełączam się na iframe 'contentframeprodukte' przed kliknięciem 'Sonstige Preise'.")
    driver.switch_to.frame("contentframeprodukte")
    try:
        logging.info("Czekam na widoczność elementu 'Sonstige Preise' (ID: list_element_8) w iframe 'contentframeprodukte'.")
        sonstige_preise = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.ID, "list_element_8"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", sonstige_preise)
        driver.execute_script("arguments[0].click();", sonstige_preise)
        logging.info("'Sonstige Preise' kliknięte w iframe 'contentframeprodukte'.")
    except Exception as e:
        logging.error("Błąd przy klikaniu 'Sonstige Preise' w iframe 'contentframeprodukte': %s", e)
        raise

def click_produktdaten(driver):
    logging.info("Przełączam się na iframe 'contentframeprodukte' przed kliknięciem 'Produktdaten'.")
    driver.switch_to.default_content()
    driver.switch_to.frame("contentframeprodukte")
    try:
        # Znajdź boczny panel przewijania (np. element zawierający menu)
        scroll_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "td.menu_bg"))
        )
        # Przewiń ten kontener na górę
        driver.execute_script("arguments[0].scrollTop = 0;", scroll_container)
        logging.info("Boczny panel został przewinięty na górę.")

        logging.info("Czekam na widoczność elementu 'Produktdaten' (ID: list_element_2) w iframe 'contentframeprodukte'.")
        produktdaten = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.ID, "list_element_2"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", produktdaten)
        driver.execute_script("arguments[0].click();", produktdaten)
        logging.info("'Produktdaten' kliknięte w iframe 'contentframeprodukte'.")
        driver.switch_to.default_content()
    except Exception as e:
        logging.error("Błąd przy klikaniu 'Produktdaten' w iframe 'contentframeprodukte': %s", e)
        driver.switch_to.default_content()
        raise

def switch_to_frameunten(driver):
    try:
        logging.info("Czekam na pojawienie się iframe 'frameunten'.")
        frameunten = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "frameunten"))
        )
        driver.switch_to.frame(frameunten)
        logging.info("Przełączono na iframe 'frameunten'.")
    except Exception as e:
        logging.error("Błąd przy przełączaniu na iframe 'frameunten': %s", e)
        raise

def click_advanced_price_settings(driver):
    try:
        logging.info("Czekam na widoczność linku 'Erweiterte Preiseinstellungen'.")
        advanced_link = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//a[contains(@href, 'auswahl=preise') and contains(., 'Erweiterte Preiseinstellungen')]")
            )
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", advanced_link)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'auswahl=preise') and contains(., 'Erweiterte Preiseinstellungen')]"))
        )
        driver.execute_script("arguments[0].click();", advanced_link)
        logging.info("Link 'Erweiterte Preiseinstellungen' kliknięty.")
    except Exception as e:
        logging.error("Błąd przy klikaniu linku 'Erweiterte Preiseinstellungen': %s", e)
        raise

def get_prices(driver, product_data):
    try:
        logging.info("Pobieram ceny przy użyciu sekcji 'Weitere Verkaufspreise (€):'.")
        # Znajdź kontener tri_box, którego nagłówek zawiera "Weitere Verkaufspreise (€):"
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@class='tri_box'][p[contains(., 'Weitere Verkaufspreise (€)')]]")
            )
        )
        # Zrzut HTML dla debugowania
        dump_frame_html(driver, file_path="debug_before_prices.html")

        # W obrębie kontenera znajdź div z klasą "content" i wewnętrzną tabelę
        table = container.find_element(By.XPATH, ".//div[@class='content']//table[contains(@class, 'table_listing')]")

        # Znajdź wiersz dla "Händler (H)"
        handler_row = table.find_element(By.XPATH, ".//tr[td[contains(., 'Händler (H)')]]")
        handler_int = handler_row.find_element(
            By.XPATH, ".//input[contains(@class, 'zahlenfeld_vorkomma')]"
        ).get_attribute("value")
        handler_dec = handler_row.find_element(
            By.XPATH, ".//input[contains(@class, 'zahlenfeld_nachkomma')]"
        ).get_attribute("value")
        handler_preis = f"{handler_int}.{handler_dec}"
        product_data["handler_preis"] = handler_preis
        logging.info("Handler preis: %s", handler_preis)

        # Znajdź wiersz dla "Endkunden (EK)"
        endkunde_row = table.find_element(By.XPATH, ".//tr[td[contains(., 'Endkunden (EK)')]]")
        endkunde_int = endkunde_row.find_element(
            By.XPATH, ".//input[contains(@class, 'zahlenfeld_vorkomma')]"
        ).get_attribute("value")
        endkunde_dec = endkunde_row.find_element(
            By.XPATH, ".//input[contains(@class, 'zahlenfeld_nachkomma')]"
        ).get_attribute("value")
        endkunde_preis = f"{endkunde_int}.{endkunde_dec}"
        product_data["endkunde_preis"] = endkunde_preis
        logging.info("Endkunde preis: %s", endkunde_preis)
    except Exception as e:
        logging.error("Błąd przy pobieraniu cen: %s", e)
        raise

def click_shopware6(driver):
    # Przełączamy się ponownie na iframe 'contentframeprodukte'
    driver.switch_to.frame("contentframeprodukte")
    logging.info("Przełączono na iframe 'contentframeprodukte'.")
    try:
        logging.info("Czekam na widoczność elementu 'Shopware 6' (ID: list_element_20).")
        shopware6 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "list_element_20"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", shopware6)
        driver.execute_script("arguments[0].click();", shopware6)
        logging.info("'Shopware 6' kliknięty.")
    except Exception as e:
        logging.error("Błąd przy klikaniu 'Shopware 6': %s", e)
        raise

def switch_to_shopware_frame(driver):
    try:
        logging.info("Czekam na pojawienie się iframe 'frameunten' (dla Shopware 6) w obrębie 'contentframeprodukte'.")
        shopware_frame = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//iframe[@id='frameunten' and contains(@src, 'shopwaresechs')]")
            )
        )
        logging.info("Znaleziony iframe 'frameunten'.")
        driver.switch_to.frame(shopware_frame)
        logging.info("Przełączono na iframe 'frameunten' dla Shopware 6.")
    except Exception as e:
        logging.error("Błąd przy przełączaniu na iframe 'frameunten' dla Shopware 6: %s", e)
        raise

def dump_frame_html(driver, file_path="frame_content.html"):
    html = driver.page_source
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    logging.info("Zrzut HTML do pliku %s wykonany.", file_path)

def check_and_import_product(driver):
    logging.info("Sprawdzam, czy produkt został już importiert (szukam tekstu 'importiert').")
    try:
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'importiert')]")
            )
        )
        logging.info("Produkt już został importiert – pomijam kliknięcia.")
        return
    except Exception:
        logging.info("Produkt nie jest importiert – kontynuuję akcję.")

    try:
        logging.info("Klikam przycisk 'produktabgleich_vormerken'.")
        button_vormerken = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "produktabgleich_vormerken"))
        )
        button_vormerken.click()
        logging.info("Przycisk 'produktabgleich_vormerken' kliknięty.")
    except Exception as e:
        logging.error("Błąd przy klikaniu przycisku 'produktabgleich_vormerken': %s", e)
        raise

    try:
        logging.info("Próbuję kliknąć przycisk 'produktabgleich_durchfuehren'.")
        button_durchfuehren = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "produktabgleich_durchfuehren"))
        )
        button_durchfuehren.click()
        logging.info("Przycisk 'produktabgleich_durchfuehren' kliknięty.")
    except Exception as e:
        logging.warning("Przycisk 'produktabgleich_durchfuehren' nie został znaleziony lub nie można go kliknąć: %s", e)

    try:
        logging.info("Czekam na pojawienie się potwierdzenia 'importiert'.")
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'importiert') and contains(@style, 'color: green')]")
            )
        )
        logging.info("Produkt został pomyślnie importiert w Shopware 6.")
    except Exception as e:
        logging.error("Błąd przy oczekiwaniu na potwierdzenie importu: %s", e)
        raise

    driver.switch_to.default_content()
