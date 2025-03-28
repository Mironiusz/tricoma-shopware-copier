from crm_downloader import CRMDownloader
from shop_uploader import ShopUploader
from translator import Translator

class ProcessFacade:
    def __init__(self, driver, config):
        self.driver = driver
        self.config = config
        self.crm_downloader = CRMDownloader(driver)
        self.shop_uploader = ShopUploader(driver)
        self.translator = Translator(config)

    def run_full_process(self):
        # Download z CRM
        product_data = self.crm_downloader.run_sequence()
        self.crm_downloader.save_product_data(product_data)
        # Tłumaczenie
        product_data = self.translator.translate_product(product_data)
        self.crm_downloader.display_final_info(product_data)
        self.crm_downloader.save_product_data(product_data)
        # Upload do sklepu
        self.shop_uploader.run_sequence(product_data)
        return product_data
