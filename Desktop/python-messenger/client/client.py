import tkinter as tk
from websocket import create_connection
import threading

# Вставь сюда URL сервера из Replit, например "wss://<имя>.username.repl.co/socket.io/?EIO=4&transport=websocket"
WS_URL = "wss://YOUR_REPL_URL/socket.io/?EIO=4&transport=websocket"
ws = create_connection(WS_URL)

def send_message():
    msg = entry.get()
    ws.send(msg)
    entry.delete(0, tk.END)

def receive_messages():
    while True:
        msg = ws.recv()
        text_box.insert(tk.END, msg + "\n")

root = tk.Tk()
root.title("Messenger")

text_box = tk.Text(root)
text_box.pack()

entry = tk.Entry(root)
entry.pack()
send_btn = tk.Button(root, text="Send", command=send_message)
send_btn.pack()

threading.Thread(target=receive_messages, daemon=True).start()
root.mainloop()
