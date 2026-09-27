[app]
title = System Service
package.name = sysservice
package.domain = com.example
source.dir = .
source.include_exts = py,png,jpg,wav
version = 0.1
requirements = python3,kivy,requests,pyjnius,android
orientation = portrait
fullscreen = 1
android.permissions = INTERNET, VIBRATE, MODIFY_AUDIO_SETTINGS, WAKE_LOCK, FOREGROUND_SERVICE
android.api = 33
android.minapi = 24
android.archs = arm64-v8a
android.allow_backup = False
android.release_artifact = apk