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
            logging.info("Switched to Shop tab.")
        else:
            logging.error("No second tab open (Shop).")

    def go_to_tab(self, tab="general"):
        try:
            if tab.lower() == "general":
                logging.info("Navigating to General tab.")
                tab_element = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((
                        By.XPATH, "//a[contains(@href, '/base') and contains(@class, 'sw-product-detail__tab-general')]"
                    ))
                )
            elif tab.lower() == "advanced pricing":
                logging.info("Navigating to Advanced pricing tab.")
                tab_element = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((
                        By.XPATH, "//a[contains(@href, '/prices') and contains(@class, 'sw-product-detail__tab-advanced-prices')]"
                    ))
                )
            else:
                logging.error("Unknown tab: %s", tab)
                return False
            self.driver.execute_script("arguments[0].scrollIntoView(true);", tab_element)
            self.driver.execute_script("arguments[0].click();", tab_element)
            logging.info("Switched to tab %s.", tab)
            return True
        except Exception as e:
            logging.error("Error switching to tab %s: %s", tab, e)
            return False

    def dump_page_source(self, file_path="page_dump.html"):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print(f"Page source saved to file: {file_path}")
        except Exception as e:
            print(f"Error saving page source: {e}")

    def update_manufacturer_selection(self):
        try:
            logging.info("Updating manufacturer selection.")
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
                logging.info("Manufacturer already set to 'Scherer Voigt GbR'.")
                return True

            self.driver.execute_script("arguments[0].scrollIntoView(true);", container)
            self.driver.execute_script("arguments[0].click();", container)
            logging.info("Clicked manufacturer field to open options.")

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
            logging.info("Selected manufacturer: 'Scherer Voigt GbR'.")
            return True

        except Exception as e:
            logging.error("Error updating manufacturer: %s", e)
            return False

    def remove_rules_added(self):
        try:
            buttons = WebDriverWait(self.driver, 3).until(
                lambda d: d.find_elements(By.XPATH, "//button[.//span[text()='Delete pricing rule']]")
            )
            count = len(buttons)
            logging.info("Found %s buttons to delete pricing rules.", count)
            if count == 0:
                return True

            for i in range(count):
                buttons = self.driver.find_elements(By.XPATH, "//button[.//span[text()='Delete pricing rule']]")
                if buttons:
                    button_to_remove = buttons[0]
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", button_to_remove)
                    self.driver.execute_script("arguments[0].click();", button_to_remove)
                    logging.info("Clicked delete pricing rule button (%s/%s).", i + 1, count)
                    time.sleep(0.5)
                else:
                    break
            return True

        except Exception as e:
            logging.info("No pricing rules found: %s", e)
            return False

    def select_conditional_rule(self, rule_text="Händler"):
        try:
            logging.info("Clicking conditional rule selector.")
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
            logging.info("Selected conditional rule: %s", rule_text)
            return True
        except Exception as e:
            logging.error("Error selecting conditional rule: %s", e)
            return False

    def click_add_pricing_rule(self):
        try:
            logging.info("Clicking 'Add pricing rule' button.")
            add_rule_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR, "button.sw-product-detail-context-prices__add-new-rule"
                ))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", add_rule_button)
            self.driver.execute_script("arguments[0].click();", add_rule_button)
            logging.info("'Add pricing rule' button clicked.")
            return True
        except Exception as e:
            logging.error("Error clicking 'Add pricing rule': %s", e)
            return False

    def update_handler_preis(self, product_data):
        try:
            handler_preis = product_data.get("handler_preis")
            if handler_preis is None:
                logging.error("No 'handler_preis' in product_data.")
                return False

            inputs = WebDriverWait(self.driver, 20).until(
                lambda d: d.find_elements(By.XPATH, "//input[@name='sw-price-field-net' and @aria-label='Euro']")
            )
            logging.info("Found %s inputs to update price.", len(inputs))

            for input_field in inputs:
                current_value = input_field.get_attribute("value")
                if current_value and current_value.strip() != "":
                    input_field.clear()
                    input_field.send_keys(str(handler_preis))
                    logging.info("Updated input (previous value: %s) to: %s", current_value, handler_preis)
                else:
                    logging.info("Skipped input with no existing value.")

            return True

        except Exception as e:
            logging.error("Error updating 'handler_preis': %s", e)
            return False

    def select_pricing_rule_in_new_card(self, rule_text="Händler Ausland"):
        try:
            logging.info("Selecting rule in new pricing card.")
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
            logging.info("Selected rule: %s", rule_text)
            return True
        except Exception as e:
            logging.error("Error selecting rule in new card: %s", e)
            return False

    def update_price_fields(self, product_data):
        try:
            endkunde_price = float(product_data.get("endkunde_preis", 0))
            gross_price = round(endkunde_price * 1.19, 2)
            adjusted_price = round(gross_price / 0.05) * 0.05
            adjusted_price = round(adjusted_price, 2)
            logging.info("Calculated gross price: %s, rounded to nearest 0.05: %s", gross_price, adjusted_price)

            gross_field = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.ID, "sw-price-field-gross"))
            )
            gross_field.clear()
            gross_field.send_keys(str(adjusted_price))
            logging.info("Gross price set to: %s", adjusted_price)
            return True
        except Exception as e:
            logging.error("Error updating gross price field: %s", e)
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
                logging.info("Found row for group: %s", group)
                actions = ActionChains(self.driver)
                min_cell = row.find_element(By.XPATH, ".//td[contains(@class, 'sw-data-grid__cell--minimumPurchase')]")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", min_cell)
                actions.double_click(min_cell).perform()
                logging.info("Double-clicked Minimum purchase for group: %s", group)
                min_input = WebDriverWait(min_cell, 10).until(
                    EC.visibility_of_element_located((By.XPATH, ".//input[@aria-label='Minimum purchase']"))
                )
                min_input.clear()
                min_input.send_keys(value_to_set)
                logging.info("Set Minimum purchase for '%s' to %s", group, value_to_set)

                scaling_cell = row.find_element(By.XPATH, ".//td[contains(@class, 'sw-data-grid__cell--scaling')]")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", scaling_cell)
                actions.double_click(scaling_cell).perform()
                logging.info("Double-clicked Scaling for group: %s", group)
                scaling_input = WebDriverWait(scaling_cell, 10).until(
                    EC.visibility_of_element_located((By.XPATH, ".//input[@aria-label='Scaling']"))
                )
                scaling_input.clear()
                scaling_input.send_keys(value_to_set)
                logging.info("Set Scaling for '%s' to %s", group, value_to_set)
            return True
        except Exception as e:
            logging.error("Error updating scaled values: %s", e)
            return False

    def update_sales_channels_selection(self):
        try:
            logging.info("Updating Sales Channels selection.")
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
                        logging.info("Removed selected channel.")
                        time.sleep(0.2)
                    except Exception as e:
                        logging.error("Error removing channel: %s", e)
            logging.info("Cleared all selected channels.")

            expand_button = container.find_element(
                By.CSS_SELECTOR, "div.sw-select__selection-indicators span.sw-select__select-indicator-expand"
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", expand_button)
            self.driver.execute_script("arguments[0].click();", expand_button)
            logging.info("Expanded Sales Channels list.")
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
                logging.info("Clicked option %s", sel)
                time.sleep(0.2)
            return True
        except Exception as e:
            logging.error("Error updating Sales Channels: %s", e)
            return False

    def save_and_change_language(self, lang):
        try:
            logging.info("Opening language switch menu.")
            language_switch = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.sw-language-switch div.sw-select__selection"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", language_switch)
            self.driver.execute_script("arguments[0].click();", language_switch)
            logging.info("Language switch menu opened.")
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
                logging.error("Unknown language: %s", lang)
                return False
            self.driver.execute_script("arguments[0].scrollIntoView(true);", option)
            self.driver.execute_script("arguments[0].click();", option)
            logging.info("Selected language: %s", lang)
            try:
                modal_save_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "sw-language-switch-save-changes-button"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView(true);", modal_save_button)
                self.driver.execute_script("arguments[0].click();", modal_save_button)
                logging.info("Clicked Save button in modal.")
            except Exception:
                logging.info("No save-changes modal appeared or was not needed.")
            return True
        except Exception as e:
            logging.error("Error in save_and_change_language: %s", e)
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
                logging.error("Unknown language: %s", lang)
                return False
            name_field.send_keys(new_name)
            logging.info("Set Name to: %s", new_name)
            code_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((
                    By.XPATH, "//div[contains(@class, 'sw-text-editor-toolbar-button__icon') and .//span[contains(@class, 'icon--regular-code-xs')]]"
                ))
            )
            if "is--active" not in code_button.get_attribute("class"):
                self.driver.execute_script("arguments[0].click();", code_button)
                logging.info("Switched editor to code mode.")
            else:
                logging.info("Editor already in code mode.")
            editor_div = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.sw-code-editor__editor.ace_editor"))
            )
            self.driver.execute_script("ace.edit(arguments[0]).setValue(arguments[1]);", editor_div, new_desc)
            logging.info("Set Description for language %s.", lang)
            return True
        except Exception as e:
            logging.error("Error updating translated text: %s", e)
            return False

    def search_product(self, product_data):
        try:
            search_input = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input.sw-search-bar__input"))
            )
            search_input.clear()
            artikelnummer = product_data.get("artikelnummer", "")
            if not artikelnummer:
                logging.error("No article number in product_data.")
                return False
            search_input.send_keys(artikelnummer)
            logging.info("Entered article number: %s", artikelnummer)
            time.sleep(1)
            result_link = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((
                    By.XPATH, f"//a[contains(@class, 'sw-search-bar-item__link') and .//span[contains(text(), '{artikelnummer}')]]"
                ))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", result_link)
            self.driver.execute_script("arguments[0].click();", result_link)
            logging.info("Clicked search result for article number: %s", artikelnummer)
            return True
        except Exception as e:
            logging.error("Error searching for product: %s", e)
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
