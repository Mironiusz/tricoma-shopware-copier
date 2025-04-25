import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

class ShopUploader:
    def __init__(self, driver):
        self.driver = driver

    def switch_to_shop(self):
        tabs = self.driver.window_handles
        if len(tabs) >= 2:
            self.driver.switch_to.window(tabs[1])
            logging.info("Przełączono na zakładkę Sklep.")
        else:
            logging.error("Brak otwartej drugiej zakładki (Sklep).")

    def go_to_tab(self, tab="general"):
        try:
            if tab.lower() == "general":
                logging.info("Przechodzę do zakładki General.")
                tab_element = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((
                        By.XPATH, "//a[contains(@href, '/base') and contains(@class, 'sw-product-detail__tab-general')]"
                    ))
                )
            elif tab.lower() == "advanced pricing":
                logging.info("Przechodzę do zakładki Advanced pricing.")
                tab_element = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((
                        By.XPATH, "//a[contains(@href, '/prices') and contains(@class, 'sw-product-detail__tab-advanced-prices')]"
                    ))
                )
            else:
                logging.error("Nieznana zakładka: %s", tab)
                return False
            self.driver.execute_script("arguments[0].scrollIntoView(true);", tab_element)
            self.driver.execute_script("arguments[0].click();", tab_element)
            logging.info("Przełączono na zakładkę %s.", tab)
            return True
        except Exception as e:
            logging.error("Błąd przy przełączaniu zakładki %s: %s", tab, e)
            return False

    def dump_page_source(self, file_path="page_dump.html"):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print(f"Page source zapisany do pliku: {file_path}")
        except Exception as e:
            print(f"Błąd podczas zapisywania page source: {e}")

    def update_manufacturer_selection(self):
        try:
            logging.info("Aktualizuję wybór producenta (manufacturer).")
            manufacturer_container = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.ID, "manufacturerId"))
            )
            container = manufacturer_container.find_element(
                By.CSS_SELECTOR, "div.sw-entity-single-select__selection"
            )
            current_value = container.find_element(
                By.CSS_SELECTOR, "div.sw-entity-single-select__selection-text"
            ).text.strip()

            if current_value == "Scherer Voigt GbR":
                logging.info("Producent już jest ustawiony na 'Scherer Voigt GbR'.")
                return True

            self.driver.execute_script("arguments[0].scrollIntoView(true);", container)
            self.driver.execute_script("arguments[0].click();", container)
            logging.info("Kliknięto pole producenta - otwieram listę opcji.")

            options_container = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "div.sw-select-result-list__content")
                )
            )
            options_list = options_container.find_element(
                By.CSS_SELECTOR, "ul.sw-select-result-list__item-list"
            )
            first_option = WebDriverWait(options_list, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "li.sw-select-option--0"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", first_option)
            self.driver.execute_script("arguments[0].click();", first_option)
            logging.info("Wybrano producenta: 'Scherer Voigt GbR'.")
            return True

        except Exception as e:
            logging.error("Błąd przy aktualizacji producenta: %s", e)
            return False


    def remove_rules_added(self):
        try:
            buttons = WebDriverWait(self.driver, 3).until(
                lambda d: d.find_elements(By.XPATH, "//button[.//span[text()='Delete pricing rule']]")
            )
            count = len(buttons)
            logging.info("Znaleziono %s przycisków do usunięcia reguły cenowej.", count)
            if count == 0:
                return True

            for i in range(count):
                buttons = self.driver.find_elements(By.XPATH, "//button[.//span[text()='Delete pricing rule']]")
                if buttons:
                    button_to_remove = buttons[0]
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", button_to_remove)
                    self.driver.execute_script("arguments[0].click();", button_to_remove)
                    logging.info("Kliknięto przycisk do usunięcia reguły cenowej (%s/%s).", i + 1, count)
                    time.sleep(0.5)
                else:
                    break
            return True

        except Exception as e:
            logging.info("Nie znaleziono reguł: %s", e)
            return False


    def select_conditional_rule(self, rule_text="Händler"):
        try:
            logging.info("Klikam w element wyboru reguły warunkowej.")
            selection_div = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR, "div.sw-product-detail-context-prices__empty-state-select-rule div.sw-select__selection"
                ))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", selection_div)
            self.driver.execute_script("arguments[0].click();", selection_div)
            li_option = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((
                    By.XPATH, f"//li[contains(@class, 'sw-select-result') and .//div[contains(@class, 'sw-highlight-text') and text()='{rule_text}']]"
                ))
            )
            li_option.click()
            logging.info("Wybrano regułę warunkową: %s", rule_text)
            return True
        except Exception as e:
            logging.error("Błąd przy wyborze reguły warunkowej: %s", e)
            return False

    def click_add_pricing_rule(self):
        try:
            logging.info("Klikam przycisk 'Add pricing rule'.")
            add_rule_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR, "button.sw-product-detail-context-prices__add-new-rule"
                ))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", add_rule_button)
            self.driver.execute_script("arguments[0].click();", add_rule_button)
            logging.info("Przycisk 'Add pricing rule' kliknięty.")
            return True
        except Exception as e:
            logging.error("Błąd przy klikaniu 'Add pricing rule': %s", e)
            return False

    def update_handler_preis(self, product_data):
        try:
            handler_preis = product_data.get("handler_preis")
            if handler_preis is None:
                logging.error("Brak ceny 'handler_preis' w product_data.")
                return False

            # Czekamy, aż pojawią się inputy
            inputs = WebDriverWait(self.driver, 20).until(
                lambda d: d.find_elements(By.XPATH, "//input[@name='sw-price-field-net' and @aria-label='Euro']")
            )
            logging.info("Znaleziono %s inputów do aktualizacji ceny.", len(inputs))

            # Iterujemy po inputach – modyfikujemy tylko te, które mają już wpisaną wartość
            for input_field in inputs:
                current_value = input_field.get_attribute("value")
                if current_value and current_value.strip() != "":
                    input_field.clear()
                    input_field.send_keys(str(handler_preis))
                    logging.info("Zaktualizowano input (wcześniejsza wartość: %s) na: %s", current_value, handler_preis)
                else:
                    logging.info("Pominięto input, ponieważ nie ma w nim wpisanej wartości.")

            return True

        except Exception as e:
            logging.error("Błąd przy aktualizacji ceny 'handler_preis': %s", e)
            return False


    def select_pricing_rule_in_new_card(self, rule_text="Händler Ausland"):
        try:
            logging.info("Przechodzę do pola wyboru w nowej regule cenowej.")
            rule_input = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//div[contains(@class, 'context-price') and contains(@class, 'context-price-group-1')]//input[@placeholder='Select a conditional rule...']"
                ))
            )
            rule_input.click()
            li_option = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    f"//li[contains(@class, 'sw-select-result') and .//div[contains(@class, 'sw-highlight-text') and normalize-space(text())='{rule_text}']]"
                ))
            )
            li_option.click()
            logging.info("Wybrano regułę: %s", rule_text)
            return True
        except Exception as e:
            logging.error("Błąd przy wyborze reguły w nowej karcie: %s", e)
            return False

    def update_price_fields(self, product_data):
        try:
            endkunde_price = float(product_data.get("endkunde_preis", 0))
            gross_price = round(endkunde_price * 1.19, 2)

            adjusted_price = round(gross_price / 0.05) * 0.05

            adjusted_price = round(adjusted_price, 2)

            logging.info("Obliczona cena: %s, zaokrąglona do najbliższej wielokrotności 0.05: %s", gross_price, adjusted_price)

            gross_field = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.ID, "sw-price-field-gross"))
            )
            gross_field.clear()
            gross_field.send_keys(str(adjusted_price))
            logging.info("Gross price ustawiony na: %s", adjusted_price)
            return True
        except Exception as e:
            logging.error("Błąd przy aktualizacji pola gross price: %s", e)
            return False


    def update_scaled_values(self, product_data):
        try:
            value_to_set = str(product_data.get("verpackungseinheit", "1"))
            groups = ["Händler", "Händler Ausland"]
            for group in groups:
                row_xpath = f"//tr[contains(@class, 'sw-data-grid__row') and .//span[normalize-space(text())='{group}']]"
                row = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, row_xpath))
                )
                logging.info("Znaleziono wiersz dla grupy: %s", group)
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(self.driver)
                # Minimum purchase
                min_cell = row.find_element(By.XPATH, ".//td[contains(@class, 'sw-data-grid__cell--minimumPurchase')]")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", min_cell)
                actions.double_click(min_cell).perform()
                logging.info("Podwójnie kliknięto Minimum purchase dla grupy: %s", group)
                min_input = WebDriverWait(min_cell, 10).until(
                    EC.visibility_of_element_located((By.XPATH, ".//input[@aria-label='Minimum purchase']"))
                )
                min_input.clear()
                min_input.send_keys(value_to_set)
                logging.info("Ustawiono Minimum purchase dla grupy '%s' na %s", group, value_to_set)
                # Scaling
                scaling_cell = row.find_element(By.XPATH, ".//td[contains(@class, 'sw-data-grid__cell--scaling')]")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", scaling_cell)
                actions.double_click(scaling_cell).perform()
                logging.info("Podwójnie kliknięto Scaling dla grupy: %s", group)
                scaling_input = WebDriverWait(scaling_cell, 10).until(
                    EC.visibility_of_element_located((By.XPATH, ".//input[@aria-label='Scaling']"))
                )
                scaling_input.clear()
                scaling_input.send_keys(value_to_set)
                logging.info("Ustawiono Scaling dla grupy '%s' na %s", group, value_to_set)
            return True
        except Exception as e:
            logging.error("Błąd przy aktualizacji scaled values: %s", e)
            return False

    def update_sales_channels_selection(self):
        try:
            logging.info("Aktualizuję wybór Sales Channels.")
            container = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.sw-product-category-form__visibility_field"))
            )

            actions = ActionChains(self.driver)
            while True:
                selected_items = container.find_elements(
                    By.CSS_SELECTOR, "ul.sw-select-selection-list li.sw-select-selection-list__item-holder"
                )
                if not selected_items:
                    break
                for item in selected_items:
                    try:
                        actions.move_to_element(item).perform()
                        time.sleep(0.2)
                        remove_button = item.find_element(By.CSS_SELECTOR, "button.sw-label__dismiss")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", remove_button)
                        remove_button.click()
                        logging.info("Usunięto wybrany kanał.")
                        time.sleep(0.2)
                    except Exception as e:
                        logging.error("Błąd przy usuwaniu kanału: %s", e)
            logging.info("Lista wybranych kanałów została wyczyszczona.")


            expand_button = container.find_element(
                By.CSS_SELECTOR, "div.sw-select__selection-indicators span.sw-select__select-indicator-expand"
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", expand_button)
            self.driver.execute_script("arguments[0].click();", expand_button)
            logging.info("Rozwinięto listę Sales Channels.")
            result_list = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.sw-select-result-list__content"))
            )
            options_list = result_list.find_element(By.CSS_SELECTOR, "ul.sw-select-result-list__item-list")
            option_selectors = [
                "li.sw-select-result.sw-select-option--0",
                "li.sw-select-result.sw-select-option--1",
                "li.sw-select-result.sw-select-option--2",
                "li.sw-select-result.sw-select-option--3"
            ]
            for sel in option_selectors:
                option = WebDriverWait(options_list, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, sel))
                )
                self.driver.execute_script("arguments[0].scrollIntoView(true);", option)
                self.driver.execute_script("arguments[0].click();", option)
                logging.info("Kliknięto opcję %s", sel)
                time.sleep(0.2)
            return True
        except Exception as e:
            logging.error("Błąd przy aktualizacji Sales Channels: %s", e)
            return False

    def save_and_change_language(self, lang):
        try:
            logging.info("Otwieram menu wyboru języka.")
            language_switch = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.sw-language-switch div.sw-select__selection"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", language_switch)
            self.driver.execute_script("arguments[0].click();", language_switch)
            logging.info("Menu wyboru języka otwarte.")
            if lang.upper() == "EN":
                selector = "//li[contains(@class, 'sw-select-result') and .//div[normalize-space(text())='English']]"
                option = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
            elif lang.upper() == "FR":
                selector = "//li[contains(@class, 'sw-select-result') and .//div[normalize-space(text())='Français']]"
                option = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
            elif lang.upper() == "DE":
                selector = "li.sw-select-result.sw-select-option--0"
                option = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
            else:
                logging.error("Nieznany język: %s", lang)
                return False
            self.driver.execute_script("arguments[0].scrollIntoView(true);", option)
            self.driver.execute_script("arguments[0].click();", option)
            logging.info("Wybrano język: %s", lang)
            try:
                modal_save_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "sw-language-switch-save-changes-button"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView(true);", modal_save_button)
                self.driver.execute_script("arguments[0].click();", modal_save_button)
                logging.info("Kliknięto przycisk Save w modalu.")
            except Exception as modal_error:
                logging.info("Modal o niezapisanych zmianach nie pojawił się lub nie był potrzebny")
            return True
        except Exception as e:
            logging.error("Błąd w funkcji save_and_change_language: %s", e)
            return False

    def update_translated_text(self, product_data, lang):
        try:
            name_field = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.ID, "sw-field--product-name"))
            )
            name_field.clear()
            if lang.upper() == "EN":
                new_name = product_data.get("titel_GBR", "")
                new_desc = product_data.get("beschreibung_en", "")
            elif lang.upper() == "FR":
                new_name = product_data.get("titel_FRA", "")
                new_desc = product_data.get("beschreibung_fr", "")
            else:
                logging.error("Nieznany język: %s", lang)
                return False
            name_field.send_keys(new_name)
            logging.info("Ustawiono Name na: %s", new_name)
            code_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((
                    By.XPATH, "//div[contains(@class, 'sw-text-editor-toolbar-button__icon') and .//span[contains(@class, 'icon--regular-code-xs')]]"
                ))
            )
            if "is--active" not in code_button.get_attribute("class"):
                self.driver.execute_script("arguments[0].click();", code_button)
                logging.info("Przełączono edytor na tryb kodu.")
            else:
                logging.info("Edytor już jest w trybie kodu.")
            editor_div = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.sw-code-editor__editor.ace_editor"))
            )
            self.driver.execute_script("ace.edit(arguments[0]).setValue(arguments[1]);", editor_div, new_desc)
            logging.info("Ustawiono Description dla języka %s.", lang)
            return True
        except Exception as e:
            logging.error("Błąd przy aktualizacji tłumaczonego tekstu: %s", e)
            return False

    def search_product(self, product_data):
        try:
            search_input = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input.sw-search-bar__input"))
            )
            search_input.clear()
            artikelnummer = product_data.get("artikelnummer", "")
            if not artikelnummer:
                logging.error("Brak numeru artykułu w product_data.")
                return False
            search_input.send_keys(artikelnummer)
            logging.info("Wpisano numer artykułu: %s", artikelnummer)
            time.sleep(1)
            result_link = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((
                    By.XPATH, f"//a[contains(@class, 'sw-search-bar-item__link') and .//span[contains(text(), '{artikelnummer}')]]"
                ))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", result_link)
            self.driver.execute_script("arguments[0].click();", result_link)
            logging.info("Kliknięto wynik wyszukiwania dla numeru artykułu: %s", artikelnummer)
            return True
        except Exception as e:
            logging.error("Błąd przy wyszukiwaniu produktu: %s", e)
            return False

    def go_to_shop(self, product_data):
        self.switch_to_shop()
        self.search_product(product_data)

    def run_sequence(self, product_data):
        self.switch_to_shop()
        self.go_to_tab("advanced pricing")
        self.remove_rules_added()
        self.select_conditional_rule()
        self.click_add_pricing_rule()
        self.select_pricing_rule_in_new_card()
        self.update_handler_preis(product_data)
        self.go_to_tab("general")
        self.update_manufacturer_selection()
        self.update_price_fields(product_data)
        self.update_scaled_values(product_data)
        self.update_sales_channels_selection()
        self.save_and_change_language("EN")
        self.update_translated_text(product_data, "EN")
        self.save_and_change_language("FR")
        self.update_translated_text(product_data, "FR")
        self.save_and_change_language("DE")
