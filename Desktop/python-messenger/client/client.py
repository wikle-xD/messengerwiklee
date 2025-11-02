import customtkinter as ctk
import socketio
import threading
import time

# Вставь сюда свой Replit URL, пример:
SERVER_URL = "https://a8e743fd-041b-4437-a474-ef1a840df3a7-00-3tts2srispit0.worf.replit.dev"


sio = socketio.Client()
nickname = ""
connected = False  # флаг подключения

# ===== SocketIO события =====
@sio.event
def connect():
    global connected
    connected = True
    sio.emit("set_nickname", nickname)
    add_message("System", "✅ Connected to server")

@sio.event
def disconnect():
    global connected
    connected = False
    add_message("System", "❌ Disconnected from server")

@sio.on("message")
def on_message(data):
    add_message("", data)

def start_sio():
    while True:
        try:
            sio.connect(SERVER_URL)
            sio.wait()
        except Exception as e:
            print(f"Connection failed: {e}, retry in 5 sec")
            time.sleep(5)

# ===== Отправка сообщений =====
def send_message():
    global connected
    msg = entry.get().strip()
    if msg and connected:
        sio.emit("message", msg)
        entry.delete(0, "end")
    elif not connected:
        add_message("System", "⚠ Not connected to server!")

# ===== UI =====
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.geometry("400x600")
root.title("💬 Messenger")

# Поле чата (заблокировано для редактирования вручную)
text_box = ctk.CTkTextbox(root, width=380, height=450, state="disabled")
text_box.pack(padx=10, pady=10)

entry_frame = ctk.CTkFrame(root)
entry_frame.pack(padx=10, pady=5, fill="x")

entry = ctk.CTkEntry(entry_frame, width=300)
entry.pack(side="left", padx=(5, 5), pady=5, fill="x", expand=True)

send_btn = ctk.CTkButton(entry_frame, text="Send", width=70, command=send_message)
send_btn.pack(side="right", padx=5, pady=5)

def add_message(author, msg):
    text_box.configure(state="normal")  # временно разблокируем
    if author:
        text_box.insert("end", f"{author}: {msg}\n")
    else:
        text_box.insert("end", f"{msg}\n")
    text_box.configure(state="disabled")  # снова блокируем
    text_box.see("end")

entry.bind("<Return>", lambda e: send_message())

# ===== Ввод ника =====
def ask_nickname():
    global nickname
    def set_nick():
        global nickname
        nickname = nick_entry.get().strip()
        if nickname:
            nick_window.destroy()
            threading.Thread(target=start_sio, daemon=True).start()
    nick_window = ctk.CTkToplevel(root)
    nick_window.geometry("300x150")
    nick_window.title("Enter your nickname")
    ctk.CTkLabel(nick_window, text="Введите ваш ник:").pack(pady=10)
    nick_entry = ctk.CTkEntry(nick_window)
    nick_entry.pack(pady=10)
    nick_entry.focus()
    ctk.CTkButton(nick_window, text="OK", command=set_nick).pack(pady=10)
    root.wait_window(nick_window)

ask_nickname()
root.mainloop()
