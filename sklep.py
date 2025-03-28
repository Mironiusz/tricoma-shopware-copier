import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def switch_to_shop(driver):
    """
    Przełącza widok na drugą zakładkę (Sklep).
    """
    tabs = driver.window_handles
    if len(tabs) >= 2:
        driver.switch_to.window(tabs[1])
        logging.info("Przełączono na zakładkę Sklep.")
    else:
        logging.error("Brak otwartej drugiej zakładki (Sklep).")

def go_to_tab(driver, tab="general"):
    """
    Przełącza widok na zakładkę określoną przez parametr tab.

    Parametry:
      driver: instancja Selenium WebDriver.
      tab: Nazwa zakładki – np. "General" lub "Advanced pricing".
    """
    try:
        if tab.lower() == "general":
            logging.info("Przechodzę do zakładki General.")
            tab_element = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((
                    By.XPATH, "//a[contains(@href, '/base') and contains(@class, 'sw-product-detail__tab-general')]"
                ))
            )
        elif tab.lower() == "advanced pricing":
            logging.info("Przechodzę do zakładki Advanced pricing.")
            tab_element = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((
                    By.XPATH, "//a[contains(@href, '/prices') and contains(@class, 'sw-product-detail__tab-advanced-prices')]"
                ))
            )
        else:
            logging.error("Nieznana zakładka: %s", tab)
            return False

        # Klikamy wybrany element
        driver.execute_script("arguments[0].scrollIntoView(true);", tab_element)
        driver.execute_script("arguments[0].click();", tab_element)
        logging.info("Przełączono na zakładkę %s.", tab)
        return True
    except Exception as e:
        logging.error("Błąd przy przełączaniu zakładki %s: %s", tab, e)
        return False
def select_conditional_rule(driver, rule_text="Händler"):
    """
    Klika w pole wyboru reguły warunkowej i wybiera opcję, której tekst to rule_text.

    Parametry:
      driver: instancja Selenium WebDriver.
      rule_text: Tekst reguły, którą chcemy wybrać (domyślnie "Händler").
    """
    try:
        logging.info("Klikam w element 'sw-select__selection' w pustym stanie reguły.")
        selection_div = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, "div.sw-product-detail-context-prices__empty-state-select-rule div.sw-select__selection"
            ))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", selection_div)
        driver.execute_script("arguments[0].click();", selection_div)
        logging.info("Kliknięto element 'sw-select__selection'.")

        # Czekamy na pojawienie się opcji – szukamy elementu li, który zawiera div ze wskazanym tekstem
        li_option = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((
                By.XPATH, f"//li[contains(@class, 'sw-select-result') and .//div[contains(@class, 'sw-highlight-text') and text()='{rule_text}']]"
            ))
        )
        li_option.click()
        logging.info("Wybrano regułę warunkową: %s", rule_text)
        return True
    except Exception as e:
        logging.error("Błąd podczas wyboru reguły warunkowej: %s", e)
        return False

def click_add_pricing_rule(driver):
    """
    Kliknie przycisk "Add pricing rule" w sekcji Advanced pricing.
    """
    try:
        logging.info("Klikam przycisk 'Add pricing rule'.")
        add_rule_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, "button.sw-product-detail-context-prices__add-new-rule"
            ))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", add_rule_button)
        driver.execute_script("arguments[0].click();", add_rule_button)
        logging.info("Kliknięto przycisk 'Add pricing rule'.")
        return True
    except Exception as e:
        logging.error("Błąd przy klikaniu 'Add pricing rule': %s", e)
        return False


def select_pricing_rule_in_new_card(driver, rule_text="Händler Ausland"):
    """
    W nowo otwartej karcie (nowa reguła cenowa) klika pole wyboru i wybiera opcję z podanym tekstem.

    Parametry:
      driver: instancja Selenium WebDriver.
      rule_text: Tekst opcji do wybrania (domyślnie "Händler Ausland").
    """
    try:
        logging.info("Przechodzę do pola wyboru w nowej regule cenowej.")
        # Wyszukujemy input w obrębie kontenera nowej reguły – dostosuj XPath, jeśli potrzeba
        rule_input = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//div[contains(@class, 'context-price') and contains(@class, 'context-price-group-1')]//input[@placeholder='Select a conditional rule...']"
            ))
        )
        rule_input.click()
        logging.info("Kliknięto pole wyboru w nowej regule cenowej.")

        # Teraz wyszukujemy element li z odpowiednim tekstem
        li_option = WebDriverWait(driver, 20).until(
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

def update_pricing_rule_prices(driver, product_data):
    """
    Dla reguł dotyczących grup 'Händler' oraz 'Händler Ausland' ustawia wartość pola gross price
    na wartość z product_data["handler_preis"].

    Parametry:
      driver: instancja Selenium WebDriver.
      product_data: słownik, który musi zawierać klucz "handler_preis".
    """
    try:
        price = str(product_data.get("handler_preis", ""))
        if not price:
            logging.error("Brak wartości handler_preis w product_data.")
            return False

        logging.info("Aktualizuję gross price na wartość: %s", price)

        # Pobieramy wszystkie karty reguł cenowych
        cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'sw-card') and .//div[contains(@class, 'sw-card__title')]]")
        # Definiujemy grupy, dla których aktualizujemy cenę
        groups = ["Händler", "Händler Ausland"]
        for group in groups:
            found = False
            for card in cards:
                try:
                    # Pobieramy tytuł karty
                    title_elem = card.find_element(By.XPATH, ".//div[contains(@class, 'sw-card__title')]")
                    title = title_elem.text.strip()
                    if group in title:
                        # Upewniamy się, że karta jest widoczna
                        driver.execute_script("arguments[0].scrollIntoView(true);", card)
                        # Szukamy inputa w kontekście tej karty – wyszukujemy input, którego placeholder i aria-label odpowiadają
                        gross_input = card.find_element(
                            By.XPATH,
                            ".//input[@placeholder='Enter gross price...' and @aria-label='Euro']"
                        )
                        # Jeśli input jest disabled, usuniemy ten atrybut (jeśli jest to bezpieczne w Twoim przypadku)
                        driver.execute_script("arguments[0].removeAttribute('disabled');", gross_input)
                        gross_input.clear()
                        gross_input.send_keys(price)
                        logging.info("Zmieniono gross price dla grupy '%s' na %s", group, price)
                        found = True
                        break
                except Exception as inner_e:
                    logging.error("Błąd przy przetwarzaniu karty: %s", inner_e)
            if not found:
                logging.error("Nie znaleziono karty dla grupy '%s'", group)
        return True
    except Exception as e:
        logging.error("Błąd przy aktualizacji handler price: %s", e)
        return False

def dump_frame_html(driver, file_path="frame_content.html"):
    html = driver.page_source
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    logging.info("Zrzut HTML do pliku %s wykonany.", file_path)


import time

def update_price_fields(driver, product_data):
    """
    Aktualizuje pole gross price:
      - Pobiera product_data["endkunde_preis"],
      - mnoży wartość przez 1.19,
      - zaokrągla wynik do dwóch miejsc po przecinku,
      - wpisuje wynik do pola gross price (id="sw-price-field-gross").

    Parametry:
      driver: instancja Selenium WebDriver.
      product_data: słownik zawierający klucz "endkunde_preis".

    Zwraca:
      True, jeśli operacja przebiegła pomyślnie, False w przypadku błędu.
    """
    try:
        # Pobierz cenę z product_data i przelicz gross price
        endkunde_price = float(product_data.get("endkunde_preis", 0))
        gross_price = round(endkunde_price * 1.19, 2)
        logging.info("Obliczona gross price: %s (endkunde_preis %s * 1.19)", gross_price, endkunde_price)

        # Znajdź pole gross price i ustaw nową wartość
        gross_field = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "sw-price-field-gross"))
        )
        gross_field.clear()
        gross_field.send_keys(str(gross_price))
        logging.info("Gross price ustawiony na: %s", gross_price)
        return True
    except Exception as e:
        logging.error("Błąd przy aktualizacji pola gross price: %s", e)
        return False


def update_scaled_values(driver, product_data):
    """
    Dla wierszy odpowiadających grupom 'Händler' oraz 'Händler Ausland'
    w tabeli Scaling:
      - podwójnie klika komórkę Minimum purchase, aby otworzyć tryb edycji,
        następnie ustawia wartość na product_data["verpackungseinheit"].
      - podwójnie klika komórkę Scaling, aby otworzyć tryb edycji,
        następnie ustawia wartość na product_data["verpackungseinheit"].

    Zakładamy, że wartość, którą chcemy ustawić, znajduje się w product_data["verpackungseinheit"].
    """
    try:
        value_to_set = str(product_data.get("verpackungseinheit", "1"))
        groups = ["Händler", "Händler Ausland"]

        for group in groups:
            # Znajdź wiersz, w którym Customer group ma dokładnie wartość group.
            row_xpath = f"//tr[contains(@class, 'sw-data-grid__row') and .//span[normalize-space(text())='{group}']]"
            row = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, row_xpath))
            )
            logging.info("Znaleziono wiersz dla grupy: %s", group)

            actions = ActionChains(driver)

            # --- Aktualizacja Minimum purchase ---
            # Znajdź komórkę Minimum purchase w tym wierszu.
            min_cell = row.find_element(By.XPATH, ".//td[contains(@class, 'sw-data-grid__cell--minimumPurchase')]")
            # Przewiń komórkę do widoku.
            driver.execute_script("arguments[0].scrollIntoView(true);", min_cell)
            # Wykonaj double click.
            actions.double_click(min_cell).perform()
            logging.info("Podwójnie kliknięto komórkę Minimum purchase dla grupy: %s", group)
            # Po double click powinno pojawić się pole edycji z aria-label "Minimum purchase".
            min_input = WebDriverWait(min_cell, 10).until(
                EC.visibility_of_element_located((By.XPATH, ".//input[@aria-label='Minimum purchase']"))
            )
            min_input.clear()
            min_input.send_keys(value_to_set)
            logging.info("Ustawiono Minimum purchase dla grupy '%s' na %s", group, value_to_set)

            # --- Aktualizacja Scaling ---
            # Znajdź komórkę Scaling w tym samym wierszu.
            scaling_cell = row.find_element(By.XPATH, ".//td[contains(@class, 'sw-data-grid__cell--scaling')]")
            # Przewiń komórkę do widoku.
            driver.execute_script("arguments[0].scrollIntoView(true);", scaling_cell)
            actions.double_click(scaling_cell).perform()
            logging.info("Podwójnie kliknięto komórkę Scaling dla grupy: %s", group)
            # Czekamy, aż pojawi się input z aria-label "Scaling".
            scaling_input = WebDriverWait(scaling_cell, 10).until(
                EC.visibility_of_element_located((By.XPATH, ".//input[@aria-label='Scaling']"))
            )
            scaling_input.clear()
            scaling_input.send_keys(value_to_set)
            logging.info("Ustawiono Scaling dla grupy '%s' na %s", group, value_to_set)

        return True
    except Exception as e:
        logging.error("Błąd przy aktualizacji wartości scaling/minimum purchase: %s", e)
        return False

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def update_sales_channels_selection(driver):
    """
    Rozwija listę Sales Channels (sekcja widoczna w formularzu) i kolejno wybiera:
      - opcję "02 - NOI-SHOP B2B - DE" (element o klasie sw-select-option--1),
      - opcję "03 - NOI-SHOP B2B - EN" (element o klasie sw-select-option--2),
      - opcję "04 - NOI-SHOP B2B - FR" (element o klasie sw-select-option--3).

    Funkcja ogranicza wyszukiwanie do sekcji, której nadrzędnym kontenerem jest
    div.sw-product-category-form__visibility_field.
    """
    try:
        logging.info("Aktualizuję wybór Sales Channels.")
        # Znajdź główny kontener sekcji Sales Channels
        container = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.sw-product-category-form__visibility_field")
            )
        )

        # W obrębie kontenera, znajdź ikonę rozwijania listy
        expand_button = container.find_element(
            By.CSS_SELECTOR, "div.sw-select__selection-indicators span.sw-select__select-indicator-expand"
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", expand_button)
        driver.execute_script("arguments[0].click();", expand_button)
        logging.info("Rozwinięto listę Sales Channels.")

        # Teraz znajdź kontener z wynikami – ograniczamy wyszukiwanie do tej sekcji
        result_list = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.sw-select-result-list__content")
            )
        )
        options_list = result_list.find_element(By.CSS_SELECTOR, "ul.sw-select-result-list__item-list")

        # Definiujemy selektory dla kolejnych opcji do kliknięcia
        option_selectors = [
            "li.sw-select-result.sw-select-option--1",  # 02 - NOI-SHOP B2B - DE
            "li.sw-select-result.sw-select-option--2",  # 03 - NOI-SHOP B2B - EN
            "li.sw-select-result.sw-select-option--3"   # 04 - NOI-SHOP B2B - FR
        ]

        for sel in option_selectors:
            option = WebDriverWait(options_list, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, sel))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", option)
            driver.execute_script("arguments[0].click();", option)
            logging.info("Kliknięto opcję %s", sel)
            time.sleep(0.2)

        return True
    except Exception as e:
        logging.error("Błąd przy aktualizacji Sales Channels: %s", e)
        return False

def save_and_change_language(driver, lang):
    """
    Otwiera menu wyboru języka w smart barze i wybiera język podany w parametrze lang (DE, EN lub FR).
    Jeśli pojawi się modal o niezapisanych zmianach, klika przycisk Save w tym modalu.

    Parametry:
      driver: instancja Selenium WebDriver.
      lang: skrót języka, np. "DE", "EN" lub "FR".
    """
    try:
        logging.info("Otwieram menu wyboru języka.")
        # Kliknij element otwierający menu wyboru języka
        language_switch = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.sw-language-switch div.sw-select__selection"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", language_switch)
        driver.execute_script("arguments[0].click();", language_switch)
        logging.info("Menu wyboru języka otwarte.")

        if lang.upper() == "EN":
            # Dla angielskiego używamy XPath, aby trafić dokładnie w element zawierający "English"
            selector = "//li[contains(@class, 'sw-select-result') and .//div[normalize-space(text())='English']]"
            option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
        elif lang.upper() == "FR":
            # Dla francuskiego używamy XPath, aby trafić dokładnie w element zawierający "Français"
            selector = "//li[contains(@class, 'sw-select-result') and .//div[normalize-space(text())='Français']]"
            option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
        elif lang.upper() == "DE":
            # Dla niemieckiego możemy użyć selektora CSS, jeśli jest wystarczająco precyzyjny
            selector = "li.sw-select-result.sw-select-option--0"
            option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
        else:
            logging.error("Nieznany język: %s", lang)
            return False

        driver.execute_script("arguments[0].scrollIntoView(true);", option)
        driver.execute_script("arguments[0].click();", option)
        logging.info("Wybrano język: %s", lang)

        # Jeśli pojawi się modal z komunikatem o niezapisanych zmianach, kliknij przycisk Save w modal
        try:
            modal_save_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "sw-language-switch-save-changes-button"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", modal_save_button)
            driver.execute_script("arguments[0].click();", modal_save_button)
            logging.info("W modalu kliknięto przycisk Save.")
        except Exception as modal_error:
            logging.info("Modal o niezapisanych zmianach nie pojawił się lub nie był potrzebny")

        return True
    except Exception as e:
        logging.error("Błąd w funkcji save_and_change_language: %s", e)
        return False

def update_translated_text(driver, product_data, lang):
    """
    Ustawia przetłumaczony tytuł oraz opis w formularzu produktu.

    Dla języka "EN" wstawia:
      - tytuł z product_data["titel_GBR"]
      - opis z product_data["beschreibung_en"]

    Dla języka "FR" wstawia:
      - tytuł z product_data["titel_FRA"]
      - opis z product_data["beschreibung_fr"]

    Parametry:
      driver: instancja Selenium WebDriver.
      product_data: słownik z danymi produktu.
      lang: kod języka ("EN" lub "FR").
    """
    try:
        # Ustawienie pola "Name"
        name_field = WebDriverWait(driver, 20).until(
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

        # Przełączanie edytora na tryb kodu (HTML)
        code_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((
                By.XPATH, "//div[contains(@class, 'sw-text-editor-toolbar-button__icon') and .//span[contains(@class, 'icon--regular-code-xs')]]"
            ))
        )
        if "is--active" not in code_button.get_attribute("class"):
            driver.execute_script("arguments[0].click();", code_button)
            logging.info("Przełączono edytor na tryb kodu.")
        else:
            logging.info("Edytor już jest w trybie kodu.")

        # Znajdź element edytora Ace – zawierający klasy: sw-code-editor__editor ace_editor
        editor_div = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.sw-code-editor__editor.ace_editor"))
        )

        # Ustaw zawartość edytora przy użyciu API Ace.
        driver.execute_script("ace.edit(arguments[0]).setValue(arguments[1]);", editor_div, new_desc)
        logging.info("Ustawiono Description dla języka %s.", lang)
        return True

    except Exception as e:
        logging.error("Błąd przy aktualizacji tłumaczonego tekstu: %s", e)
        return False

def search_product(driver, product_data):
    """
    Wyszukuje produkt w sklepie na podstawie numeru artykułu.

    Wprowadza wartość z product_data["artikelnummer"] do pola wyszukiwania,
    czeka chwilę na wyniki, a następnie klika pierwszy wynik, który zawiera numer artykułu.

    Parametry:
      driver: instancja Selenium WebDriver.
      product_data: słownik z danymi produktu, musi zawierać klucz "artikelnummer".
    """
    try:
        # Znajdź pole wyszukiwania i wpisz numer artykułu
        search_input = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input.sw-search-bar__input"))
        )
        search_input.clear()
        artikelnummer = product_data.get("artikelnummer", "")
        if not artikelnummer:
            logging.error("Brak numeru artykułu w product_data.")
            return False
        search_input.send_keys(artikelnummer)
        logging.info("Wpisano numer artykułu: %s", artikelnummer)

        # Odczekaj chwilę, aby wyniki się załadowały (np. 1 sekundę)
        time.sleep(1)

        # Znajdź pierwszy wynik, który zawiera numer artykułu.
        # Szukamy elementu <a> z klasą 'sw-search-bar-item__link' zawierającego tekst numeru artykułu.
        result_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((
                By.XPATH, f"//a[contains(@class, 'sw-search-bar-item__link') and .//span[contains(text(), '{artikelnummer}')]]"
            ))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", result_link)
        driver.execute_script("arguments[0].click();", result_link)
        logging.info("Kliknięto wynik wyszukiwania dla numeru artykułu: %s", artikelnummer)
        return True

    except Exception as e:
        logging.error("Błąd przy wyszukiwaniu produktu: %s", e)
        return False
