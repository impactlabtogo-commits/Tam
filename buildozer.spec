[app]
title = Tam
package.name = tam
package.domain = org.impactlab
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,flet,requests,urllib3,idna,certifi,charset-normalizer
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.build_tools_version = 33.0.0
android.accept_sdk_license = True

# Cibler exclusivement armeabi-v7a garantit une compatibilité maximale sur les téléphones Itel / Tecno et un build stable
android.archs = armeabi-v7a
