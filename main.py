from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivy.properties import StringProperty, ListProperty
from kivymd.theming import ThemableBehavior
from kivymd.uix.list import OneLineIconListItem, MDList
import requests
import urllib.request
import sys
import os
import ssl

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.check_hostname = False

KV = '''
# menu
<ItemDrawer>:
    theme_text_color: "Custom"
    on_release: self.parent.set_color_item(self)

    IconLeftWidget:
        id: icon
        icon: root.icon
        theme_text_color: "Custom"
        text_color: root.text_color

<ContentNavigationDrawer>:
    orientation: "vertical"
    padding: "8dp"
    spacing: "8dp"

    MDLabel:
        text: "GWA Calculator"
        font_style: "Button"
        adaptive_height: True

    MDLabel: 
        text: "Version 1.0.68"
        font_style: "Caption"
        adaptive_height: True

    ScrollView:
        DrawerList:
            id: md_list


MDScreen:
    MDNavigationLayout:
        ScreenManager:
            MDScreen:
                MDBoxLayout:
                    orientation: "vertical"

                    MDTopAppBar:
                        title: "GWA Calculator"
                        anchor_title: "center"
                        elevation: 0
                        left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]

                    ScrollView:
                        BoxLayout:
                            id: subject_container
                            orientation: "vertical"
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: 10

                            Label:
                                text: "GWA: -"
                                id: overall_grade_label
                                font_size: '24sp'
                                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                                size_hint: None, None
                                size: self.texture_size
                                color: 0, 0, 0, 1  # Set the text color to black (RGBA values: 0, 0, 0, 1)
                                bold: True  # Make the text bold
                                adaptive_height: True

                            Label:
                                text: "Please add subjects first"
                                id: no_subject_added_label
                                font_size: '24sp'
                                color: 0.7, 0.7, 0.7, 1  # Light gray color
                                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                                size_hint: None, None
                                size: self.texture_size
                                opacity: 0 if app.subjects else 1  # Hide the label if there are subjects added
                                adaptive_height: True

                    MDBottomAppBar:
                        MDTopAppBar:
                            title: " "
                            icon: "plus"
                            type: "bottom"
                            mode: "end"
                            elevation: 0
                            on_action_button: app.add_subject()
                            left_action_items: [["delete", lambda x: app.show_coming_soon_dialog()]]

                    Widget:

        MDNavigationDrawer:
            id: nav_drawer  

            ContentNavigationDrawer:
                id: content_drawer
'''


class ContentNavigationDrawer(MDBoxLayout):
    pass


class ItemDrawer(OneLineIconListItem):
    icon = StringProperty()
    text_color = ListProperty((0, 0, 0, 1))


class DrawerList(ThemableBehavior, MDList):
    def set_color_item(self, instance_item):
        for item in self.children:
            if item.text_color == self.theme_cls.primary_color:
                item.text_color = self.theme_cls.text_color
                break
        instance_item.text_color = self.theme_cls.primary_color

        if instance_item.text == "Check for Updates":
            self.check_for_updates_dialog()

    def check_for_updates_dialog(self):
        app = MDApp.get_running_app()
        app.check_for_updates()


class GradeCalculator(MDApp):
    subjects = []
    latest_version_url = "https://raw.githubusercontent.com/ArdiSalvi/gwaCalcVers/main/version.txt"

    def build(self):
        self.theme_cls.font_styles.update({
            "H5": ["Roboto", 16, "Bold"],
            "Subtitle2": ["Roboto", 14, "Regular"]
        })
        self.theme_cls.font_base = "Roboto"
        self.theme_cls.material_style = "M2"
        self.theme_cls.primary_palette = "Blue"
        self.dialog = None
        return Builder.load_string(KV)

    def on_start(self):
        icon_item = {
            "folder": "My files",
            "account-multiple": "Shared with me",
            "star": "Starred",
            "download": "Check for Updates"
        }
        for icon_name in icon_item.keys():
            self.root.ids.content_drawer.ids.md_list.add_widget(
                ItemDrawer(icon=icon_name, text=icon_item[icon_name])
            )

    def show_coming_soon_dialog(self):
        coming_soon_dialog = MDDialog(
            title="Feature Coming Soon",
            text="This specific functionality has not been included in the application yet.\n\nPlease be patient and look out for future updates, as it may be added at a later time.",
            buttons=[
                MDFlatButton(text="OK", on_release=lambda x: coming_soon_dialog.dismiss()),
            ]
        )
        coming_soon_dialog.open()

    def calculate_grade(self, instance):
        grades = {}

        grade_inputs = {subject: self.root.ids[subject] for subject in self.subjects}

        for subject, grade_input in grade_inputs.items():
            if len(grade_input.text) > 0:
                try:
                    grades[subject] = float(grade_input.text)
                except ValueError:
                    self.root.ids['overall_grade_label'].text = "Invalid input. Please enter a number."
                    return

        quarter_grade = sum(grades.values()) / len(self.subjects)

        previous_grade_input = self.root.ids['previous_grade_input']
        previous_grade_text = previous_grade_input.text

        if previous_grade_text.strip():
            try:
                previous_grade = float(previous_grade_text)
            except ValueError:
                self.root.ids['overall_grade_label'].text = "Invalid input. Please enter a number."
                return
        else:
            previous_grade = 0.0

        overall_grade = (2 / 3) * quarter_grade + (1 / 3) * previous_grade

        if overall_grade > 1000.00:
            self.root.ids['overall_grade_label'].text = "GWA exceeds 1000.00"
        else:
            self.root.ids['overall_grade_label'].text = f"GWA: {overall_grade:.2f}"

    def clear_inputs(self, instance):
        previous_grade_input = self.root.ids['previous_grade_input']

        for subject in self.subjects:
            self.root.ids[subject].text = ""  # Clear the subject inputs

        previous_grade_input.text = ""  # Clear the previous grade input
        self.root.ids['overall_grade_label'].text = "GWA: "  # Clear the overall grade label

    def add_subject(self):
        # Create the content layout for the dialog
        content = MDBoxLayout(orientation='vertical', size_hint=(1, None), height=200)

        # Create text inputs for Subject Name and GWA
        subject_name_input = MDTextField(hint_text="Subject Name")
        gwa_input = MDTextField(hint_text="GWA")

        content.add_widget(subject_name_input)
        content.add_widget(gwa_input)

        cancel_button = MDFlatButton(
            text="CANCEL",
            theme_text_color="Custom",
            text_color=self.theme_cls.primary_color,
            on_release=self.dismiss_dialog
        )
        add_subject_button = MDFlatButton(
            text="ADD SUBJECT",
            theme_text_color="Custom",
            text_color=self.theme_cls.primary_color,
            on_release=lambda x: self.save_subject(self.dialog, subject_name_input.text, gwa_input.text)
        )

        self.dialog = MDDialog(
            title="Add Subject",
            type="custom",
            content_cls=content,
            buttons=[cancel_button, add_subject_button],
        )

        self.dialog.open()

    def dismiss_dialog(self, instance):
        if self.dialog:
            self.dialog.dismiss()

    def save_subject(self, dialog, subject_name, subject_gwa):
        if subject_name and subject_gwa:
            # Check if the subject name already exists
            for subject_data in self.subjects:
                if subject_name in subject_data:
                    dialog.dismiss()
                    error_dialog = MDDialog(
                        title="Error",
                        text="Subject name already exists. Please enter a different name.",
                        buttons=[
                            MDFlatButton(text="OK", on_release=lambda x: error_dialog.dismiss())
                        ]
                    )
                    error_dialog.open()
                    return

            new_subject = subject_name

            try:
                gwa = float(subject_gwa)
            except ValueError:
                dialog.dismiss()
                error_dialog = MDDialog(
                    title="Error",
                    text="Please enter a valid grade for the GWA.",
                    buttons=[
                        MDFlatButton(text="OK", on_release=lambda x: error_dialog.dismiss())
                    ]
                )
                error_dialog.open()
                return

            self.subjects.append({new_subject: gwa})

            new_subject_button = MDRectangleFlatButton(
                text=f"[size=16][b]Subject: {new_subject}\nGWA: {subject_gwa}[/b][/size]",
                size_hint=(0.5, None),  # Set width to 50% of the available space
                height=80,
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                md_bg_color=(0, 0, 255, 0.8),
                text_color=(1, 1, 1, 1)
            )

            # Adjust the button properties
            new_subject_button.font_size = '30sp'

            self.root.ids.no_subject_added_label.opacity = 0

            # Add the new subject button to the subject_container
            self.root.ids.subject_container.add_widget(new_subject_button)

            dialog.dismiss()
        else:
            # Show an error message if subject name or GWA is empty
            dialog.dismiss()
            error_dialog = MDDialog(
                title="Error",
                text="Please enter both the subject name and GWA.",
                buttons=[
                    MDFlatButton(text="OK", on_release=lambda x: error_dialog.dismiss())
                ]
            )
            error_dialog.open()

    def check_for_updates(self):
        latest_version = self.get_latest_version()
        if latest_version:
            if self.compare_versions(latest_version):
                self.show_update_dialog(latest_version)
            else:
                self.show_no_update_dialog()
        else:
            self.show_error_dialog()

    def get_latest_version(self):
        try:
            response = requests.get(self.latest_version_url)
            if response.status_code == 200:
                return response.text.strip()
        except requests.exceptions.RequestException:
            pass
        return None

    def compare_versions(self, latest_version):
        current_version = "1.0.68"

        # Split the version strings into lists of integers
        current_version_parts = list(map(int, current_version.split(".")))
        latest_version_parts = list(map(int, latest_version.split(".")))

        # Compare each part of the version numbers
        for c, l in zip(current_version_parts, latest_version_parts):
            if l > c:
                return True  # New version is available

        return False  # No new version available

    def show_update_dialog(self, latest_version):
        update_dialog = MDDialog(
            title="Update Available",
            text=f"A new version (v{latest_version}) is available. Do you want to update?",
            buttons=[
                MDFlatButton(text="Later", on_release=lambda x: update_dialog.dismiss()),
                MDFlatButton(text="Update", on_release=lambda x: self.open_update_url()),
            ]
        )
        update_dialog.open()

    def open_update_url(self):
        update_url = "https://raw.githubusercontent.com/ArdiSalvi/gwaCalcVers/main/main.py"

        try:
            context = ssl.create_default_context()  # Create SSL context
            response = urllib.request.urlopen(update_url, context=context)  # Pass the context in urlopen
            new_code = response.read().decode()

            # Check if the new code is different from the current code
            if new_code != open(sys.argv[0]).read():
                with open(sys.argv[0], "w") as file:
                    file.write(new_code)

                update_dialog = MDDialog(
                    title="Update Successful",
                    text="The application has been updated successfully. Please restart the program.",
                    buttons=[
                        MDFlatButton(
                            text="Exit App",
                            on_release=lambda x: os.execv(sys.executable, [sys.executable] + sys.argv)
                        ),
                    ]
                )
                update_dialog.open()
            else:
                no_update_dialog = MDDialog(
                    title="Up to Date",
                    text="You already have the latest version installed.",
                    buttons=[
                        MDFlatButton(text="OK", on_release=lambda x: no_update_dialog.dismiss()),
                    ]
                )
                no_update_dialog.open()
        except Exception as e:
            error_dialog = MDDialog(
                title="Error",
                text="An error occurred while updating the application: " + str(e),
                buttons=[
                    MDFlatButton(text="OK", on_release=lambda x: error_dialog.dismiss()),
                ]
            )
            error_dialog.open()

    def show_no_update_dialog(self):
        current_version = "1.0.68"
        no_update_dialog = MDDialog(
            title="GWA Calculator is up to date",
            text=f"You already have the latest version (v{current_version}) installed.",
            buttons=[
                MDFlatButton(text="OK", on_release=lambda x: no_update_dialog.dismiss()),
            ]
        )
        no_update_dialog.open()

    def show_error_dialog(self):
        error_dialog = MDDialog(
            title="Error",
            text="Failed to check for updates.",
            buttons=[
                MDFlatButton(text="OK", on_release=lambda x: error_dialog.dismiss()),
            ]
        )
        error_dialog.open()


if __name__ == '__main__':
    GradeCalculator().run()
