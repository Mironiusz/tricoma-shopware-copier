import logging
import deepl

class Translator:
    def __init__(self, config):
        self.auth_key = config["DEEPL_AUTH_KEY"]
        self.translator = deepl.Translator(self.auth_key)

    def translate_text(self, text, target_lang):
        try:
            result = self.translator.translate_text(text, target_lang=target_lang, tag_handling="html")
            logging.info("Translation to %s completed.", target_lang)
            return result.text
        except Exception as e:
            logging.error("Error during translation to %s: %s", target_lang, e)
            return ""

    def translate_product(self, product_data):
        description = product_data.get("beschreibung", "")
        if description:
            product_data["beschreibung_en"] = self.translate_text(description, "EN-GB")
            product_data["beschreibung_fr"] = self.translate_text(description, "FR")
        else:
            logging.warning("No product description to translate.")
        return product_data
