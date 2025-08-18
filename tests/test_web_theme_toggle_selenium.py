import threading
import time

import pytest

pytest.importorskip("flask")
selenium = pytest.importorskip("selenium")


def _run_app(port: int):
    from rabbitmirror.web.app import app

    app.testing = True
    app.run(host="127.0.0.1", port=port, use_reloader=False)


@pytest.mark.slow
def test_theme_toggle_cycles_dark_light_auto(monkeypatch):
    # Start the Flask dev server in a background thread
    port = 5055
    t = threading.Thread(target=_run_app, args=(port,), daemon=True)
    t.start()
    time.sleep(0.8)  # give the server a moment

    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.common.by import By

    options = ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    try:
        base = f"http://127.0.0.1:{port}"
        driver.get(base + "/")

        btn = driver.find_element(By.ID, "theme-toggle")
        html = driver.find_element(By.TAG_NAME, "html")

        # Click 1: auto -> dark
        btn.click()
        time.sleep(0.05)
        data_theme = html.get_attribute("data-theme")
        aria_pressed_1 = btn.get_attribute("aria-pressed")
        assert data_theme == "dark"
        assert aria_pressed_1 == "true"

        # Click 2: dark -> light
        btn.click()
        time.sleep(0.05)
        data_theme = html.get_attribute("data-theme")
        aria_pressed_2 = btn.get_attribute("aria-pressed")
        assert data_theme == "light"
        assert aria_pressed_2 == "false"

        # Click 3: light -> auto (attribute removed)
        btn.click()
        time.sleep(0.05)
        data_theme = html.get_attribute("data-theme")
        assert data_theme in (None, "")
    finally:
        driver.quit()
