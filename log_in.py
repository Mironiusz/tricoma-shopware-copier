import logging
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

class LogIn:
    def __init__(self, driver, tricoma, shopware):
        self.driver = driver
        self.tricoma = tricoma
        self.shopware = shopware

    def select_tricoma_login(self):
        print("Dostępni użytkownicy Tricoma:")
        users = list(self.tricoma.items())
        for idx, (key, credentials) in enumerate(users, start=1):
            print(f"{idx}: {key}")
        user_id = input("Wybierz użytkownika Tricoma: ")
        _, selected_credentials = users[int(user_id) - 1]
        return selected_credentials.get("USERNAME"), selected_credentials.get("PASSWORD")


    def select_shopware_login(self):
        print("Dostępni użytkownicy Shopware:")
        users = list(self.shopware.items())
        for idx, (key, credentials) in enumerate(users, start=1):
            print(f"{idx}: {key}")
        user_id = input("Wybierz użytkownika Shopware: ")
        _, selected_credentials = users[int(user_id) - 1]
        return selected_credentials.get("USERNAME"), selected_credentials.get("PASSWORD")


    def log_in_tricoma(self, tricoma_credentials):
        login, password = tricoma_credentials
        logging.info("Przełączam się na tricomę.")
        tabs = self.driver.window_handles
        self.driver.switch_to.window(tabs[0])
        self.driver.switch_to.default_content()
        logging.info("Przełączam się na iframe do logowania.")
        iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "contentframe"))
        )
        self.driver.switch_to.frame(iframe)
        logging.info("Przełączono na iframe logowania.")
        logging.info("Wpisuję dane logowania do Tricoma.")

        try:
            user_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "benutzer"))
            )
            user_field.clear()
            user_field.send_keys(login)
            logging.info("Pole username ustawione.")
        except Exception as e:
            logging.error("Błąd przy uzupełnianiu pola username: %s", e)

        try:
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "passwort"))
            )
            password_field.clear()
            password_field.send_keys(password)
            logging.info("Pole password ustawione.")
        except Exception as e:
            logging.error("Błąd przy uzupełnianiu pola password: %s", e)

        try:
            logging.info("Klikam przycisk zapisu.")
            save_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input.login[name='submitbuton']"))
            )
            save_button.click()
            logging.info("Przycisk zapisu kliknięty.")
        except Exception as e:
            logging.error("Błąd przy klikaniu przycisku zapisu: %s", e)


    def log_in_shopware(self, shopware_credentials):
        login, password = shopware_credentials
        logging.info("Przełączam się na shopware.")
        tabs = self.driver.window_handles
        self.driver.switch_to.window(tabs[1])
        self.driver.switch_to.default_content()

        try:
            user_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "sw-field--username"))
            )
            user_field.clear()
            user_field.send_keys(login)
            logging.info("Pole username ustawione.")
        except Exception as e:
            logging.error("Błąd przy uzupełnianiu pola username: %s", e)

        try:
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "sw-field--password"))
            )
            password_field.clear()
            password_field.send_keys(password)
            logging.info("Pole password ustawione.")
        except Exception as e:
            logging.error("Błąd przy uzupełnianiu pola password: %s", e)

        try:
            logging.info("Klikam przycisk zapisu.")
            save_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.sw-login__login-action"))
            )
            save_button.click()
            logging.info("Przycisk zapisu kliknięty.")
        except Exception as e:
            logging.error("Błąd przy klikaniu przycisku zapisu: %s", e)


    def log_in(self):
        try:
            shopware_credentials = self.select_shopware_login()
            self.log_in_shopware(shopware_credentials)
            tricoma_credentials = self.select_tricoma_login()
            self.log_in_tricoma(tricoma_credentials)
        except Exception as e:
            logging.error("Błąd logowania: %s", e)
            raise