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
            logging.info("Product data loaded from %s", filename)
            return data
        except Exception as e:
            logging.error("Error loading data from file %s: %s", filename, e)
            return {}

    def save_product_data(self, product_data, filename="product_data.json"):
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(product_data, f, ensure_ascii=False, indent=4)
            logging.info("Product data saved to file: %s", filename)
        except Exception as e:
            logging.error("Error saving product data to file: %s", e)

    def display_final_info(self, product_data):
        print("\n--- Product data summary ---")
        for key, value in product_data.items():
            print(f"{key}: {value}")
        print("--- End of summary ---")

    def wait_for_login(self, crm_url, shop_url):
        logging.info("Opening CRM and shop")
        self.driver.get(crm_url)
        self.driver.execute_script("window.open(arguments[0], '_blank');", shop_url)
        tabs = self.driver.window_handles
        logging.info("Open tabs: %s", tabs)

    def switch_to_crm(self):
        tabs = self.driver.window_handles
        if len(tabs) >= 1:
            self.driver.switch_to.window(tabs[0])
            logging.info("Switched to CRM tab.")
            self.driver.switch_to.default_content()
        else:
            logging.error("No open tabs to switch to (CRM).")

    def switch_to_product_iframe(self):
        self.driver.switch_to.default_content()
        logging.info("Switching to iframe with id 'contentframeprodukte'.")
        product_iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "contentframeprodukte"))
        )
        self.driver.switch_to.frame(product_iframe)
        logging.info("Switched to product iframe.")

    def wait_for_product_page(self):
        logging.info("Waiting for product page to load (element with id 'feld44').")
        try:
            WebDriverWait(self.driver, 30).until(lambda d: len(d.find_elements(By.XPATH, "//*[@id='feld44']")) > 0)
            fields = self.driver.find_elements(By.XPATH, "//*[@id='feld44']")
            logging.info("Found %d elements with id 'feld44'.", len(fields))
            return fields[0]
        except Exception as e:
            logging.error("Failed to find element 'feld44': %s", e)
            raise

    def fill_product_data(self):
        try:
            logging.info("Filling 'feld93' with value 'Stck'.")
            feld93 = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "feld93"))
            )
            feld93.clear()
            feld93.send_keys("Stck")
            logging.info("Field 'feld93' set.")
        except Exception as e:
            logging.error("Error filling field 'feld93': %s", e)
        try:
            logging.info("Filling 'feld94_vorne' with value '1'.")
            feld94 = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "feld94_vorne"))
            )
            feld94.clear()
            feld94.send_keys("1")
            logging.info("Field 'feld94_vorne' set.")
        except Exception as e:
            logging.error("Error filling field 'feld94_vorne': %s", e)
        try:
            logging.info("Setting select 'feld99' to value '124'.")
            feld99 = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "feld99"))
            )
            select_feld99 = Select(feld99)
            select_feld99.select_by_value("124")
            logging.info("Select 'feld99' set.")
        except Exception as e:
            logging.error("Error setting select 'feld99': %s", e)

    def click_save(self):
        try:
            logging.info("Clicking save button.")
            save_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input.Buttonspeichern[name='feldspeichern']"))
            )
            save_button.click()
            logging.info("Save button clicked.")
        except Exception as e:
            logging.error("Error clicking save button: %s", e)

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
            logging.info("Retrieving product number from 'feld44'.")
            new_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='feld44']"))
            )
            artikelnummer = new_field.get_attribute("value")
            product_data["artikelnummer"] = artikelnummer
            logging.info("Product number: %s", artikelnummer)
        except Exception as e:
            logging.error("Error retrieving product number: %s", e)
        try:
            logging.info("Retrieving packaging unit from 'feld82_vorne'.")
            verpackungseinheit = self.driver.find_element(By.ID, "feld82_vorne").get_attribute("value")
            product_data["verpackungseinheit"] = verpackungseinheit
            logging.info("Packaging unit: %s", verpackungseinheit)
        except Exception as e:
            logging.error("Error retrieving packaging unit: %s", e)
        try:
            logging.info("Retrieving product description from editor iframe.")
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
            logging.info("Product description retrieved.")
            self.driver.switch_to.parent_frame()
        except Exception as e:
            logging.error("Error retrieving product description: %s", e)
            product_data["beschreibung"] = ""
        return product_data

    def handle_language_popup(self, product_data):
        try:
            logging.info("Clicking language selection button (alt='Sprachwahl').")
            lang_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//img[@alt='Sprachwahl']"))
            )
            lang_button.click()
            logging.info("Language selection button clicked.")
        except Exception as e:
            logging.error("Error clicking language selection button: %s", e)
        logging.info("Returning to main context.")
        self.driver.switch_to.default_content()
        try:
            logging.info("Waiting for language popup iframe (id='contentframeSprache').")
            lang_iframe = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "contentframeSprache"))
            )
            self.driver.switch_to.frame(lang_iframe)
            logging.info("Switched to language popup iframe.")
        except Exception as e:
            logging.error("Error switching to language popup iframe: %s", e)
            raise
        try:
            logging.info("Retrieving title fields from popup.")
            titel_fr_elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "titel_FRA"))
            )
            product_data["titel_FRA"] = titel_fr_elem.get_attribute("value")
            logging.info("Retrieved 'titel_FRA': %s", product_data["titel_FRA"])
            titel_eng_elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "titel_GBR"))
            )
            product_data["titel_GBR"] = titel_eng_elem.get_attribute("value")
            logging.info("Retrieved 'titel_GBR': %s", product_data["titel_GBR"])
        except Exception as e:
            logging.error("Error retrieving data from popup: %s", e)
        logging.info("Returning to main context.")
        self.driver.switch_to.default_content()
        try:
            close_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div#window_Sprache img.window_close"))
            )
            self.driver.execute_script("arguments[0].click();", close_button)
            logging.info("Popup closed.")
        except Exception as e:
            logging.error("Error closing popup: %s", e)
        self.driver.switch_to.default_content()

    def click_sonstige_preise(self):
        logging.info("Switching to iframe 'contentframeprodukte' before clicking 'Sonstige Preise'.")
        self.driver.switch_to.frame("contentframeprodukte")
        try:
            logging.info("Waiting for 'Sonstige Preise' element.")
            sonstige_preise = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.ID, "list_element_8"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", sonstige_preise)
            self.driver.execute_script("arguments[0].click();", sonstige_preise)
            logging.info("'Sonstige Preise' clicked.")
        except Exception as e:
            logging.error("Error clicking 'Sonstige Preise': %s", e)
            raise

    def switch_to_frameunten(self):
        try:
            logging.info("Waiting for iframe 'frameunten'.")
            frameunten = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "frameunten"))
            )
            self.driver.switch_to.frame(frameunten)
            logging.info("Switched to iframe 'frameunten'.")
        except Exception as e:
            logging.error("Error switching to iframe 'frameunten': %s", e)
            raise

    def click_advanced_price_settings(self):
        try:
            logging.info("Waiting for 'Erweiterte Preiseinstellungen' link.")
            advanced_link = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, "//a[contains(@href, 'auswahl=preise') and contains(., 'Erweiterte Preiseinstellungen')]"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", advanced_link)
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'auswahl=preise') and contains(., 'Erweiterte Preiseinstellungen')]"))
            )
            self.driver.execute_script("arguments[0].click();", advanced_link)
            logging.info("'Erweiterte Preiseinstellungen' clicked.")
        except Exception as e:
            logging.error("Error clicking link: %s", e)
            raise

    def get_prices(self, product_data):
        try:
            logging.info("Retrieving prices from 'Weitere Verkaufspreise (€)' section.")
            container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='tri_box'][p[contains(., 'Weitere Verkaufspreise (€)')]]"))
            )
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
            logging.error("Error retrieving prices: %s", e)
            raise

    def click_shopware6(self, sciezka_pliku="plik.txt"):
        self.driver.switch_to.frame("contentframeprodukte")
        logging.info("Switched to iframe 'contentframeprodukte'.")

        try:
            login = open(sciezka_pliku, "r", encoding="utf-8").readline().strip()
            if not login:
                raise ValueError("No login in file")
            element_id = f"list_element_{26 if login.lower() == 'noihamburg' else 20}"

            logging.info("Waiting for Shopware 6 element with ID '%s'.", element_id)
            shopware6 = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, element_id))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", shopware6)
            self.driver.execute_script("arguments[0].click();", shopware6)
            logging.info("'Shopware 6' clicked.")
        except FileNotFoundError:
            logging.error("File not found: %s", sciezka_pliku)
            raise
        except Exception as e:
            logging.error("Error clicking 'Shopware 6': %s", e)
            raise

    def switch_to_shopware_frame(self):
        try:
            logging.info("Waiting for iframe 'frameunten' for Shopware 6.")
            shopware_frame = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//iframe[@id='frameunten' and contains(@src, 'shopwaresechs')]"))
            )
            logging.info("Found iframe 'frameunten'.")
            self.driver.switch_to.frame(shopware_frame)
            logging.info("Switched to iframe 'frameunten' for Shopware 6.")
        except Exception as e:
            logging.error("Error switching to iframe 'frameunten': %s", e)
            raise

    def check_and_import_product(self):
        logging.info("Checking if product has already been importiert.")
        try:
            WebDriverWait(self.driver, 1).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'importiert')]"))
            )
            logging.info("Product already importiert – skipping clicks.")
            return
        except Exception:
            logging.info("Product not importiert – continuing actions.")
        try:
            logging.info("Clicking 'produktabgleich_vormerken' button.")
            button_vormerken = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "produktabgleich_vormerken"))
            )
            button_vormerken.click()
            logging.info("'produktabgleich_vormerken' clicked.")
        except Exception as e:
            logging.error("Error clicking 'produktabgleich_vormerken': %s", e)
            raise
        try:
            logging.info("Clicking 'produktabgleich_durchfuehren' button.")
            button_durchfuehren = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "produktabgleich_durchfuehren"))
            )
            button_durchfuehren.click()
            logging.info("'produktabgleich_durchfuehren' clicked.")
        except Exception as e:
            logging.warning("'produktabgleich_durchfuehren' not found or not clickable: %s", e)
        try:
            logging.info("Waiting for confirmation 'importiert'.")
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'importiert') and contains(@style, 'color: green')]"))
            )
            logging.info("Product successfully importiert.")
        except Exception as e:
            logging.error("Error waiting for import confirmation: %s", e)
            raise
        self.driver.switch_to.default_content()

    def click_produktdaten(self):
        try:
            logging.info("Clicking 'Produktdaten'.")
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
            logging.info("'Produktdaten' clicked.")
            self.driver.switch_to.default_content()
        except Exception as e:
            logging.error("Error clicking 'Produktdaten': %s", e)
            self.driver.switch_to.default_content()
            raise

    def open_product(self, product_name):
        logging.info("open_product: searching for '%s'", product_name)
        self.switch_to_crm()
        self.driver.switch_to.default_content()

        inp = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "tricoma_maneta_search"))
        )

        try:
            self.driver.execute_script("arguments[0].click();", inp)
        except Exception:
            logging.warning("open_product: JS click failed, trying normal click()")
            inp.click()

        time.sleep(0.5)

        inp = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.ID, "tricoma_maneta_search"))
        )
        inp.clear()
        inp.send_keys(product_name)
        logging.info("open_product: entered '%s' in search", product_name)

        result_box = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "maneta_search_window"))
        )

        first_link = result_box.find_element(By.CSS_SELECTOR, "a.tricoma_list_element_link")
        self.driver.execute_script("arguments[0].click();", first_link)
        logging.info("open_product: clicked first result")

        time.sleep(3)

        self.switch_to_product_iframe()
        self.wait_for_product_page()
        logging.info("open_product: product page loaded")

    def run_sequence(self):
        self.switch_to_crm()
        self.switch_to_product_iframe()
        self.click_produktdaten()
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
