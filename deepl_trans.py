import deepl
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Użyj swojego klucza API DeepL Free
DEEPL_AUTH_KEY = "98ae0d75-7785-4f60-a8d4-64a869672fa5:fx"
translator = deepl.Translator(DEEPL_AUTH_KEY)

def translate_text_deepl(text, target_lang):
    """
    Tłumaczy podany tekst na wybrany język przy użyciu biblioteki DeepL.

    Parametry:
      text: Tekst do tłumaczenia.
      target_lang: Docelowy język (np. "EN" lub "FR").

    Zwraca:
      Przetłumaczony tekst.
    """
    try:
        # Używamy tag_handling="html", gdyż opis może zawierać znaczniki HTML
        result = translator.translate_text(text, target_lang=target_lang, tag_handling="html")
        logging.info("Tłumaczenie na %s zakończone.", target_lang)
        return result.text
    except Exception as e:
        logging.error("Błąd podczas tłumaczenia na %s: %s", target_lang, e)
        return ""