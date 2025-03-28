import logging
import time
from crm import (
    init_driver, wait_for_login, switch_to_product_iframe, wait_for_product_page,
    fill_product_data, click_save, get_product_details, handle_language_popup,
    click_sonstige_preise, switch_to_frameunten, click_advanced_price_settings,
    get_prices, click_shopware6, switch_to_shopware_frame, check_and_import_product,
    click_produktdaten, dump_frame_html, get_fresh_element, switch_to_crm
)
from deepl_trans import translate_text_deepl
from sklep import (go_to_tab, switch_to_shop, select_conditional_rule, click_add_pricing_rule,
    select_pricing_rule_in_new_card, update_price_fields, update_scaled_values, update_sales_channels_selection,
    save_and_change_language, update_pricing_rule_prices, update_translated_text, search_product
)
import json

def save_product_data(product_data, filename="product_data.json"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(product_data, f, ensure_ascii=False, indent=4)
        logging.info("Dane produktu zapisane do pliku: %s", filename)
    except Exception as e:
        logging.error("Błąd przy zapisywaniu danych produktu do pliku: %s", e)

def load_product_data(filename="product_data.json"):
    """Wczytuje dane produktu z pliku JSON."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Błąd przy wczytywaniu danych z pliku {filename}: {e}")
        return {}

def display_final_info(product_data):
    print("\n--- Podsumowanie danych produktu ---")
    for key, value in product_data.items():
        print(f"{key}: {value}")
    print("--- Koniec podsumowania ---")

def main():
    driver = None
    try:
        driver = init_driver()
        wait_for_login(driver)

        product_data = load_product_data()
        print("Pobrane dane produktu:")
        for key, value in product_data.items():
            print(f"{key}: {value}")


        # Główna pętla – każda iteracja wykonuje pełną sekwencję
        while True:
            # ------------------- SEKWENCJA CRM -------------------

            logging.info("Rozpoczynam sekwencję CRM.")
            switch_to_crm(driver)
            driver.switch_to.default_content()
            switch_to_product_iframe(driver)
            wait_for_product_page(driver)
            fill_product_data(driver)
            click_save(driver)
            product_data = get_product_details(driver)
            handle_language_popup(driver, product_data)

            click_sonstige_preise(driver)
            switch_to_frameunten(driver)
            click_advanced_price_settings(driver)
            get_prices(driver, product_data)
            driver.switch_to.default_content()
            click_shopware6(driver)
            switch_to_shopware_frame(driver)
            check_and_import_product(driver)
            click_produktdaten(driver)

            logging.info("Pobrane dane produktu:")
            for key, value in product_data.items():
                logging.info("  %s: %s", key, value)
            print("Pobrane dane produktu:")
            display_final_info(product_data)
            driver.switch_to.default_content()
            # input("\nNaciśnij Enter, aby przejść do sekwencji tłumaczenia (DeepL)...")

            # ------------------- SEKWENCJA DEEPL -------------------

            logging.info("Rozpoczynam sekwencję tłumaczenia (DeepL).")
            description = product_data.get("beschreibung", "")
            if description:
                product_data["beschreibung_en"] = translate_text_deepl(description, "EN-GB")
                product_data["beschreibung_fr"] = translate_text_deepl(description, "FR")
            else:
                logging.warning("Brak opisu produktu do tłumaczenia.")
            logging.info("Dane po tłumaczeniu:")
            display_final_info(product_data)
            save_product_data(product_data)

            # input("\nNaciśnij Enter, aby przejść do wysyłania danych do sklepu...")

            # ------------------- SEKWENCJA SKLEPU -------------------
            logging.info("Rozpoczynam sekwencję wysyłania danych do sklepu.")
            switch_to_shop(driver)
            search_product(driver, product_data)
            input("\nNaciśnij Enter, aby przejść do wysyłania danych do sklepu...")
            go_to_tab(driver, "advanced pricing")
            select_conditional_rule(driver)
            click_add_pricing_rule(driver)
            select_pricing_rule_in_new_card(driver)
            #update_pricing_rule_prices(driver, product_data)
            go_to_tab(driver, "general")
            update_price_fields(driver, product_data)
            update_scaled_values(driver, product_data)
            update_sales_channels_selection(driver)
            save_and_change_language(driver, "EN")
            update_translated_text(driver, product_data, "EN")
            save_and_change_language(driver, "FR")
            update_translated_text(driver, product_data, "FR")
            save_and_change_language(driver, "DE")




            input("\nNaciśnij Enter, aby robić kolejny produkt...")
            # Resetowanie danych (opcjonalnie)
            product_data = {}
            logging.info("Rozpoczynam nową iterację sekwencji CRM.")

    except Exception as global_error:
        logging.error("Wystąpił krytyczny błąd: %s", global_error)
    finally:
        # Nie zamykamy drivera, aby można było zweryfikować wynik
        pass

if __name__ == "__main__":
    main()
