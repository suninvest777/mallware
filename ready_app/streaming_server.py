"""
WebSocket сервер для стриминга экрана Android на PC
"""
import threading
import socket
import struct
import time
import base64
import json
from datetime import datetime


class StreamingServer:
    """Сервер для стриминга экрана"""
    
    def __init__(self, port=8888):
        self.port = port
        self.server_socket = None
        self.clients = []
        self.is_running = False
        self.thread = None
        self.screen_recorder = None
        
    def start(self):
        """Запускает сервер"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Пробуем привязать к порту
            try:
                self.server_socket.bind(('0.0.0.0', self.port))
            except OSError as e:
                if e.errno == 98 or "Address already in use" in str(e):
                    print(f"Port {self.port} is already in use, trying alternative port...")
                    # Пробуем альтернативный порт
                    self.port = 8889
                    try:
                        self.server_socket.bind(('0.0.0.0', self.port))
                        print(f"Using alternative port: {self.port}")
                    except:
                        print(f"Error binding to port {self.port}: {e}")
                        return False
                else:
                    print(f"Error binding socket: {e}")
                    return False
            
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)  # Таймаут для возможности проверки is_running
            self.is_running = True
            
            # Запускаем сервер в отдельном потоке
            self.thread = threading.Thread(target=self._server_loop, name="StreamingServer")
            self.thread.daemon = True
            self.thread.start()
            
            # Небольшая задержка для проверки запуска
            time.sleep(0.5)
            
            # Запускаем запись экрана (опционально)
            try:
                from screen_recorder import start_background_recording
                self.screen_recorder = start_background_recording()
                if self.screen_recorder:
                    print("Screen recorder started")
            except Exception as e:
                print(f"Screen recorder not available: {e}")
            
            print(f"Streaming server started on port {self.port}")
            return True
        except Exception as e:
            print(f"Error starting streaming server: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _server_loop(self):
        """Основной цикл сервера"""
        print(f"Server loop started, listening on port {self.port}")
        while self.is_running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"New client connected: {address}")
                
                # Обрабатываем клиента в отдельном потоке
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address),
                    name=f"ClientHandler-{address}"
                )
                client_thread.daemon = True
                client_thread.start()
                
                self.clients.append(client_socket)
            except socket.timeout:
                # Таймаут - это нормально, продолжаем цикл
                continue
            except Exception as e:
                if self.is_running:
                    print(f"Error in server loop: {e}")
                    import traceback
                    traceback.print_exc()
                else:
                    # Сервер остановлен, выходим
                    break
    
    def _handle_client(self, client_socket, address):
        """Обрабатывает подключение клиента"""
        try:
            # Отправляем информацию о подключении
            welcome = {
                'type': 'welcome',
                'message': 'Connected to Android device',
                'timestamp': datetime.now().isoformat()
            }
            self._send_json(client_socket, welcome)
            
            # Импортируем remote_control для обработки команд
            try:
                from remote_control import RemoteController
                controller = RemoteController()
            except:
                controller = None
            
            # Цикл отправки кадров и обработки команд
            frame_count = 0
            client_socket.settimeout(0.1)  # Таймаут для проверки команд
            
            while self.is_running:
                try:
                    # Проверяем наличие входящих команд
                    try:
                        client_socket.settimeout(0.05)  # Короткий таймаут
                        size_data = client_socket.recv(4)
                        if size_data and len(size_data) == 4:
                            size = struct.unpack('>I', size_data)[0]
                            command_data = self._recv_all(client_socket, size)
                            if command_data and len(command_data) == size:
                                # Обрабатываем команду
                                if controller:
                                    command_json = json.loads(command_data.decode('utf-8'))
                                    result = controller.handle_command(command_json)
                                    # Отправляем результат обратно
                                    response = {
                                        'type': 'command_result',
                                        'result': result
                                    }
                                    self._send_json(client_socket, response)
                    except socket.timeout:
                        # Нет данных - это нормально
                        pass
                    except socket.error:
                        # Ошибка соединения
                        break
                    finally:
                        client_socket.settimeout(0.1)
                    
                    # Получаем кадр экрана (пока заглушка)
                    frame_data = self._capture_frame()
                    
                    if frame_data:
                        # Отправляем кадр
                        frame_message = {
                            'type': 'frame',
                            'data': base64.b64encode(frame_data).decode('utf-8'),
                            'timestamp': datetime.now().isoformat(),
                            'frame_number': frame_count
                        }
                        self._send_json(client_socket, frame_message)
                        frame_count += 1
                    
                    # Задержка для контроля FPS (например, 10 FPS)
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"Error in client loop: {e}")
                    break
                    
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            try:
                client_socket.close()
                if client_socket in self.clients:
                    self.clients.remove(client_socket)
            except:
                pass
    
    def _capture_frame(self):
        """Захватывает кадр экрана"""
        # Пока что это заглушка
        # Реальная реализация будет использовать screen_recorder
        # или напрямую MediaProjection API
        
        # Для тестирования возвращаем пустые данные
        # В реальной версии здесь будет код захвата кадра
        return None
    
    def _send_json(self, client_socket, data):
        """Отправляет JSON данные клиенту"""
        try:
            json_data = json.dumps(data).encode('utf-8')
            # Отправляем размер данных
            size = struct.pack('>I', len(json_data))
            client_socket.sendall(size + json_data)
        except Exception as e:
            print(f"Error sending JSON: {e}")
    
    def _recv_all(self, sock, size):
        """Читает все данные указанного размера"""
        data = b''
        while len(data) < size:
            chunk = sock.recv(size - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def stop(self):
        """Останавливает сервер"""
        self.is_running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        # Закрываем все клиентские соединения
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        
        # Останавливаем запись экрана
        if self.screen_recorder:
            try:
                self.screen_recorder.stop_recording()
            except:
                pass


def start_streaming_server(port=8888):
    """Запускает сервер стриминга в фоне"""
    server = StreamingServer(port)
    if server.start():
        return server
    return None


def get_device_ip():
    """Получает IP адрес устройства для подключения"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unknown"
