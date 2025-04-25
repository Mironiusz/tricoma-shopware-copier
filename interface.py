import logging

class UserInterface:
    def __init__(self, facade):
        self.facade = facade

    def show_menu(self):
        print("Wybierz operację:")
        print("1 - Pełny proces (Download, Translate, Upload)")
        print("2 - Tylko Download i Translate")
        print("3 - Tylko Upload")
        print("4 - Przetwarzaj listę produktów z pliku")
        choice = input("Wprowadź wybór (1/2/3/4): ")
        return choice

    def execute_choice(self):
        choice = self.show_menu()
        # if choice == "1":
        #     self.facade.run_full_process()
        if choice == "1" or choice == "":
            self.facade.run_download_process()
            self.facade.run_translate_process()
            self.facade.go_to_shop()
            self.facade.run_upload_process()
        elif choice == "2":
            self.facade.run_download_process()
            self.facade.run_translate_process()
            self.facade.go_to_shop()
        elif choice == "3":
            self.facade.run_upload_process()
        elif choice == "4":
            filename = "products.txt"
            try:
                self.facade.run_batch_process(filename)
            except Exception:
                logging.error("Nie udało się przetworzyć pliku %s", filename)
        else:
            logging.error("Nieprawidłowy wybór.")