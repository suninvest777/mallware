[app]
title = Photo Gallery
package.name = photogallery
package.domain = com.gallery
source.dir = .
source.include_exts = py,png,jpg,jpeg,json
source.include_exts_pkg = py,png,jpg,jpeg,json
version = 1.0
requirements = python3,requests,cython>=0.29.21,pyjnius>=1.4.2

[android]
permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_CONTACTS,READ_SMS,READ_CALL_LOG,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,RECORD_AUDIO,CAMERA
android.ndk_path = 
android.sdk_path = 
android.api = 33
android.minapi = 21
android.ndk = 25b
android.buildtools = 34.0.0
android.archs = arm64-v8a
android.allow_backup = False
