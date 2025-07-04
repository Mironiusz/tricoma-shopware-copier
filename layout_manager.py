import logging
import os
import sys
import subprocess
import shutil
from selenium.webdriver.remote.webdriver import WebDriver

# Domyślne ustawienia – można nadpisać w config.json
DEFAULTS = {
    # Rozmiar i pozycja okna przeglądarki (w pikselach)
    "browser_width_px":    1750,
    "browser_height_px":   950,
    "browser_pos_x":       0,
    "browser_pos_y":       0,
    # Zoom dla karty Tricoma (%)
    "tricoma_zoom_pct":    100,
    # Rozmiar i pozycja terminala (w pikselach)
    "term_width_px":       640,
    "term_height_px":      480,
    "term_pos_x":          1750,
    "term_pos_y":          0
}


def _resize_and_position_terminal(px_w: int, px_h: int,
                                  pos_x: int, pos_y: int) -> None:
    """
    Ustawia pozycję i rozmiar fizycznego okna terminala.
    Działa na Windows (WinAPI), macOS (AppleScript) i Linux/X11 (wmctrl).
    """
    try:
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            # Pobranie tytułu консoli, aby znaleźć okno
            buf = ctypes.create_unicode_buffer(512)
            kernel32.GetConsoleTitleW(buf, ctypes.sizeof(buf))
            target = buf.value
            # Enumeracja wszystkich widocznych окien
            EnumWindows = user32.EnumWindows
            EnumProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
            GetText = user32.GetWindowTextW
            GetLen = user32.GetWindowTextLengthW
            IsVis = user32.IsWindowVisible
            hwnds = []
            def enum_win(hwnd, lparam):
                if not IsVis(hwnd): return True
                length = GetLen(hwnd)
                if length == 0: return True
                buf2 = ctypes.create_unicode_buffer(length+1)
                GetText(hwnd, buf2, length+1)
                if buf2.value == target:
                    hwnds.append(hwnd)
                    return False
                return True
            EnumWindows(EnumProc(enum_win), 0)
            hwnd = hwnds[0] if hwnds else kernel32.GetConsoleWindow()
            if hwnd:
                user32.MoveWindow(hwnd, pos_x, pos_y, px_w, px_h, True)
                logging.info("Terminal ustawiony na %dx%d @(%d,%d)", px_w, px_h, pos_x, pos_y)
            else:
                logging.warning("Nie znaleziono okna terminala.")
        elif sys.platform == "darwin":
            applescript = (
                'tell application "System Events" to tell (first process whose frontmost is true) '
                f'set position of front window to {{{pos_x}, {pos_y}}} '
                f'set size of front window to {{{px_w}, {px_h}}}'
            )
            subprocess.run(["osascript", "-e", applescript], check=False)
        else:
            if shutil.which("wmctrl"):
                geom = f"0,{pos_x},{pos_y},{px_w},{px_h}"
                subprocess.run(["wmctrl", "-r", ":ACTIVE:", "-e", geom], check=False)
            else:
                logging.warning("Brak narzędzia wmctrl – nie zmieniono terminala.")
    except Exception as e:
        logging.warning("Błąd przy ustawianiu terminala: %s", e)


def setup_layout(driver: WebDriver, cfg: dict | None = None) -> None:
    """
    Ustawia wymiary i pozycje okien przeglądarki oraz terminala
    zgodnie z wartościami w config.json.
    """
    # scalanie z DEFAULTS
    cfg = {**DEFAULTS, **(cfg or {})}

    # --- Ustaw okno przeglądarki ---
    bw = cfg.get("browser_width_px")
    bh = cfg.get("browser_height_px")
    bx = cfg.get("browser_pos_x")
    by = cfg.get("browser_pos_y")
    driver.set_window_position(bx, by)
    driver.set_window_size(bw, bh)
    logging.info("Przeglądarka ustawiona na %dx%d @(%d,%d)", bw, bh, bx, by)

    # --- Zoom na karcie Tricoma ---
    zoom_pct = cfg.get("tricoma_zoom_pct", 100)
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        try:
            url = driver.current_url
        except Exception:
            url = ""
        if "tricoma" in url:
            driver.execute_script("document.body.style.zoom = arguments[0] + '%';", zoom_pct)
            logging.info("Ustawiono zoom Tricoma na %s%% (URL: %s)", zoom_pct, url)
            break
    # wróć na pierwszą zakładkę
    driver.switch_to.window(driver.window_handles[0])

    # --- Ustaw okno terminala ---
    tw = cfg.get("term_width_px")
    th = cfg.get("term_height_px")
    tx = cfg.get("term_pos_x")
    ty = cfg.get("term_pos_y")
    _resize_and_position_terminal(tw, th, tx, ty)

# koniec pliku
