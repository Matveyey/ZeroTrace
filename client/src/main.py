from flet import app
from modules.ui.ui_elements.layout import MessengerApp


def main(page):
    app_ui = MessengerApp(page)
    app_ui.build()

app(target=main)
print("END")