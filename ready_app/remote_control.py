"""
Модуль для удаленного управления Android устройством
Принимает команды и выполняет их (touch события, команды и т.д.)
"""
import subprocess
import threading
import json
import struct
import socket


class RemoteController:
    """Класс для удаленного управления устройством"""
    
    def __init__(self, server_socket=None):
        self.server_socket = server_socket
        self.is_running = False
        
    def handle_command(self, command_data):
        """Обрабатывает команду от PC"""
        try:
            cmd_type = command_data.get('type')
            
            if cmd_type == 'touch':
                return self._handle_touch(command_data)
            elif cmd_type == 'key':
                return self._handle_key(command_data)
            elif cmd_type == 'command':
                return self._handle_shell_command(command_data)
            elif cmd_type == 'swipe':
                return self._handle_swipe(command_data)
            else:
                return {'success': False, 'error': 'Unknown command type'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_touch(self, data):
        """Обрабатывает touch событие"""
        try:
            x = data.get('x', 0)
            y = data.get('y', 0)
            action = data.get('action', 'tap')  # tap, down, up
            
            # Используем adb команду для отправки touch события
            if action == 'tap':
                cmd = f"input tap {x} {y}"
            elif action == 'down':
                cmd = f"input touchscreen swipe {x} {y} {x} {y} 100"
            elif action == 'up':
                cmd = f"input touchscreen swipe {x} {y} {x} {y} 1"
            else:
                cmd = f"input tap {x} {y}"
            
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=2)
            
            return {
                'success': result.returncode == 0,
                'command': cmd,
                'output': result.stdout
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_swipe(self, data):
        """Обрабатывает swipe событие"""
        try:
            x1 = data.get('x1', 0)
            y1 = data.get('y1', 0)
            x2 = data.get('x2', 0)
            y2 = data.get('y2', 0)
            duration = data.get('duration', 300)
            
            cmd = f"input touchscreen swipe {x1} {y1} {x2} {y2} {duration}"
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=2)
            
            return {
                'success': result.returncode == 0,
                'command': cmd
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_key(self, data):
        """Обрабатывает нажатие клавиши"""
        try:
            key_code = data.get('key_code')
            
            if not key_code:
                return {'success': False, 'error': 'key_code not provided'}
            
            cmd = f"input keyevent {key_code}"
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=2)
            
            return {
                'success': result.returncode == 0,
                'command': cmd
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_shell_command(self, data):
        """Выполняет shell команду"""
        try:
            command = data.get('command')
            
            if not command:
                return {'success': False, 'error': 'command not provided'}
            
            # Безопасность: ограничиваем доступные команды
            allowed_commands = ['getprop', 'dumpsys', 'pm', 'am']
            if not any(command.startswith(cmd) for cmd in allowed_commands):
                return {'success': False, 'error': 'Command not allowed'}
            
            result = subprocess.run(command.split(), capture_output=True, text=True, timeout=5)
            
            return {
                'success': result.returncode == 0,
                'command': command,
                'output': result.stdout[:1000],  # Ограничиваем размер вывода
                'error': result.stderr[:500] if result.stderr else None
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_touch_event(self, x, y, action='tap'):
        """Отправляет touch событие через pyjnius (более надежно)"""
        try:
            from jnius import autoclass
            
            MotionEvent = autoclass('android.view.MotionEvent')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            
            mActivity = PythonActivity.mActivity
            
            # Создаем touch событие
            if action == 'down':
                event = MotionEvent.obtain(
                    0, 0, MotionEvent.ACTION_DOWN, x, y, 0
                )
            elif action == 'up':
                event = MotionEvent.obtain(
                    0, 0, MotionEvent.ACTION_UP, x, y, 0
                )
            else:
                # Tap = down + up
                event_down = MotionEvent.obtain(
                    0, 0, MotionEvent.ACTION_DOWN, x, y, 0
                )
                event_up = MotionEvent.obtain(
                    0, 0, MotionEvent.ACTION_UP, x, y, 0
                )
                mActivity.dispatchTouchEvent(event_down)
                mActivity.dispatchTouchEvent(event_up)
                return True
            
            mActivity.dispatchTouchEvent(event)
            return True
            
        except ImportError:
            # Fallback к adb команде
            return self._handle_touch({'x': x, 'y': y, 'action': action})['success']
        except Exception as e:
            return False
    
    def send_text(self, text):
        """Отправляет текст на устройство"""
        try:
            # Экранируем специальные символы
            escaped_text = text.replace(' ', '%s').replace('&', '\\&')
            cmd = f"input text {escaped_text}"
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=2)
            return result.returncode == 0
        except Exception as e:
            return False


def process_remote_command(command_json):
    """Обрабатывает команду от удаленного клиента"""
    controller = RemoteController()
    try:
        command_data = json.loads(command_json)
        result = controller.handle_command(command_data)
        return result
    except Exception as e:
        return {'success': False, 'error': str(e)}
