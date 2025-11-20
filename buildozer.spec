[app]
title = Shock Detector
package.name = shockdetector
package.domain = org.test
source.dir = .
version = 0.3
orientation = portrait

# Requirements: filetype (for crash fix), tts (for alarm), libffi_system (for build fix)
requirements = python3,kivy==2.3.1,plyer,filetype,tts,libffi_system

# Permissions: CALL_PHONE is critical
android.permissions = INTERNET, ACCELEROMETER, CALL_PHONE

# Build fixes
android.javac_target_version = 17
android.ndk = 25b
android.cmdline_tools_version = 8512546

[buildozer]
log_level = 2
warn_on_root = 1