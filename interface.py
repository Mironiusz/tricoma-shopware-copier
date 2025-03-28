import logging

class UserInterface:
    def __init__(self, facade):
        self.facade = facade

    def show_menu(self):
        print("Wybierz operację:")
        print("1 - Pełny proces (Download, Translate, Upload)")
        print("2 - Tylko Download")
        print("3 - Tylko Translate")
        print("4 - Tylko Upload")
        choice = input("Wprowadź wybór (1/2/3/4): ")
        return choice

    def execute_choice(self):
        choice = self.show_menu()
        if choice == "1":
            product_data = self.facade.run_full_process()
        elif choice == "2":
            product_data = self.facade.crm_downloader.run_sequence()
            self.facade.crm_downloader.save_product_data(product_data)
        elif choice == "3":
            product_data = self.facade.crm_downloader.load_product_data()
            product_data = self.facade.translator.translate_product(product_data)
            self.facade.crm_downloader.display_final_info(product_data)
            self.facade.crm_downloader.save_product_data(product_data)
        elif choice == "4":
            product_data = self.facade.crm_downloader.load_product_data()
            self.facade.shop_uploader.run_sequence(product_data)
        else:
            logging.error("Nieprawidłowy wybór.")
