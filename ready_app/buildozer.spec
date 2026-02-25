[app]
title = PhotoView
package.name = photoview
package.domain = com.photo
source.dir = .
source.include_exts = py,png,jpg,jpeg,json
source.include_exts_pkg = py,png,jpg,jpeg,json
version = 1.0
requirements = python3,requests,kivy,cython>=0.29.21,pyjnius>=1.4.2

[android]
permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.ndk_path = 
android.sdk_path = 
android.api = 33
android.minapi = 21
android.ndk = 25b
android.buildtools = 34.0.0
