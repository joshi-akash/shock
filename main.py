import kivy
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.modalview import ModalView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform

try:
    from plyer import accelerometer, call, tts
except ImportError:
    print("Plyer not available — running in desktop mode.")
    accelerometer = None
    call = None
    tts = None

kivy.require('2.3.1')

SHOCK_THRESHOLD = 30.0
COUNTDOWN_TIME = 20


class ShockPopup(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.8, 0.4)
        self.auto_dismiss = False
        self.time_left = COUNTDOWN_TIME

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.title_label = Label(text='Shock Detected!', font_size='24sp', bold=True)
        self.countdown_label = Label(text=f'Calling in {self.time_left}s...', font_size='20sp')
        cancel_button = Button(text='CANCEL', font_size='20sp', size_hint_y=0.4,
                               background_color=(0.9, 0.1, 0.1, 1))

        layout.add_widget(self.title_label)
        layout.add_widget(self.countdown_label)
        layout.add_widget(cancel_button)
        self.add_widget(layout)

        cancel_button.bind(on_press=self.on_cancel)
        self.play_alarm()
        self.countdown_event = Clock.schedule_interval(self.update_countdown, 1)

    def play_alarm(self):
        if tts:
            try:
                tts.speak("Shock detected! Tap cancel to prevent emergency call.")
            except Exception as e:
                print(f"TTS error: {e}")

    def update_countdown(self, dt):
        self.time_left -= 1
        self.countdown_label.text = f'Calling in {self.time_left}s...'
        if self.time_left <= 0:
            self.dismiss()
            App.get_running_app().make_emergency_call()
            return False

    def on_cancel(self, instance):
        self.countdown_event.cancel()
        self.dismiss()
        App.get_running_app().is_alert_active = False


class MainScreen(Screen):
    pass


class ShockDetectorApp(App):
    def build(self):
        self.store = JsonStore('shockdetector_storage.json')
        self.is_alert_active = False

        if platform == 'android':
            self.request_android_permissions()
        return MainScreen()

    def on_start(self):
        if self.store.exists('emergency_contact'):
            number = self.store.get('emergency_contact')['number']
            if self.root and 'phone_input' in self.root.ids:
                self.root.ids.phone_input.text = number

        self.enable_accelerometer()
        Clock.schedule_interval(self.check_acceleration, 1.0 / 30.0)

    def request_android_permissions(self):
        try:
            from android.permissions import request_permissions, Permission
            permissions = [Permission.CALL_PHONE, Permission.BODY_SENSORS]
            request_permissions(permissions, self.on_permissions_result)
        except Exception as e:
            print(f"Permission request failed: {e}")

    def on_permissions_result(self, permissions, results):
        if all(results):
            if 'status_label' in self.root.ids:
                self.root.ids.status_label.text = "Monitoring"
        else:
            if 'status_label' in self.root.ids:
                self.root.ids.status_label.text = "Permission denied."

    def enable_accelerometer(self):
        if accelerometer:
            try:
                accelerometer.enable()
            except Exception as e:
                print(f"Accelerometer error: {e}")

    def save_contact(self):
        if not self.root or 'phone_input' not in self.root.ids:
            return
        number = self.root.ids.phone_input.text.strip()
        if number and len(number) >= 5:
            self.store.put('emergency_contact', number=number)
            self.root.ids.status_label.text = f"Saved: {number}"
        else:
            self.root.ids.status_label.text = "Invalid number"

    def on_pause(self):
        if accelerometer:
            try:
                accelerometer.disable()
            except Exception:
                pass
        return True

    def on_resume(self):
        self.enable_accelerometer()

    def check_acceleration(self, dt):
        if self.is_alert_active or not accelerometer:
            return
        val = accelerometer.acceleration
        if not val or all(v is None for v in val):
            return
        try:
            magnitude = (val[0] ** 2 + val[1] ** 2 + val[2] ** 2) ** 0.5
        except TypeError:
            return
        if magnitude > SHOCK_THRESHOLD:
            print(f"Shock detected! Magnitude: {magnitude:.2f}")
            self.trigger_alert()

    def trigger_alert(self):
        if self.is_alert_active:
            return
        self.is_alert_active = True
        popup = ShockPopup()
        popup.open()
        popup.bind(on_dismiss=self.on_alert_dismiss)

    def on_alert_dismiss(self, instance):
        self.is_alert_active = False

    def make_emergency_call(self):
        if not self.store.exists('emergency_contact'):
            if 'status_label' in self.root.ids:
                self.root.ids.status_label.text = "No contact saved"
            return
        number = self.store.get('emergency_contact')['number']
        print(f"Attempting to call {number}")
        if call:
            try:
                call.makecall(tel=number)
            except Exception as e:
                print(f"Call failed: {e}")
                self.root.ids.status_label.text = "Call failed"
        else:
            print("Call not supported on this platform.")


if __name__ == '__main__':
    ShockDetectorApp().run()
