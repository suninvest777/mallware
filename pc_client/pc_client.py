"""
PC клиент для просмотра стрима экрана Android и удаленного управления
"""
import socket
import struct
import json
import base64
import threading
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import io


class AndroidRemoteClient:
    """Клиент для подключения к Android устройству"""
    
    def __init__(self, host, port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.is_connected = False
        self.frame_thread = None
        self.current_frame = None
        
    def connect(self):
        """Подключается к Android устройству"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.host, self.port))
            self.is_connected = True
            
            # Запускаем поток для приема кадров
            self.frame_thread = threading.Thread(target=self._receive_frames)
            self.frame_thread.daemon = True
            self.frame_thread.start()
            
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def _receive_frames(self):
        """Принимает кадры от устройства"""
        while self.is_connected:
            try:
                # Читаем размер данных
                size_data = self._recv_all(4)
                if not size_data:
                    break
                
                size = struct.unpack('>I', size_data)[0]
                
                # Читаем JSON данные
                json_data = self._recv_all(size)
                if not json_data:
                    break
                
                message = json.loads(json_data.decode('utf-8'))
                
                if message.get('type') == 'frame':
                    # Декодируем кадр
                    frame_data = base64.b64decode(message['data'])
                    self.current_frame = frame_data
                    
            except Exception as e:
                print(f"Error receiving frame: {e}")
                break
    
    def _recv_all(self, size):
        """Читает все данные указанного размера"""
        data = b''
        while len(data) < size:
            chunk = self.socket.recv(size - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def send_command(self, command_data):
        """Отправляет команду на устройство"""
        if not self.is_connected:
            return False
        
        try:
            json_data = json.dumps(command_data).encode('utf-8')
            size = struct.pack('>I', len(json_data))
            self.socket.sendall(size + json_data)
            return True
        except Exception as e:
            print(f"Error sending command: {e}")
            return False
    
    def send_touch(self, x, y, action='tap'):
        """Отправляет touch событие"""
        return self.send_command({
            'type': 'touch',
            'x': x,
            'y': y,
            'action': action
        })
    
    def send_key(self, key_code):
        """Отправляет нажатие клавиши"""
        return self.send_command({
            'type': 'key',
            'key_code': key_code
        })
    
    def send_swipe(self, x1, y1, x2, y2, duration=300):
        """Отправляет swipe событие"""
        return self.send_command({
            'type': 'swipe',
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'duration': duration
        })
    
    def disconnect(self):
        """Отключается от устройства"""
        self.is_connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass


class RemoteControlGUI:
    """GUI приложение для удаленного управления"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Android Remote Control")
        self.root.geometry("800x600")
        
        self.client = None
        self.canvas = None
        self.last_touch_x = 0
        self.last_touch_y = 0
        
        self._create_ui()
        
    def _create_ui(self):
        """Создает интерфейс"""
        # Панель подключения
        connect_frame = tk.Frame(self.root)
        connect_frame.pack(pady=10)
        
        tk.Label(connect_frame, text="Device IP:").pack(side=tk.LEFT, padx=5)
        self.ip_entry = tk.Entry(connect_frame, width=15)
        self.ip_entry.pack(side=tk.LEFT, padx=5)
        self.ip_entry.insert(0, "192.168.1.100")
        
        tk.Label(connect_frame, text="Port:").pack(side=tk.LEFT, padx=5)
        self.port_entry = tk.Entry(connect_frame, width=5)
        self.port_entry.pack(side=tk.LEFT, padx=5)
        self.port_entry.insert(0, "8888")
        
        self.connect_btn = tk.Button(connect_frame, text="Connect", command=self._connect)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        # Canvas для отображения экрана
        self.canvas = tk.Canvas(self.root, bg="black", width=400, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Привязываем события мыши
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        
        # Панель управления
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=5)
        
        tk.Button(control_frame, text="Back", command=self._send_back).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Home", command=self._send_home).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Menu", command=self._send_menu).pack(side=tk.LEFT, padx=5)
        
        # Обновление кадров
        self._update_frame()
        
    def _connect(self):
        """Подключается к устройству"""
        ip = self.ip_entry.get()
        try:
            port = int(self.port_entry.get())
        except:
            messagebox.showerror("Error", "Invalid port")
            return
        
        self.client = AndroidRemoteClient(ip, port)
        if self.client.connect():
            messagebox.showinfo("Success", "Connected to device")
            self.connect_btn.config(text="Disconnect", command=self._disconnect)
        else:
            messagebox.showerror("Error", "Failed to connect")
    
    def _disconnect(self):
        """Отключается от устройства"""
        if self.client:
            self.client.disconnect()
            self.client = None
        self.connect_btn.config(text="Connect", command=self._connect)
        messagebox.showinfo("Info", "Disconnected")
    
    def _on_click(self, event):
        """Обрабатывает клик мыши"""
        if not self.client or not self.client.is_connected:
            return
        
        # Масштабируем координаты (если нужно)
        x = event.x
        y = event.y
        
        self.last_touch_x = x
        self.last_touch_y = y
        
        self.client.send_touch(x, y, 'down')
    
    def _on_drag(self, event):
        """Обрабатывает перетаскивание мыши"""
        if not self.client or not self.client.is_connected:
            return
        
        x = event.x
        y = event.y
        
        # Отправляем движение
        self.client.send_touch(x, y, 'move')
    
    def _on_release(self, event):
        """Обрабатывает отпускание мыши"""
        if not self.client or not self.client.is_connected:
            return
        
        x = event.x
        y = event.y
        
        self.client.send_touch(x, y, 'up')
    
    def _send_back(self):
        """Отправляет команду Back"""
        if self.client:
            self.client.send_key(4)  # KEYCODE_BACK
    
    def _send_home(self):
        """Отправляет команду Home"""
        if self.client:
            self.client.send_key(3)  # KEYCODE_HOME
    
    def _send_menu(self):
        """Отправляет команду Menu"""
        if self.client:
            self.client.send_key(82)  # KEYCODE_MENU
    
    def _update_frame(self):
        """Обновляет отображение кадра"""
        if self.client and self.client.current_frame:
            try:
                # Декодируем изображение
                image = Image.open(io.BytesIO(self.client.current_frame))
                image = image.resize((400, 600), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                self.canvas.image = photo  # Сохраняем ссылку
            except Exception as e:
                print(f"Error displaying frame: {e}")
        
        # Повторяем через 100ms
        self.root.after(100, self._update_frame)
    
    def run(self):
        """Запускает приложение"""
        self.root.mainloop()


if __name__ == "__main__":
    app = RemoteControlGUI()
    app.run()
