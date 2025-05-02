import logging

class UserInterface:
    def __init__(self, facade):
        self.facade = facade

    def show_menu(self):
        print("Choose an operation:")
        print("1 - Full process (Download, Translate, Upload)")
        print("2 - Download and Translate only")
        print("3 - Upload only")
        print("4 - Process product list from file")
        choice = input("Enter your choice (1/2/3/4): ")
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
                logging.error("Failed to process file %s", filename)
        else:
            logging.error("Invalid choice.")
