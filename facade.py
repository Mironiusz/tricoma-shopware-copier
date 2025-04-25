import time
import logging
import os
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
        # Download danych z CRM
        product_data = self.crm_downloader.run_sequence()
        self.crm_downloader.save_product_data(product_data)
        # Tłumaczenie opisu
        product_data = self.translator.translate_product(product_data)
        self.crm_downloader.display_final_info(product_data)
        self.crm_downloader.save_product_data(product_data)
        # Upload do sklepu
        self.shop_uploader.go_to_shop(product_data)

        input("\nNaciśnij Enter, aby przejść do wysyłania danych do sklepu...")

        self.shop_uploader.run_sequence(product_data)
        return product_data

    def run_download_process(self):
        product_data = self.crm_downloader.run_sequence()
        self.crm_downloader.save_product_data(product_data)
        return product_data

    def run_translate_process(self):
        product_data = self.crm_downloader.load_product_data()
        product_data = self.translator.translate_product(product_data)
        self.crm_downloader.display_final_info(product_data)
        self.crm_downloader.save_product_data(product_data)
        return product_data

    def get_data(self):
        return self.crm_downloader.load_product_data()

    def go_to_shop(self):
        product_data = self.get_data()
        self.shop_uploader.go_to_shop(product_data)
        return product_data

    def run_upload_process(self):
        product_data = self.get_data()
        self.shop_uploader.run_sequence(product_data)
        return product_data

    def run_batch_process(self,
                          filename="products.txt",
                          counter_file="product_counter.txt",
                          pause_file="pause.txt"):
        """
        Dla każdego produktu z pliku (jedna nazwa w linii):
          - wywołaj open_product(name)
          - wykonaj pełen proces kopiowania
          - usuń linię z pliku
          - zaktualizuj licznik i czas działania
          - sprawdź pause.txt i ewentualnie przerwij
        """

        # --- Inicjalizacja licznika i czasu ---
        processed_count = 0
        start_time = time.time()

        if os.path.exists(counter_file):
            try:
                with open(counter_file, "r", encoding="utf-8") as cf:
                    lines = cf.read().splitlines()
                processed_count = int(lines[0])
                h, m, s = map(int, lines[1].split(":"))
                elapsed_before = h * 3600 + m * 60 + s
                start_time = time.time() - elapsed_before
                logging.info(
                    "Wczytano stan z %s: %d produktów, czas wcześniej: %s",
                    counter_file, processed_count, lines[1]
                )
            except Exception:
                logging.warning(
                    "Nie udało się wczytać %s — licznik zerowany.", counter_file
                )
                processed_count = 0
                start_time = time.time()

        # --- Wczytanie listy produktów ---
        try:
            with open(filename, "r", encoding="utf-8") as f:
                all_lines = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            logging.error("Plik %s nie istnieje.", filename)
            return

        remaining = all_lines.copy()

        # --- Główna pętla batchu ---
        for name in all_lines:
            logging.info("=== Przetwarzam produkt: %s ===", name)

            # 1) Open/search
            self.crm_downloader.open_product(name)
            # 2) Download, translate, upload
            self.run_download_process()
            self.run_translate_process()
            self.go_to_shop()
            self.run_upload_process()

            # --- Po pomyślnym uploadzie ---
            processed_count += 1

            # Usuń z remaining i nadpisz products.txt
            remaining.remove(name)
            with open(filename, "w", encoding="utf-8") as f:
                for r in remaining:
                    f.write(r + "\n")

            # Oblicz i zapisz licznik + czas
            elapsed = int(time.time() - start_time)
            h, rem = divmod(elapsed, 3600)
            m, s = divmod(rem, 60)
            elapsed_str = f"{h:02d}:{m:02d}:{s:02d}"

            with open(counter_file, "w", encoding="utf-8") as cf:
                cf.write(f"{processed_count}\n")
                cf.write(elapsed_str + "\n")

            logging.info(
                "Przetworzono %d produktów; czas działania: %s",
                processed_count, elapsed_str
            )

            # --- Sprawdzenie pliku pause.txt ---
            try:
                with open(pause_file, "r", encoding="utf-8") as pf:
                    content = pf.read().strip()
                if content == "-":
                    logging.info(
                        "Znaleziono '-' w %s — przerywam batch i wracam do menu.",
                        pause_file
                    )
                    return
            except FileNotFoundError:
                # plik nie istnieje → batch leci dalej
                pass
            except Exception as e:
                logging.warning(
                    "Nie udało się odczytać %s (%s) — batch kontynuuje.",
                    pause_file, e
                )

        logging.info("Przetwarzanie z pliku %s zakończone.", filename)