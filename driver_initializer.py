import logging
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

class DriverInitializer:
    def __init__(self, config):
        self.config = config

    def init_driver(self):
        logging.info("Initializing Firefox with geckodriver and dedicated profile.")
        service = Service(self.config["GECKODRIVER_PATH"])
        options = Options()
        options.binary_location = self.config["FIREFOX_BINARY"]
        options.profile = self.config["FIREFOX_PROFILE"]
        driver = webdriver.Firefox(service=service, options=options)
        return driver
