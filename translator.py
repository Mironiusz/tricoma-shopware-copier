import logging
import deepl

class Translator:
    def __init__(self, config):
        self.auth_key = config["DEEPL_AUTH_KEY"]
        self.translator = deepl.Translator(self.auth_key)

    def translate_text(self, text, target_lang):
        try:
            result = self.translator.translate_text(text, target_lang=target_lang, tag_handling="html")
            logging.info("Tłumaczenie na %s zakończone.", target_lang)
            return result.text
        except Exception as e:
            logging.error("Błąd podczas tłumaczenia na %s: %s", target_lang, e)
            return ""

    def translate_product(self, product_data):
        description = product_data.get("beschreibung", "")
        if description:
            product_data["beschreibung_en"] = self.translate_text(description, "EN-GB")
            product_data["beschreibung_fr"] = self.translate_text(description, "FR")
        else:
            logging.warning("Brak opisu produktu do tłumaczenia.")
        return product_data
