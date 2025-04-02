import logging
import time
import json
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

class CRMDownloader:
    def __init__(self, driver):
        self.driver = driver

    def load_product_data(self, filename="product_data.json"):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            logging.info("Dane produktu wczytane z %s", filename)
            return data
        except Exception as e:
            logging.error("Błąd przy wczytywaniu danych z pliku %s: %s", filename, e)
            return {}

    def save_product_data(self, product_data, filename="product_data.json"):
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(product_data, f, ensure_ascii=False, indent=4)
            logging.info("Dane produktu zapisane do pliku: %s", filename)
        except Exception as e:
            logging.error("Błąd przy zapisywaniu danych produktu do pliku: %s", e)

    def display_final_info(self, product_data):
        print("\n--- Podsumowanie danych produktu ---")
        for key, value in product_data.items():
            print(f"{key}: {value}")
        print("--- Koniec podsumowania ---")

    def wait_for_login(self, crm_url, shop_url):
        logging.info("Otwieram CRM oraz Sklep")
        self.driver.get(crm_url)
        self.driver.execute_script("window.open(arguments[0], '_blank');", shop_url)
        tabs = self.driver.window_handles
        logging.info("Otwartych zakładek: %s", tabs)

    def switch_to_crm(self):
        tabs = self.driver.window_handles
        if len(tabs) >= 1:
            self.driver.switch_to.window(tabs[0])
            logging.info("Przełączono na zakładkę CRM.")
            self.driver.switch_to.default_content()
        else:
            logging.error("Brak otwartych zakładek do przełączenia (CRM).")

    def switch_to_product_iframe(self):
        self.driver.switch_to.default_content()
        logging.info("Przełączam się na iframe z id 'contentframeprodukte'.")
        product_iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "contentframeprodukte"))
        )
        self.driver.switch_to.frame(product_iframe)
        logging.info("Przełączono na iframe produktu.")

    def wait_for_product_page(self):
        logging.info("Czekam na załadowanie strony produktu (element o id 'feld44').")
        try:
            WebDriverWait(self.driver, 30).until(lambda d: len(d.find_elements(By.XPATH, "//*[@id='feld44']")) > 0)
            fields = self.driver.find_elements(By.XPATH, "//*[@id='feld44']")
            logging.info("Znaleziono %d elementów o id 'feld44'.", len(fields))
            return fields[0]
        except Exception as e:
            logging.error("Nie udało się znaleźć elementu 'feld44': %s", e)
            raise

    def fill_product_data(self):
        try:
            logging.info("Uzupełniam pole 'feld93' wartością 'Stck'.")
            feld93 = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "feld93"))
            )
            feld93.clear()
            feld93.send_keys("Stck")
            logging.info("Pole 'feld93' ustawione.")
        except Exception as e:
            logging.error("Błąd przy uzupełnianiu pola 'feld93': %s", e)
        try:
            logging.info("Uzupełniam pole 'feld94_vorne' wartością '1'.")
            feld94 = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "feld94_vorne"))
            )
            feld94.clear()
            feld94.send_keys("1")
            logging.info("Pole 'feld94_vorne' ustawione.")
        except Exception as e:
            logging.error("Błąd przy uzupełnianiu pola 'feld94_vorne': %s", e)
        try:
            logging.info("Ustawiam select 'feld99' na wartość '124'.")
            feld99 = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "feld99"))
            )
            select_feld99 = Select(feld99)
            select_feld99.select_by_value("124")
            logging.info("Select 'feld99' ustawiony.")
        except Exception as e:
            logging.error("Błąd przy ustawianiu selecta 'feld99': %s", e)

    def click_save(self):
        try:
            logging.info("Klikam przycisk zapisu.")
            save_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input.Buttonspeichern[name='feldspeichern']"))
            )
            save_button.click()
            logging.info("Przycisk zapisu kliknięty.")
        except Exception as e:
            logging.error("Błąd przy klikaniu przycisku zapisu: %s", e)

    def remove_inline_styles(self, html):
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(True):
            for attr in ["style", "data-mce-style"]:
                if tag.has_attr(attr):
                    del tag[attr]
        return str(soup)

    def get_product_details(self):
        product_data = {}
        try:
            logging.info("Pobieram numer produktu z pola 'feld44'.")
            new_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='feld44']"))
            )
            artikelnummer = new_field.get_attribute("value")
            product_data["artikelnummer"] = artikelnummer
            logging.info("Numer produktu: %s", artikelnummer)
        except Exception as e:
            logging.error("Błąd przy pobieraniu numeru produktu: %s", e)
        try:
            logging.info("Pobieram wartość opakowania z pola 'feld82_vorne'.")
            verpackungseinheit = self.driver.find_element(By.ID, "feld82_vorne").get_attribute("value")
            product_data["verpackungseinheit"] = verpackungseinheit
            logging.info("Opakowanie: %s", verpackungseinheit)
        except Exception as e:
            logging.error("Błąd przy pobieraniu opakowania: %s", e)
        try:
            logging.info("Pobieram opis produktu z iframe edytora.")
            desc_iframe = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "tri_editor_feld42_ifr"))
            )
            self.driver.switch_to.frame(desc_iframe)
            body_elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            beschreibung = body_elem.get_attribute("innerHTML")
            beschreibung = self.remove_inline_styles(beschreibung)
            product_data["beschreibung"] = beschreibung
            logging.info("Opis produktu pobrany.")
            self.driver.switch_to.parent_frame()
        except Exception as e:
            logging.error("Błąd przy pobieraniu opisu produktu: %s", e)
            product_data["beschreibung"] = ""
        return product_data

    def handle_language_popup(self, product_data):
        try:
            logging.info("Klikam przycisk wyboru języka (alt='Sprachwahl').")
            lang_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//img[@alt='Sprachwahl']"))
            )
            lang_button.click()
            logging.info("Przycisk wyboru języka kliknięty.")
        except Exception as e:
            logging.error("Błąd przy klikaniu przycisku wyboru języka: %s", e)
        logging.info("Powracam do głównego kontekstu.")
        self.driver.switch_to.default_content()
        try:
            logging.info("Czekam na iframe popupu językowego (id='contentframeSprache').")
            lang_iframe = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "contentframeSprache"))
            )
            self.driver.switch_to.frame(lang_iframe)
            logging.info("Przełączono na iframe popupu językowego.")
        except Exception as e:
            logging.error("Błąd przy przełączaniu na iframe popupu językowego: %s", e)
            raise
        try:
            logging.info("Pobieram zawartość pól tytułów w popupie.")
            titel_fr_elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "titel_FRA"))
            )
            product_data["titel_FRA"] = titel_fr_elem.get_attribute("value")
            logging.info("Pobrano 'titel_FRA': %s", product_data["titel_FRA"])
            titel_eng_elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "titel_GBR"))
            )
            product_data["titel_GBR"] = titel_eng_elem.get_attribute("value")
            logging.info("Pobrano 'titel_GBR': %s", product_data["titel_GBR"])
        except Exception as e:
            logging.error("Błąd przy pobieraniu danych z popupu: %s", e)
        logging.info("Powracam do głównego kontekstu.")
        self.driver.switch_to.default_content()
        try:
            close_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div#window_Sprache img.window_close"))
            )
            self.driver.execute_script("arguments[0].click();", close_button)
            logging.info("Popup zamknięty.")
        except Exception as e:
            logging.error("Błąd przy zamykaniu popupu: %s", e)
        self.driver.switch_to.default_content()

    def click_sonstige_preise(self):
        logging.info("Przełączam się na iframe 'contentframeprodukte' przed kliknięciem 'Sonstige Preise'.")
        self.driver.switch_to.frame("contentframeprodukte")
        try:
            logging.info("Czekam na element 'Sonstige Preise'.")
            sonstige_preise = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.ID, "list_element_8"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", sonstige_preise)
            self.driver.execute_script("arguments[0].click();", sonstige_preise)
            logging.info("'Sonstige Preise' kliknięte.")
        except Exception as e:
            logging.error("Błąd przy klikaniu 'Sonstige Preise': %s", e)
            raise

    def switch_to_frameunten(self):
        try:
            logging.info("Czekam na iframe 'frameunten'.")
            frameunten = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "frameunten"))
            )
            self.driver.switch_to.frame(frameunten)
            logging.info("Przełączono na iframe 'frameunten'.")
        except Exception as e:
            logging.error("Błąd przy przełączaniu na iframe 'frameunten': %s", e)
            raise

    def click_advanced_price_settings(self):
        try:
            logging.info("Czekam na link 'Erweiterte Preiseinstellungen'.")
            advanced_link = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, "//a[contains(@href, 'auswahl=preise') and contains(., 'Erweiterte Preiseinstellungen')]"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", advanced_link)
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'auswahl=preise') and contains(., 'Erweiterte Preiseinstellungen')]"))
            )
            self.driver.execute_script("arguments[0].click();", advanced_link)
            logging.info("Kliknięto link 'Erweiterte Preiseinstellungen'.")
        except Exception as e:
            logging.error("Błąd przy klikaniu linku: %s", e)
            raise

    def get_prices(self, product_data):
        try:
            logging.info("Pobieram ceny z sekcji 'Weitere Verkaufspreise (€)'.")
            container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='tri_box'][p[contains(., 'Weitere Verkaufspreise (€)')]]"))
            )
            # html = self.driver.page_source
            # with open("debug_before_prices.html", "w", encoding="utf-8") as f:
            #     f.write(html)
            table = container.find_element(By.XPATH, ".//div[@class='content']//table[contains(@class, 'table_listing')]")
            handler_row = table.find_element(By.XPATH, ".//tr[td[contains(., 'Händler (H)')]]")
            handler_int = handler_row.find_element(By.XPATH, ".//input[contains(@class, 'zahlenfeld_vorkomma')]").get_attribute("value")
            handler_dec = handler_row.find_element(By.XPATH, ".//input[contains(@class, 'zahlenfeld_nachkomma')]").get_attribute("value")
            handler_preis = f"{handler_int}.{handler_dec}"
            product_data["handler_preis"] = handler_preis
            logging.info("Handler preis: %s", handler_preis)
            endkunde_row = table.find_element(By.XPATH, ".//tr[td[contains(., 'Endkunden (EK)')]]")
            endkunde_int = endkunde_row.find_element(By.XPATH, ".//input[contains(@class, 'zahlenfeld_vorkomma')]").get_attribute("value")
            endkunde_dec = endkunde_row.find_element(By.XPATH, ".//input[contains(@class, 'zahlenfeld_nachkomma')]").get_attribute("value")
            endkunde_preis = f"{endkunde_int}.{endkunde_dec}"
            product_data["endkunde_preis"] = endkunde_preis
            logging.info("Endkunde preis: %s", endkunde_preis)
            self.driver.switch_to.default_content()
        except Exception as e:
            logging.error("Błąd przy pobieraniu cen: %s", e)
            raise

    def click_shopware6(self):
        self.driver.switch_to.frame("contentframeprodukte")
        logging.info("Przełączono na iframe 'contentframeprodukte'.")
        try:
            logging.info("Czekam na element 'Shopware 6'.")
            shopware6 = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "list_element_26")) # christine: 20, noihamburg: 26
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", shopware6)
            self.driver.execute_script("arguments[0].click();", shopware6)
            logging.info("'Shopware 6' kliknięty.")
        except Exception as e:
            logging.error("Błąd przy klikaniu 'Shopware 6': %s", e)
            raise

    def switch_to_shopware_frame(self):
        try:
            logging.info("Czekam na iframe 'frameunten' dla Shopware 6.")
            shopware_frame = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//iframe[@id='frameunten' and contains(@src, 'shopwaresechs')]"))
            )
            logging.info("Znaleziono iframe 'frameunten'.")
            self.driver.switch_to.frame(shopware_frame)
            logging.info("Przełączono na iframe 'frameunten' dla Shopware 6.")
        except Exception as e:
            logging.error("Błąd przy przełączaniu na iframe 'frameunten': %s", e)
            raise

    def check_and_import_product(self):
        logging.info("Sprawdzam, czy produkt został już importiert.")
        try:
            WebDriverWait(self.driver, 1).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'importiert')]"))
            )
            logging.info("Produkt już został importiert – pomijam kliknięcia.")
            return
        except Exception:
            logging.info("Produkt nie jest importiert – kontynuuję akcję.")
        try:
            logging.info("Klikam przycisk 'produktabgleich_vormerken'.")
            button_vormerken = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "produktabgleich_vormerken"))
            )
            button_vormerken.click()
            logging.info("Przycisk 'produktabgleich_vormerken' kliknięty.")
        except Exception as e:
            logging.error("Błąd przy klikaniu 'produktabgleich_vormerken': %s", e)
            raise
        try:
            logging.info("Klikam przycisk 'produktabgleich_durchfuehren'.")
            button_durchfuehren = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "produktabgleich_durchfuehren"))
            )
            button_durchfuehren.click()
            logging.info("Przycisk 'produktabgleich_durchfuehren' kliknięty.")
        except Exception as e:
            logging.warning("Przycisk 'produktabgleich_durchfuehren' nie został znaleziony lub nie można go kliknąć: %s", e)
        try:
            logging.info("Czekam na potwierdzenie 'importiert'.")
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'importiert') and contains(@style, 'color: green')]"))
            )
            logging.info("Produkt został pomyślnie importiert.")
        except Exception as e:
            logging.error("Błąd przy oczekiwaniu na potwierdzenie importu: %s", e)
            raise
        self.driver.switch_to.default_content()

    def click_produktdaten(self):
        try:
            logging.info("Klikam 'Produktdaten'.")
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("contentframeprodukte")
            scroll_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "td.menu_bg"))
            )
            self.driver.execute_script("arguments[0].scrollTop = 0;", scroll_container)
            produktdaten = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.ID, "list_element_2"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", produktdaten)
            self.driver.execute_script("arguments[0].click();", produktdaten)
            logging.info("'Produktdaten' kliknięte.")
            self.driver.switch_to.default_content()
        except Exception as e:
            logging.error("Błąd przy klikaniu 'Produktdaten': %s", e)
            self.driver.switch_to.default_content()
            raise

    def run_sequence(self):
        self.switch_to_crm()
        self.switch_to_product_iframe()
        self.wait_for_product_page()
        self.fill_product_data()
        self.click_save()
        product_data = self.get_product_details()
        self.handle_language_popup(product_data)
        self.click_sonstige_preise()
        self.switch_to_frameunten()
        self.click_advanced_price_settings()
        self.get_prices(product_data)
        self.click_shopware6()
        self.switch_to_shopware_frame()
        self.check_and_import_product()
        self.click_produktdaten()

        return product_data
