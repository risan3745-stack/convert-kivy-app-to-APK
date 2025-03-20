# Imports

import pyrebase
import requests
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.utils import get_color_from_hex
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.properties import NumericProperty
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.metrics import dp

# ----------------------------------------------------------------------------------------------------------------------

# Firebase Configuration

config = {
    "apiKey": "AIzaSyBzhPxemvqtZykNHGuyoPNVTQqxutUnYNE",
    "authDomain": "foodi-woodi.firebaseapp.com",
    "databaseURL": "https://foodi-woodi-default-rtdb.firebaseio.com/",
    "storageBucket": "foodi-woodi.appspot.com"
}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

def refresh_token(refresh_token):
    api_key = config["apiKey"]
    request_url = f"https://securetoken.googleapis.com/v1/token?key={api_key}"
    headers = {"content-type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "refresh_token", "refresh_token": refresh_token}

    try:
        response = requests.post(request_url, headers=headers, data=data)
        response.raise_for_status()
        return response.json().get('id_token'), response.json().get('refresh_token')
    except Exception as e:
        pass


def save_tokens(id_token, refresh_token):
    with open("auth_tokens.txt", "w") as f:
        f.write(f"{id_token}\n{refresh_token}")


def load_tokens():
    try:
        with open("auth_tokens.txt", "r") as f:
            tokens = f.read().splitlines()
            if len(tokens) >= 2:
                return tokens[0], tokens[1]
            return None, None
    except (FileNotFoundError, ValueError, IndexError):
        return None, None

# ----------------------------------------------------------------------------------------------------------------------

# Popup Classes

class TitleErrorPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Error"
        self.size_hint = (None, None)
        self.size = (400, 200)

        content = BoxLayout(
            orientation='vertical',
            padding=10,
            spacing=10
        )
        content.add_widget(Label(text="Title for recipe is required"))

        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=44
        )
        close_button = Button(
            text="Close",
            size_hint=(None, None),
            size=(100, 44)
        )

        close_button.bind(on_press=self.dismiss)
        button_layout.add_widget(Widget())
        button_layout.add_widget(close_button)
        button_layout.add_widget(Widget())
        content.add_widget(button_layout)
        self.content = content

class IngredientsErrorPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Error"
        self.size_hint = (None, None)
        self.size = (400, 200)

        content = BoxLayout(
            orientation='vertical',
            padding=10,
            spacing=10
        )
        content.add_widget(Label(text="Ingredients for recipe is required"))

        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=44
        )
        close_button = Button(
            text="Close",
            size_hint=(None, None),
            size=(100, 44)
        )

        close_button.bind(on_press=self.dismiss)
        button_layout.add_widget(Widget())
        button_layout.add_widget(close_button)
        button_layout.add_widget(Widget())
        content.add_widget(button_layout)
        self.content = content

class StepsErrorPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Error"
        self.size_hint = (None, None)
        self.size = (400, 200)

        content = BoxLayout(
            orientation='vertical',
            padding=10,
            spacing=10
        )
        content.add_widget(Label(text="At least one step is required"))

        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=44
        )
        close_button = Button(
            text="Close",
            size_hint=(None, None),
            size=(100, 44)
        )

        close_button.bind(on_press=self.dismiss)
        button_layout.add_widget(Widget())
        button_layout.add_widget(close_button)
        button_layout.add_widget(Widget())
        content.add_widget(button_layout)
        self.content = content


class PasswordErrorPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Password Error"
        self.size_hint = (None, None)
        self.size = (400, 200)

        content = BoxLayout(
            orientation='vertical',
            padding=10,
            spacing=10
        )
        content.add_widget(Label(text="Password must be 6 characters or more"))

        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=44
        )
        close_button = Button(
            text="Close",
            size_hint=(None, None),
            size=(100, 44)
        )

        close_button.bind(on_press=self.dismiss)
        button_layout.add_widget(Widget())
        button_layout.add_widget(close_button)
        button_layout.add_widget(Widget())
        content.add_widget(button_layout)
        self.content = content


class EmailErrorPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Email Error"
        self.size_hint = (None, None)
        self.size = (400, 200)
        content = BoxLayout(
            orientation='vertical',
            padding=10,
            spacing=10
        )

        content.add_widget(Label(text="Email is invalid"))
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=44)

        close_button = Button(
            text="Close",
            size_hint=(None, None),
            size=(100, 44))

        close_button.bind(on_press=self.dismiss)
        button_layout.add_widget(Widget())
        button_layout.add_widget(close_button)
        button_layout.add_widget(Widget())
        content.add_widget(button_layout)
        self.content = content


class CredentialsErrorPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Invalid Credentials"
        self.size_hint = (None, None)
        self.size = (400, 200)
        content = BoxLayout(
            orientation='vertical',
            padding=10,
            spacing=10)

        content.add_widget(Label(text="Invalid email or password"))
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=44)

        close_button = Button(
            text="Close",
            size_hint=(None, None),
            size=(100, 44))

        close_button.bind(on_press=self.dismiss)
        button_layout.add_widget(Widget())
        button_layout.add_widget(close_button)
        button_layout.add_widget(Widget())
        content.add_widget(button_layout)
        self.content = content


class ExistsErrorPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Exists"
        self.size_hint = (None, None)
        self.size = (400, 200)

        content = BoxLayout(
            orientation='vertical',
            padding=10,
            spacing=10)

        content.add_widget(Label(text="Account Already Exists"))
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=44)

        close_button = Button(
            text="Close",
            size_hint=(None, None),
            size=(100, 44))

        close_button.bind(on_press=self.dismiss)
        button_layout.add_widget(Widget())
        button_layout.add_widget(close_button)
        button_layout.add_widget(Widget())
        content.add_widget(button_layout)
        self.content = content

class ServerError(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Server error"
        self.size_hint = (None, None)
        self.size = (400, 200)

        content = BoxLayout(
            orientation='vertical',
            padding=10,
            spacing=10)

        content.add_widget(Label(text="There is a server error. We are trying hard to fix it. Please check back later."))
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=44)

        close_button = Button(
            text="Close",
            size_hint=(None, None),
            size=(100, 44))

        close_button.bind(on_press=self.dismiss)
        button_layout.add_widget(Widget())
        button_layout.add_widget(close_button)
        button_layout.add_widget(Widget())
        content.add_widget(button_layout)
        self.content = content

class SuccessEmail(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Success"
        self.size_hint = (None, None)
        self.size = (400, 200)

        content = BoxLayout(
            orientation='vertical',
            padding=10,
            spacing=10)

        content.add_widget(Label(text="Email Successfully sent"))
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=44)

        close_button = Button(
            text="Close",
            size_hint=(None, None),
            size=(100, 44))

        close_button.bind(on_press=self.dismiss)
        button_layout.add_widget(Widget())
        button_layout.add_widget(close_button)
        button_layout.add_widget(Widget())
        content.add_widget(button_layout)
        self.content = content

class Success(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Success"
        self.size_hint = (None, None)
        self.size = (400, 200)

        content = BoxLayout(
            orientation='vertical',
            padding=10,
            spacing=10)

        content.add_widget(Label(text="Recipe Submitted successfully"))
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=44)

        close_button = Button(
            text="Close",
            size_hint=(None, None),
            size=(100, 44))

        close_button.bind(on_press=self.dismiss)
        button_layout.add_widget(Widget())
        button_layout.add_widget(close_button)
        button_layout.add_widget(Widget())
        content.add_widget(button_layout)
        self.content = content

class Failiure(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Error"
        self.size_hint = (None, None)
        self.size = (400, 200)

        content = BoxLayout(
            orientation='vertical',
            padding=10,
            spacing=10)

        content.add_widget(Label(text="Unexpected error"))
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=44)

        close_button = Button(
            text="Close",
            size_hint=(None, None),
            size=(100, 44))

        close_button.bind(on_press=self.dismiss)
        button_layout.add_widget(Widget())
        button_layout.add_widget(close_button)
        button_layout.add_widget(Widget())
        content.add_widget(button_layout)
        self.content = content

# ----------------------------------------------------------------------------------------------------------------------

# Screens

class Settings(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        screen_width, screen_height = Window.size
        base_font_size = min(screen_width, screen_height) / 20

        self.settings_label = Label(
            text="Settings:",
            font_size=self.scale_font(base_font_size * 1.5),
            color=get_color_from_hex('#ffffff'),
            size_hint=(None, None),
            size=(dp(200), dp(60)),
            pos_hint={'center_x': 0.5, 'top': 1},
            halign='center',
            valign='middle'
        )

        self.Back = Button(
            text="Back",
            font_size=self.scale_font(base_font_size * 1.5),
            color=get_color_from_hex('#fc0303'),
            pos_hint={'center_x': 0.5, 'top': 0.9},
            pos=(0, -60),
            size_hint=(None, None),
            size=(dp(200), dp(50)),
            text_size=(dp(200), None),
            halign='center',
            background_color=get_color_from_hex('#1303fc'),
            background_normal=''
        )

        self.Reset_Password = Button(
            text="forgot password",
            bold=True,
            font_size=self.scale_font(base_font_size * 1.2),
            color=get_color_from_hex('#ff7403'),
            pos_hint={'center_x': 0.5, 'top': 0.8},
            pos=(0, -60),
            size_hint=(None, None),
            size=(dp(450), dp(50)),
            text_size=(dp(450), None),
            halign='center',
            background_color=get_color_from_hex('#03ff46'),
            background_normal=''
        )

        self.Back.bind(on_press=self.Return_to_main_app)
        self.Reset_Password.bind(on_press=self.Go_to_Forgot_Password_screen)
        layout.add_widget(self.settings_label)
        layout.add_widget(self.Back)
        layout.add_widget(self.Reset_Password)
        self.add_widget(layout)

        Window.bind(size=self.update_label_size)
        Clock.schedule_once(lambda dt: self.update_label_size(Window, Window.size), 0)

    def update_label_size(self, instance, size):
        screen_width, screen_height = size
        base_font_size = min(screen_width, screen_height) / 20

        self.settings_label.font_size = self.scale_font(base_font_size * 1.5)
        self.Back.font_size = self.scale_font(base_font_size * 1.5)
        self.Reset_Password.font_size = self.scale_font(base_font_size * 1.2)

        self.settings_label.size = (dp(200), dp(60))
        self.Back.size = (dp(200), dp(50))
        self.Reset_Password.size = (dp(450), dp(50))

    def scale_font(self, size):
        return dp(size)


    def Return_to_main_app(self, instance):
        self.manager.current = 'app'

    def Go_to_Forgot_Password_screen(self, instance):
        self.manager.current = 'forgot'

class ForgotPassword(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(50)
        )

        # Initialize labels and button
        self.Forgot_password = Label(
            text="Forgot your password?",
            bold=True,
            color=get_color_from_hex('#ff0303'),
            halign='center',
            valign='middle',
            size_hint_y=None  # Don't let it expand vertically
        )

        self.Instructions = Label(
            text="We'll send an email to reset your password then once sent, close the app and come back in and login",
            bold=True,
            color=get_color_from_hex('#030fff'),
            halign='center',
            valign='middle',
            size_hint_y=None  # Don't let it expand vertically
        )

        self.Ok = Button(
            text="Send Email",
            size_hint=(0.6, 0.11),
            background_color=get_color_from_hex('#fc7303'),
            background_normal='',
            color="black",
        )
        self.Ok.bind(on_press=self.reset_password)

        self.Close = Button(
            text="Close app",
            size_hint=(0.6, 0.11),
            background_color=get_color_from_hex('#1eff05'),
            background_normal='',
            color="black",
            opacity=0,  # Invisible initially
            disabled=True  # Disable it initially
        )

        self.Close.bind(on_press=self.Go_Back)

        # Add widgets to layout
        self.layout.add_widget(self.Forgot_password)
        self.layout.add_widget(self.Instructions)
        self.layout.add_widget(self.Ok)
        self.layout.add_widget(self.Close)

        self.add_widget(self.layout)

        # Bind the window size to update the label
        Window.bind(size=self.update_label_size)
        Clock.schedule_once(lambda dt: self.update_label_size(Window, Window.size), 0)

    def update_label_size(self, instance, size):
        screen_width, screen_height = size
        base_font_size = min(screen_width, screen_height) / 20

        self.Forgot_password.font_size = self.scale_font(base_font_size * 2.0) #Increased font size for this one!
        self.Instructions.font_size = self.scale_font(base_font_size * 1.3) #Increased font size for this one!
        self.Ok.font_size = self.scale_font(base_font_size * 1.3)
        self.Close.font_size = self.scale_font(base_font_size * 1.3)

        self.Forgot_password.text_size = (screen_width * 0.9, None)
        self.Instructions.text_size = (screen_width * 0.9, None)

        self.Forgot_password.height = self.Forgot_password.texture_size[1]  # Adjust height based on text content
        self.Instructions.height = self.Instructions.texture_size[1]  # Adjust height based on text content

    def scale_font(self, size):
        return dp(size)

    def reset_password(self, instance):
        try:
            # Read email directly from file
            with open("email.txt", "r") as f:
                email = f.read().strip()  # Clean whitespace/newlines

            if email:
                auth.send_password_reset_email(email)
                SuccessEmail().open()

        except auth.AuthError as e:
            ServerError().open()
        except Exception as e:
            ServerError().open()
        Clock.schedule_once(self.show_close_button, 3)

    def show_close_button(self, dt):
        self.Close.opacity = 1  # Make the button visible
        self.Close.disabled = False  # Enable the button

    def Go_Back(self, instance):
        App.get_running_app().stop()


class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loading_popup = None
        self.show_welcome_ui()  # Always show welcome UI first, then goes to the login screen, or auto-logins the user

    def show_welcome_ui(self):
        self.clear_widgets()
        layout = BoxLayout(
            orientation='vertical',
            spacing=20,
            padding=50
        )

        welcome_label = Label(
            text="Welcome to Foodi Woodi!!!",
            font_size=40,
            bold=True,
            color=get_color_from_hex('#ffffff')
        )

        proceed_button = Button(
            text="Proceed",
            size_hint=(0.6, 0.15),
            pos_hint={'center_x': 0.5},
            background_color=get_color_from_hex('#0905f5'),
            background_normal='',
            color="black",
            font_size=24
        )
        proceed_button.bind(on_press=self.on_proceed_clicked)

        layout.add_widget(welcome_label)
        layout.add_widget(proceed_button)
        self.add_widget(layout)

    def on_proceed_clicked(self, instance):
        self.show_loading("Checking for saved login...")
        Clock.schedule_once(lambda dt: self.attempt_auto_login(), 0.1)

    def attempt_auto_login(self):
        token_result = load_tokens()

        try:
            if token_result and len(token_result) == 2:
                stored_id_token, stored_refresh_token = token_result

                # Refresh tokens (to auto-login user to the app)
                new_id_token, new_refresh_token = refresh_token(stored_refresh_token)
                if new_id_token:
                    # Verify token with Firebase
                    user_info = auth.get_account_info(new_id_token)
                    user_id = user_info['users'][0]['localId']

                    # Check user exists in database
                    user_data = db.child("users").child(user_id).get(token=new_id_token).val()
                    if not user_data:
                        raise Exception("User account not found")

                    # Save new tokens and username
                    save_tokens(new_id_token, new_refresh_token)
                    if 'username' in user_data:
                        with open("user.txt", "w") as f:
                            f.write(user_data['username'])

                    # Login successful - goes to main app
                    if self.manager:
                        self.dismiss_loading()
                        self.manager.current = 'app'
                        return

            # If token check fails, the go to the login page
            self.fallback_to_login()

        except Exception as e:
            self.fallback_to_login()

    def fallback_to_login(self):
        self.dismiss_loading()
        try:
            os.remove("auth_tokens.txt")
        except (FileNotFoundError, PermissionError):
            pass
        if self.manager:
            self.manager.current = 'login'

    def show_loading(self, message="Loading..."):
        self.loading_popup = Popup(
            title=message,
            content=BoxLayout(
                orientation='vertical',
                spacing=10,
                children=[
                    Label(text="Checking saved credentials..."),
                    Button(
                        text="Cancel",
                        size_hint_y=None,
                        height=40,
                        on_press=lambda x: self.fallback_to_login()
                    )
                ]
            ),
            size_hint=(None, None),
            size=(300, 200)
        )
        self.loading_popup.open()

    def dismiss_loading(self):
        if self.loading_popup:
            self.loading_popup.dismiss()
            self.loading_popup = None


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(
            orientation='vertical',
            spacing=10,
            padding=10
        )

        input_layout = BoxLayout(
            orientation='vertical',
            spacing=10
        )

        self.email_input = TextInput(
            hint_text='Email',
            multiline=False,
            background_color=(0, 0, 0, 1),
            font_size=40,
            hint_text_color=(0, 1, 0, 1),
            foreground_color=(1, 1, 1, 1)
        )

        self.password_input = TextInput(
            hint_text='Password',
            multiline=False,
            password=True,
            background_color=(0, 0, 0, 1),
            font_size=40,
            hint_text_color=(0, 1, 0, 1),
            foreground_color=(1, 1, 1, 1)
        )

        input_layout.add_widget(self.email_input)
        input_layout.add_widget(self.password_input)

        self.login_button = Button(
            text='Login',
            background_color=get_color_from_hex('#f57905'),
            background_normal='',
            bold=True,
            font_size=20,
            color="black"
        )
        self.login_button.bind(on_press=self.login)
        main_layout.add_widget(input_layout)
        main_layout.add_widget(self.login_button)

        self.signup_button = Button(
            text="Don't have an account? Create one here.",
            size_hint=(1, 0.2),
            background_color=get_color_from_hex('#0905f5'),
            background_normal='',
            bold=True,
            font_size=20,
            color="black"
        )
        self.signup_button.bind(on_press=self.open_signup_screen)
        main_layout.add_widget(self.signup_button)
        self.add_widget(main_layout)

    def login(self, instance):
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            save_tokens(user['idToken'], user['refreshToken'])
            user_data = db.child("users").child(user['localId']).get().val()
            if user_data and 'username' in user_data:
                with open("user.txt", "w") as f:
                    f.write(user_data['username'])

                file = open("email.txt", "w")
                file.write(email)

            self.manager.current = 'app'
        except Exception as e:
            error_str = str(e)
            if "INVALID_LOGIN_CREDENTIALS" in error_str or "invalid email" in error_str.lower():
                CredentialsErrorPopup().open()

    def open_signup_screen(self, instance):
        self.manager.current = 'signup'


class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(
            orientation='vertical',
            spacing=10,
            padding=10
        )

        self.email_input = TextInput(
            hint_text='Email',
            multiline=False,
            background_color=(0, 0, 0, 1),
            font_size=40,
            hint_text_color=(0, 1, 0, 1),
            foreground_color=(1, 1, 1, 1)
        )

        self.password_input = TextInput(
            password=True,
            hint_text='Password',
            multiline=False,
            background_color=(0, 0, 0, 1),
            font_size=40,
            hint_text_color=(0, 1, 0, 1),
            foreground_color=(1, 1, 1, 1)
        )

        self.Name = TextInput(
            hint_text='Your Name',
            multiline=False,
            background_color=(0, 0, 0, 1),
            font_size=40,
            hint_text_color=(0, 1, 0, 1),
            foreground_color=(1, 1, 1, 1)
        )

        signup_button = Button(
            text="Create Account",
            size_hint=(1, 0.2),
            background_color=get_color_from_hex('#31f505'),
            background_normal='',
            bold=True,
            font_size=20,
            color="black"
        )
        signup_button.bind(on_press=self.signup)

        back_to_login_button = Button(
            text="Back to login",
            size_hint=(1, 0.2),
            background_color=get_color_from_hex('#a905f5'),
            background_normal='',
            bold=True,
            font_size=20,
            color="black"
        )
        back_to_login_button.bind(on_press=self.back_to_login)
        layout.add_widget(self.email_input)
        layout.add_widget(self.password_input)
        layout.add_widget(self.Name)
        layout.add_widget(signup_button)
        layout.add_widget(back_to_login_button)
        self.add_widget(layout)

    def signup(self, instance):
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()
        username = self.Name.text.strip()
        try:
            user = auth.create_user_with_email_and_password(email, password)
            save_tokens(user['idToken'], user['refreshToken'])

            db.child("users").child(user['localId']).set({
                "email": email,
                "username": username
            })

            with open("user.txt", "w") as f:
                f.write(username)
            self.email_input.text = ""
            self.password_input.text = ""
            self.manager.current = 'login'
        except Exception as e:
            error_str = str(e)
            if "WEAK_PASSWORD" in error_str:
                PasswordErrorPopup().open()

            elif "INVALID_EMAIL" in error_str:
                EmailErrorPopup().open()

            elif "EMAIL_EXISTS" in error_str:
                ExistsErrorPopup().open()

            else:
                Failiure().open()

    def back_to_login(self, instance):
        self.manager.current = 'login'


class AddRecipe(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cuisine_name = ""  # Store selected cuisine name
        self.layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=20)

        self.Back_Button = Button(
            text='Back',
            size_hint=(None, None),
            size=(100, 50),
            pos_hint={'x': 0, 'top': 1},
            background_color=get_color_from_hex('#ff2121'),
            background_normal='',
            bold=True,
            font_size=20,
            color="black"
        )
        self.Back_Button.bind(on_press=self.back)
        self.layout.add_widget(self.Back_Button)

        self.Add_Step = Button(
            text='add step',
            size_hint=(None, None),
            size=(100, 50),
            pos_hint={'y': 0, 'top': 1},
            background_color=get_color_from_hex('#2125ff'),
            background_normal='',
            bold=True,
            font_size=20,
            color="black"
        )
        self.Add_Step.bind(on_press=self.add_step)
        self.layout.add_widget(self.Add_Step)

        # Title input
        self.title_input = TextInput(
            hint_text='Recipe Title goes here',
            background_color=(0, 0, 0, 1),
            foreground_color=(1, 1, 1, 1),
            font_size=30,
            multiline=False,
            padding=(10, 10)
        )
        self.layout.add_widget(self.title_input)

        self.ingredients = TextInput(
            hint_text='Ingredients goes here',
            background_color=(0, 0, 0, 1),
            foreground_color=(1, 1, 1, 1),
            font_size=30,
            multiline=False,
            padding=(10, 10)
        )
        self.layout.add_widget(self.ingredients)

        # Message label
        self.message = Label(
            font_size=30,
            halign='center',
            size_hint_y=None,
            height=60
        )
        self.layout.add_widget(self.message)

        # ScrollView for steps
        scroll = ScrollView()
        self.step_grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.step_grid.bind(minimum_height=self.step_grid.setter('height'))

        self.step_inputs = []
        for i in range(1, 8):
            step_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=60)
            step_label = Label(
                text=f"Step {i}:",
                font_size=30,
                size_hint_x=0.3,
                halign='left'
            )

            step_input = TextInput(
                background_color=(0, 0, 0, 1),
                foreground_color=(1, 1, 1, 1),
                font_size=30,
                multiline=False,
                padding=(10, 10)
            )

            self.step_inputs.append(step_input)
            step_row.add_widget(step_label)
            step_row.add_widget(step_input)
            self.step_grid.add_widget(step_row)

        scroll.add_widget(self.step_grid)
        self.layout.add_widget(scroll)

        # Submit button
        submit_button = Button(
            text='Submit Recipe',
            size_hint=(1, None),
            height=50,
            background_color=get_color_from_hex('#31f505'),
            background_normal='',
            bold=True,
            font_size=20,
            color="black"
        )

        submit_button.bind(on_press=self.submit_recipe)
        self.layout.add_widget(submit_button)

        self.add_widget(self.layout)

    def add_step(self, instance=None):
        step_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=60)
        step_label = Label(
            text=f"Step {len(self.step_inputs) + 1}:",
            font_size=30,
            size_hint_x=0.3)
        step_input = TextInput(
            background_color=(0, 0, 0, 1),
            foreground_color=(
                1,
                1,
                1,
                1),
            font_size=30,
            multiline=False,
            padding=(10, 10)
        )
        self.step_inputs.append(step_input)
        step_row.add_widget(step_label), step_row.add_widget(step_input)
        self.step_grid.add_widget(step_row)

    def update_cuisine_name(self, cuisine_name):
        self.message.text = f"Add recipe to {cuisine_name}:"
        self.cuisine_name = cuisine_name  # Store the cuisine name

    def submit_recipe(self, instance):
        # Collect data from inputs
        title = self.title_input.text.strip()
        ingredients = self.ingredients.text.strip()
        steps = [step.text.strip() for step in self.step_inputs if step.text.strip()]

        if not title:
            TitleErrorPopup().open()
            return

        if not steps:
            StepsErrorPopup().open()
            return

        if not ingredients:
            IngredientsErrorPopup().open()
            return

        # Push to Firebase
        try:
            with open("user.txt", "r") as file:  # Lowercase filename
                username = file.read().strip()
        except FileNotFoundError:
            username = "Unknown"

        recipe_data = {
            "Ingredients": ingredients,
            "steps": steps,
            "author": username,
        }

        try:
            (db.child("recipes/cuisines")
             .child(self.cuisine_name)
             .child(username)
             .child(title)
             .set(recipe_data))

            self.clear_inputs()
            Success().open()
        except Exception as e:
            ServerError().open()  # Debugging help

    def clear_inputs(self):
        self.title_input.text = ""
        for step_input in self.step_inputs:
            step_input.text = ""

    def back(self, instance):
        self.manager.current = 'app'

class MainApp(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = RelativeLayout()
        self.add_widget(self.layout)

        # Dropdown menu configuration
        self.dropdown_menu = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            width=400,
            height=0,
            spacing=10,
            padding=2,
            opacity=0
        )

        with self.dropdown_menu.canvas.before:
            Color(0, 0, 0, 0.7)
            self.dropdown_menu.bg_rect = Rectangle(
                pos=self.dropdown_menu.pos,
                size=self.dropdown_menu.size
            )
        self.dropdown_menu.bind(pos=self.update_bg_rect, size=self.update_bg_rect)
        self.layout.add_widget(self.dropdown_menu)

        cuisines = [
            "Italian",
            "Jamaican",
            "Hispanic",
            "Indian",
            "American",
            "Chinese",
            "General"
        ]

        for cuisine in cuisines:
            btn = Button(
                text=cuisine,
                size_hint_y=None,
                background_normal=f'{cuisine}.png',
                color=(1, 1, 1, 1),
                bold=True,
                font_size='18sp',
                border=(0, 0, 0, 1)
            )
            btn.bind(on_press=self.on_cuisine_selected)
            self.dropdown_menu.add_widget(btn)

        self.add_recipe_button = CircularButton(
            text="+",
            size_hint=(
                None,
                None),
            size=(
                60,
                60),
            pos_hint={'bottom': 1, 'right': 0.1}
        )

        self.add_recipe_button.bind(
            on_press=self.toggle_dropdown_menu,
            pos=self.update_dropdown_position,
            size=self.update_dropdown_position
        )
        self.layout.add_widget(self.add_recipe_button)

        self.Settings = Button(
            size_hint=(
                None,
                None),
            size=(
                60,
                60),
            pos_hint={'bottom': 1, 'right': 1},
            background_normal='settings.png'
        )
        self.Settings.bind(
            on_press=self.open_settings,
            pos = self.update_dropdown_position,
            size = self.update_dropdown_position)
        self.layout.add_widget(self.Settings)

    def open_settings(self, *args):
        self.manager.get_screen('Settings')
        self.manager.current = 'Settings'


    def update_bg_rect(self, instance, value):
        instance.bg_rect.pos = instance.pos
        instance.bg_rect.size = instance.size

    def update_dropdown_position(self, *args):
        btn = self.add_recipe_button
        btn_x = btn.x
        btn_top = btn.y + btn.height
        dropdown_x = btn_x + (btn.width / 2) - (self.dropdown_menu.width / 2)
        dropdown_y = btn_top
        self.dropdown_menu.pos = (dropdown_x, dropdown_y)
        self.dropdown_menu.height = Window.height - dropdown_y

    def toggle_dropdown_menu(self, instance):
        if self.dropdown_menu.opacity == 0:
            # Show the dropdown menu
            self.update_dropdown_position()
            self.dropdown_menu.opacity = 1

            # Create a popup to display instructions
            instruction_popup = Popup(
                title="Instructions",
                size_hint=(None, None),
                size=(400, 200)
            )

            # Create content for the popup
            content = BoxLayout(orientation='vertical', spacing=10, padding=10)
            instruction_label = Label(
                text="Select a cuisine to add a recipe to.",
                font_size=20,
                halign='center'
            )

            close_button = Button(
                text="Ok",
                size_hint=(1, None),
                height=50,
                background_color=get_color_from_hex('#31f505'),
                background_normal='',
                bold=True,
                font_size=20,
                color="black"
            )

            close_button.bind(on_press=instruction_popup.dismiss)

            # Add widgets to the popup content
            content.add_widget(instruction_label)
            content.add_widget(close_button)
            instruction_popup.content = content

            # Open the popup
            instruction_popup.open()
        else:
            # Hide the dropdown menu
            self.dropdown_menu.opacity = 0

    def on_cuisine_selected(self, instance):
        self.dropdown_menu.opacity = 0
        cuisine_screen = self.manager.get_screen('cuisine')
        cuisine_screen.update_cuisine_name(instance.text)
        self.manager.current = 'cuisine'

# ----------------------------------------------------------------------------------------------------------------------

# Circular button properties (used in MainApp class)

class CircularButton(Button):
    radius = NumericProperty(20)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.bind(
            pos=self.update_radius,
            size=self.update_radius)
        self.update_radius()

    def update_radius(self, *args):
        self.radius = min(self.width, self.height) / 2
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex('#971df5'))
            Ellipse(pos=self.pos, size=(self.radius * 2, self.radius * 2))

# ----------------------------------------------------------------------------------------------------------------------

# Screen manager (used to switch screens via buttons)

class MyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(WelcomeScreen(name='welcome'))
        self.add_widget(LoginScreen(name='login'))
        self.add_widget(MainApp(name='app'))
        self.add_widget(SignupScreen(name='signup'))
        self.add_widget(AddRecipe(name='cuisine'))
        self.add_widget(Settings(name='Settings'))
        self.add_widget(ForgotPassword(name='forgot'))

# ----------------------------------------------------------------------------------------------------------------------

# Build and run the app

class MyApp(App):
    def build(self):
        return MyScreenManager(transition=FadeTransition())


if __name__ == '__main__':
    MyApp().run()
