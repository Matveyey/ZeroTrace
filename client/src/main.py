from flet import app
from modules.ui.ui_elements.layout import MessengerApp


def main(page):
    app_ui = MessengerApp(page)
    app_ui.start()

app(target=main)
print("END")