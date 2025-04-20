import flet as ft

from modules.core.messenger_core import SecureMessenger


class LoginSystem:
    def __init__(self, page: ft.Page, messenger: SecureMessenger, on_success):
        self.page = page
        self.kem_pub = self.page.client_storage.get("kem_pub")
        self.sign_pub = self.page.client_storage.get("sign_pub")
        self.keys_data = self.page.client_storage.get("keys_data")
        self.username_area = ft.TextField(label="Username", width=600, scale=0)
        
        if self.kem_pub and self.sign_pub and self.keys_data:
            self.mode = "login"
        else:
            self.username_area.scale = 1
            self.mode = "register"
        self.on_success = on_success
        self.password_area = ft.TextField(label="Password", width=600, password=True)
        self.continue_button = ft.TextButton(
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.PRIMARY_CONTAINER, shape=ft.RoundedRectangleBorder(10)
            ),
            on_click=self.check_password if self.mode=="login" else self.register,
            width=300,
            height=50,
            text="Continue",
        )

        self.__secure_messenger = messenger

    def build(self):
        self.page.add(
            ft.Column(
                controls=[self.username_area, self.password_area, self.continue_button],
                spacing=50,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                height=self.page.height,
                width=self.page.width,
            )
        )
        self.page.update()

    def register(self, e):
        result = self.__secure_messenger.register(self.username_area.value ,self.password_area.value)
        if result:
            self.on_success()
        else:
            self.username_area.border_color = ft.Colors.ERROR_CONTAINER
            self.username_area.value = "Username already create"
            self.page.update()
    def check_password(self, e):
        password = self.password_area.value
        result = self.__secure_messenger.load_keys(
            self.kem_pub, self.sign_pub, self.keys_data, password
        )
        if result:
            self.on_success(password)
        else:
            self.password_area.border_color = ft.Colors.ERROR_CONTAINER
            self.password_area.value = "Incorrect"
            self.page.update()
