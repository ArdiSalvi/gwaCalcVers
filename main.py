from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
import requests
import urllib.request
import sys
import os

KV = '''
#:import MDRaisedButton kivymd.uix.button.MDRaisedButton

MDScreen:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            id: overall_grade_label
            title: "GWA: -"
            right_action_items:
                [["menu", lambda x: app.open_menu()], ["download", lambda x: app.check_for_updates()]]

        ScrollView:
            BoxLayout:
                id: subject_container
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height

        Label:
            text: "Add subjects first"
            id: no_subject_added_label
            font_size: '24sp'
            color: 0.7, 0.7, 0.7, 1  # Light gray color
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            size_hint: None, None
            size: self.texture_size
            opacity: 0 if app.subjects else 1  # Hide the label if there are subjects added

        MDBottomAppBar:
            MDTopAppBar:
                title: "GWA Calculator"
                icon: "plus"
                type: "bottom"
                left_action_items: [["menu", lambda x: x]]
                mode: "end"
                on_action_button: app.add_subject()  # Call the add_subject method when the plus button is pressed
'''


class GradeCalculator(MDApp):
    subjects = []
    latest_version_url = "https://raw.githubusercontent.com/ArdiSalvi/gwaCalcVers/main/version.txt"

    def build(self):
        self.theme_cls.material_style = "M2"
        self.theme_cls.primary_palette = "Orange"
        self.dialog = None  # Declare the dialog attribute
        return Builder.load_string(KV)

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
        content = MDBoxLayout(orientation='vertical', size_hint=(1, None), height=130)

        # Create text inputs for Subject Name and GWA
        subject_name_input = MDTextField(hint_text="Subject Name")
        gwa_input = MDTextField(hint_text="GWA")

        # Add the text inputs to the content layout
        content.add_widget(subject_name_input)
        content.add_widget(gwa_input)

        # Create buttons for the dialog
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

        # Create the dialog
        self.dialog = MDDialog(
            title="Add Subject",
            type="custom",
            content_cls=content,
            buttons=[cancel_button, add_subject_button],
        )

        # Open the dialog
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

            # Create a new button for the new subject
            new_subject_button = MDRaisedButton(
                text=f"[size=16][b]{new_subject}[/b][/size]\n[size=14]GWA: {subject_gwa}[/size]",
                size_hint=(1, None),
                height=80,
            )

            # Adjust the button properties
            new_subject_button.font_size = '16sp'
            new_subject_button.md_bg_color = self.theme_cls.accent_color

            self.root.ids.no_subject_added_label.opacity = 0  # Set the opacity to 0 to hide the label

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

    def open_menu(self):
        menu_items = [
            {
                "text": "Check for updates",
                "on_release": self.check_for_updates
            }
        ]

        self.menu = MDDropdownMenu(
            caller=self.root.ids.overall_grade_label.ids.right_actions.children[-1],
            items=menu_items,
            width_mult=4,
        )

        self.menu.open()

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
        current_version = "1.0.4"  # Replace with your current version
        return latest_version > current_version

    def show_update_dialog(self, latest_version):
        update_dialog = MDDialog(
            title="Update Available",
            text=f"A new version ({latest_version}) is available. Do you want to update?",
            buttons=[
                MDFlatButton(text="Cancel", on_release=lambda x: update_dialog.dismiss()),
                MDFlatButton(text="Update", on_release=lambda x: self.open_update_url()),
            ]
        )
        update_dialog.open()

    def open_update_url(self):
        update_url = "https://raw.githubusercontent.com/ArdiSalvi/gwaCalcVers/main/main.py"

        try:
            response = urllib.request.urlopen(update_url)
            new_code = response.read().decode()

            # Check if the new code is different from the current code
            if new_code != open(sys.argv[0]).read():
                with open(sys.argv[0], "w") as file:
                    file.write(new_code)

                print("Application updated successfully.")
                # Restart the application
                os.execv(sys.executable, [sys.executable] + sys.argv)

            else:
                print("Application is already up to date.")
        except Exception as e:
            print("An error occurred while updating the application:", str(e))

    def show_no_update_dialog(self):
        no_update_dialog = MDDialog(
            title="Up to Date",
            text="You already have the latest version installed.",
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
