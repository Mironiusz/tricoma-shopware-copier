# tricoma-shopware-copier/layout_manager.py
import os
import sys
import logging
from selenium.webdriver.remote.webdriver import WebDriver

# Domyślne proporcje – można nadpisać w config.json
DEFAULTS = {
    "browser_width_ratio": 0.80,   # 80 % szerokości ekranu
    "browser_height_ratio": 1.00,  # 100 % wysokości
    "term_width_ratio":    0.20,   # 20 % szerokości
    "term_height_ratio":   0.50,   # 50 % wysokości
    "min_browser_height":  950,    # px
    "zoom_step_pct":       10      # o ile % przybliżać/oddalać jednorazowo
}

def _get_screen_size(driver: WebDriver) -> tuple[int, int]:
    """Pobiera dostępną rozdzielczość ekranu poprzez JS (działa we wszystkich
    nowoczesnych przeglądarkach)."""
    width  = driver.execute_script("return screen.availWidth;")
    height = driver.execute_script("return screen.availHeight;")
    return int(width), int(height)

def _apply_browser_zoom(driver: WebDriver, min_height: int, step: int = 10):
    """Zmniejsza zoom („ctrl -”) aż do uzyskania co najmniej min_height px."""
    current_zoom = 100  # zaczynamy od 100 %
    inner_h = driver.execute_script("return window.innerHeight;")
    while inner_h < min_height and current_zoom > 50:
        current_zoom -= step
        driver.execute_script(
            "document.body.style.zoom = arguments[0] + '%';", current_zoom
        )
        inner_h = driver.execute_script("return window.innerHeight;")
        logging.info(
            "Zmniejszono zoom do %s %% → wysokość okna: %s px", current_zoom, inner_h
        )

def _resize_terminal(width_ratio: float, height_ratio: float) -> None:
    """Ustawia rozmiar terminala (nie pozycję). Działa w Windows i *BSD/POSIX."""
    try:
        # przybliżenie – zakładamy znak ≈ 8×16 px (monospace)
        import shutil
        cols_total, lines_total = shutil.get_terminal_size()
        cols  = max(20, int(cols_total * width_ratio))
        lines = max(10, int(lines_total * height_ratio))
        if os.name == "nt":  # Windows -> komenda MODE
            os.system(f"mode con: cols={cols} lines={lines}")
        else:                # ANSI escape sequence (xterm, iTerm2, gnome-terminal…)
            sys.stdout.write(f"\x1b[8;{lines};{cols}t")
            sys.stdout.flush()
    except Exception as e:
        logging.warning("Nie udało się zmienić rozmiaru terminala: %s", e)

def setup_layout(driver: WebDriver, cfg: dict | None = None) -> None:
    """Główna funkcja – ustawia wymiary przeglądarki i terminala."""
    cfg = {**DEFAULTS, **(cfg or {})}           # mergujemy z domyślnymi
    scr_w, scr_h = _get_screen_size(driver)

    # --- PRZEGLĄDARKA ---
    new_w = int(scr_w * cfg["browser_width_ratio"])
    new_h = int(scr_h * cfg["browser_height_ratio"])
    driver.set_window_position(0, 0)
    driver.set_window_size(new_w, new_h)
    logging.info("Okno przeglądarki ustawione na %s × %s px", new_w, new_h)

    # --- Zoom, jeśli < min_browser_height ---
    _apply_browser_zoom(driver, cfg["min_browser_height"], cfg["zoom_step_pct"])

    # --- TERMINAL ---
    _resize_terminal(cfg["term_width_ratio"], cfg["term_height_ratio"])
