from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.list import OneLineListItem
import gspread
import gspread_db
from PyDictionary import PyDictionary
from google.oauth2.service_account import Credentials

root_kv = """
BoxLayout:
    orientation: "vertical"

    MDToolbar:
        id: toolbar
        title: "Wordie"
        md_bg_color: app.theme_cls.primary_color


    MDBottomNavigation:
        id: panel

        MDBottomNavigationItem:
            name: "files1"
            text: "Word"
            icon: "card-text"

            BoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(10)
                pos_hint: {"center_x": .5, "center_y": .5}

                MDTextField:
                    id: tf_word
                    hint_text: "Enter Word"
                    pos_hint: {'center_x':0.5,'center_y':0.6}

                MDRectangleFlatButton
                    id: btn_search
                    text: "Search"
                    halign: "center"
                    on_release:
                        app.create_meaning(tf_word.text)
                        panel.switch_tab("files2")

        MDBottomNavigationItem:
            name: "files2"
            text: "Meaning"
            icon: "clipboard-text"
            ScrollView:
                MDList:
                    id: list_answer
                    font_style: "Body1"
                    theme_text_color: "Primary"
                    halign: "center"

        MDBottomNavigationItem:
            name: "files3"
            text: "JS"
            icon: "language-javascript"

            MDLabel:
                font_style: "Body1"
                theme_text_color: "Primary"
                text: "Oh god JS again"
                halign: "center"
"""


class MainApp(MDApp):
    def __init__(self, **kwargs):
        self.title = "wordie"
        super().__init__(**kwargs)

    def callback(self, instance):
        self.root.ids.panel.switch_tab(instance.text)

    def create_meaning(self, instance):
        # print(self.root.ids.tf_word.text)

        dictionary = PyDictionary(self.root.ids.tf_word.text)
        # print(dictionary.printMeanings())
        dic = dictionary.getMeanings()

        # gc = gspread.service_account(filename='wordie-credentials.json')
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        credentials = Credentials.from_service_account_file(
            'wordie-credentials.json',
            scopes=scopes
        )
        client = gspread_db.authorize(credentials)
        db = client.open("wordie")
        if db.table_exists(table_name="wordie_db"):
            print("Yes it exists")
            wordie_dbu = db['wordie_db']
        else:
            print("It does not exist")
            db.create_table(table_name='wordie_db', header=['word', 'meaning'])
            wordie_dbu = db['wordie_db']

        for key in dic.keys():
            # Print the word itself
            item_key = OneLineListItem(text=key.capitalize() + ':')
            self.root.ids.list_answer.add_widget(item_key)
            # wordie_dbu.insert({'word': key.capitalize()})
            print(key.capitalize() + ':')
            for k in dic[key].keys():
                # Print whether it is Noun or Verb etc
                item_k = OneLineListItem(text=k + ':')
                self.root.ids.list_answer.add_widget(item_k)
                print(k + ':')
                # Probably for each line in the string
                wordie_dbu.insert({'word': key.capitalize(), 'meaning': str(dic[key][k])})
                for m in dic[key][k]:
                    item_m = OneLineListItem(text=m)
                    self.root.ids.list_answer.add_widget(item_m)
                    print(m)

    def build(self):
        self.root = Builder.load_string(root_kv)
        self.create_meaning(self.root.ids.tf_word.text)


if __name__ == "__main__":
    MainApp().run()
