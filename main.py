import logging
import json
from driver_initializer import DriverInitializer
from facade import ProcessFacade
from interface import UserInterface

def load_config(filename="config.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except Exception as e:
        logging.error("Błąd przy wczytywaniu konfiguracji: %s", e)
        return {}

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    config = load_config()
    driver_init = DriverInitializer(config)
    driver = driver_init.init_driver()
    facade = ProcessFacade(driver, config)
    # Logowanie w CRM i Sklepie
    crm_url = config.get("CRM_URL", "https://default-crm-url")
    shop_url = config.get("SHOP_URL", "https://default-shop-url")
    facade.crm_downloader.wait_for_login(crm_url, shop_url)
    ui = UserInterface(facade)
    while True:
        ui.execute_choice()

if __name__ == "__main__":
    main()
