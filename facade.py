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
        # Download data from CRM
        product_data = self.crm_downloader.run_sequence()
        self.crm_downloader.save_product_data(product_data)
        # Translate description
        product_data = self.translator.translate_product(product_data)
        self.crm_downloader.display_final_info(product_data)
        self.crm_downloader.save_product_data(product_data)
        # Upload to shop
        self.shop_uploader.go_to_shop(product_data)

        input("\nPress Enter to proceed with sending data to the shop...")

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
        For each product from the file (one name per line):
          - call open_product(name)
          - execute the full copy process
          - remove the line from the file
          - update counter and run time
          - check pause.txt and possibly break
        """

        # --- Initialize counter and start time ---
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
                    "Loaded state from %s: %d products, previous time: %s",
                    counter_file, processed_count, lines[1]
                )
            except Exception:
                logging.warning(
                    "Failed to load %s — counter reset.", counter_file
                )
                processed_count = 0
                start_time = time.time()

        # --- Load list of products ---
        try:
            with open(filename, "r", encoding="utf-8") as f:
                all_lines = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            logging.error("File %s does not exist.", filename)
            return

        remaining = all_lines.copy()

        # --- Main batch loop ---
        for name in all_lines:
            logging.info("=== Processing product: %s ===", name)

            # 1) Open/search
            self.crm_downloader.open_product(name)
            # 2) Download, translate, upload
            self.run_download_process()
            self.run_translate_process()
            self.go_to_shop()
            self.run_upload_process()

            # --- After successful upload ---
            processed_count += 1

            # Remove from remaining and overwrite products.txt
            remaining.remove(name)
            with open(filename, "w", encoding="utf-8") as f:
                for r in remaining:
                    f.write(r + "\n")

            # Calculate and save counter + elapsed time
            elapsed = int(time.time() - start_time)
            h, rem = divmod(elapsed, 3600)
            m, s = divmod(rem, 60)
            elapsed_str = f"{h:02d}:{m:02d}:{s:02d}"

            with open(counter_file, "w", encoding="utf-8") as cf:
                cf.write(f"{processed_count}\n")
                cf.write(elapsed_str + "\n")

            logging.info(
                "Processed %d products; runtime: %s",
                processed_count, elapsed_str
            )

            # --- Check pause.txt ---
            try:
                with open(pause_file, "r", encoding="utf-8") as pf:
                    content = pf.read().strip()
                if content == "-":
                    logging.info(
                        "Found '-' in %s — aborting batch and returning to menu.",
                        pause_file
                    )
                    return
            except FileNotFoundError:
                # file does not exist → continue batch
                pass
            except Exception as e:
                logging.warning(
                    "Failed to read %s (%s) — batch continues.",
                    pause_file, e
                )

        logging.info("Processing from file %s completed.", filename)
