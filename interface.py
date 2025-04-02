import logging

class UserInterface:
    def __init__(self, facade):
        self.facade = facade

    def show_menu(self):
        print("Wybierz operację:")
        # print("1 - Pełny proces (Download, Translate, Upload)")
        print("1 - Tylko Download i Translate")
        print("2 - Tylko Upload")
        choice = input("Wprowadź wybór (1/2): ")
        return choice

    def execute_choice(self):
        choice = self.show_menu()
        # if choice == "1":
        #     self.facade.run_full_process()
        if choice == "1":
            self.facade.run_download_process()
            self.facade.run_translate_process()
            self.facade.go_to_shop()
        elif choice == "":
            self.facade.run_upload_process()
        elif choice == "2":
            self.facade.run_upload_process()
        else:
            logging.error("Nieprawidłowy wybór.")
