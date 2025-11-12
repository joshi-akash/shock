[app]
title = Shock Detector
package.name = shockdetector
package.domain = org.yourname
source.dir = .
source.include_exts = py, kv, png, jpg, jpeg, json, txt
version = 1.0

requirements = python3, kivy==2.3.1, plyer
orientation = portrait
fullscreen = 0
android.permissions = CALL_PHONE, BODY_SENSORS, VIBRATE, WAKE_LOCK
android.api = 34
android.minapi = 27
android.sdk = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.enable_androidx = True
icon.filename = %(source.dir)s/icon.png
android.wakelock = True
source.exclude_exts = spec, pyc, pyo, orig, bak
copy_private_data = False
