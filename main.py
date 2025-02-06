import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.core.clipboard import Clipboard  # Import clipboard support


class Setup(GridLayout):
    def __init__(self, **kwargs):
        super(Setup, self).__init__(**kwargs)
        self.cols = 2

        self.add_widget(Label(text="Enter text to capitalize: ", color="white"))

        self.utext = TextInput(multiline=False, background_color="lime")
        self.add_widget(self.utext)

        self.submit = Button(text="Capitalize", font_size=40)
        self.submit.bind(on_press=self.show_popup)  # Bind button to method
        self.add_widget(self.submit)

    def show_popup(self, instance):
        """Show popup with capitalized text and copy button"""
        capitalized_text = self.utext.text.upper()

        # Label to display the capitalized text
        text_label = Label(text=capitalized_text, font_size=20)

        # Button to copy text to clipboard
        copy_button = Button(text="Copy", size_hint=(1, 0.3))
        copy_button.bind(on_press=lambda x: Clipboard.copy(capitalized_text))

        # Button to close the popup
        close_button = Button(text="Close", size_hint=(1, 0.3))
        close_button.bind(on_press=lambda x: popup.dismiss())

        # Layout for popup
        popup_layout = GridLayout(cols=1, padding=10)
        popup_layout.add_widget(text_label)
        popup_layout.add_widget(copy_button)
        popup_layout.add_widget(close_button)

        # Create and open the popup
        popup = Popup(title="Capitalized Text",
                      content=popup_layout,
                      size_hint=(0.8, 0.5))
        popup.open()


class MyApp(App):
    def build(self):
        return Setup()


if __name__ == "__main__":
    MyApp().run()
