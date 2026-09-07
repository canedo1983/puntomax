[app]
title = PuntoMAX
package.name = puntomax
package.domain = org.puntomax
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,kivymd
orientation = portrait
osx.kivy_version = 2.2.0
osx.macports.use_default_python = 1
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.12.2
[buildozer]
log_level = 2
warn_on_root = 1
