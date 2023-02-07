import sqlite3, sys, socket, hashlib, time, os, hashlib, maskpass, customtkinter, tkinter
from threading import Thread
from tkinter import *
from cryptography.fernet import Fernet


SEPARATOR = "<sep>"
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
key = b'fXpsGp9mJFfNYCTtGeB2zpY9bzjPAoaC0Fkcc13COy4='
auth_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



def change_appearance_mode(new_appearance_mode):
    customtkinter.set_appearance_mode(new_appearance_mode)
    

def send_login(event=None):
    global username
    global server_ip
    server_ip = auth_ip.get()
    server_ip = str(server_ip)
    auth_server.connect((server_ip, 430))
    username  = 'admin'
    password = my_password.get()
    auth_server.send(Fernet(key).encrypt(f"{username}{SEPARATOR}{password}".encode()))
    if Fernet(key).decrypt(auth_server.recv(1024)).decode() == "successful":
        auth_server.close()
        print("successful")
        login_app.destroy()
    else:
        print("failed")
        auth_server.close()
        login_app.destroy()
        sys.exit()


def on_closing_login(event=None):
    try:
        auth_server.send(Fernet(key).encrypt("/exit".encode()))
        auth_server.close()
    except OSError: 
        pass
    login_app.destroy()
    sys.exit()


def on_closing(event=None):
    try:
        s.send(Fernet(key).encrypt("/exit".encode()))
        s.close()
    except OSError: 
        pass
    app.destroy()
    sys.exit()
    

def listen():
    while True:
        output = Fernet(key).decrypt(s.recv(1024)).decode()
        if output == "/serverexit":
            s.close()
            app.destroy()
            sys.exit()
        else: continue

def adduser():
    username = adduser_username.get()
    password = adduser_password.get()
    s.send(Fernet(key).encrypt(f"adduser{SEPARATOR}{username}{SEPARATOR}{password}".encode()))
    output = Fernet(key).decrypt(s.recv(1024)).decode()
    msg_list.insert(tkinter.END, f"")
    msg_list.insert(tkinter.END, f"{output}")
    adduser_username.set("")
    adduser_password.set("")

def removeuser():
    username = removeuser_username.get()
    s.send(Fernet(key).encrypt(f"removeuser{SEPARATOR}{username}".encode()))
    output = Fernet(key).decrypt(s.recv(1024)).decode()
    msg_list.insert(tkinter.END, f"")
    msg_list.insert(tkinter.END, f"{output}")
    removeuser_username.set("")



customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

login_app = customtkinter.CTk()
login_app.geometry("615x400")
login_app.title("Login")
login_app.grid_columnconfigure(1, weight=1)
login_app.grid_rowconfigure(0, weight=1)
login_app.bind("<Return>", send_login)

login_app.login_frame = customtkinter.CTkFrame(master=login_app, width=180, corner_radius=10)
login_app.login_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nswe")


auth_ip = tkinter.StringVar()
my_password = tkinter.StringVar()

login_app.auth_ip = customtkinter.CTkLabel(master=login_app.login_frame, text='Host Address')
login_app.auth_ip.pack(pady=5, padx=60)

auth_ip_field = customtkinter.CTkEntry(master=login_app.login_frame, placeholder_text="Host Address", width=455, height=25, textvariable=auth_ip)
auth_ip_field.pack(pady=20, padx=60)

login_app.login_password = customtkinter.CTkLabel(master=login_app.login_frame, text='Password')
login_app.login_password.pack(pady=5, padx=60)

password_field = customtkinter.CTkEntry(master=login_app.login_frame, placeholder_text="Password", show="*", width=455, height=25, textvariable=my_password)
password_field.pack(pady=10, padx=60)

login_button = customtkinter.CTkButton(master=login_app.login_frame, text="Login", command=send_login)
login_button.pack(pady=20, padx=60)

login_app.protocol("WM_DELETE_WINDOW", on_closing_login)

login_app.mainloop()


s.connect((server_ip, 432))


app = customtkinter.CTk()
app.geometry("1000x650")
app.title("fluffy chat")
app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(0, weight=1)

app.frame_left = customtkinter.CTkFrame(master=app, width=180, corner_radius=10)
app.frame_left.grid(row=0, column=0, sticky="nswe", padx=20, pady=20)

app.frame_right = customtkinter.CTkFrame(master=app, width=180, corner_radius=10)
app.frame_right.grid(row=0, column=1, padx=20, pady=20, sticky="nswe")


app.frame_left.grid_rowconfigure(0, minsize=10) 
app.frame_left.grid_rowconfigure(5, weight=1)
app.frame_left.grid_rowconfigure(8, minsize=20)
app.frame_left.grid_rowconfigure(11, minsize=10)

app.frame_right.rowconfigure((0, 1, 2, 3), weight=1)
app.frame_right.rowconfigure(7, weight=10)
app.frame_right.columnconfigure((0, 1), weight=1)
app.frame_right.columnconfigure(2, weight=0)


app.label_2 = customtkinter.CTkLabel(master=app.frame_left, text='fluffy chat')
app.label_2.grid(row=1, column=0, pady=10, padx=20)


messages_frame = tkinter.Frame(app.frame_right)
my_msg = tkinter.StringVar()
scrollbar = tkinter.Scrollbar(messages_frame, bg='#0f0f0f')
msg_list = tkinter.Listbox(messages_frame, height=10, width=110, yscrollcommand=scrollbar.set, bg="grey38",fg='white')
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack(pady=15, padx=40, fill="both", expand=True)


removeuser_username = tkinter.StringVar()

app.adduser_username = customtkinter.CTkLabel(master=app.frame_left, text='Username')
app.adduser_username.grid(row=2, column=0, pady=5, padx=20, sticky="w")

username_field = customtkinter.CTkEntry(master=app.frame_left, placeholder_text="username", width=150, height=25, textvariable=removeuser_username)
username_field.grid(row=3, column=0, pady=5, padx=20, sticky="w")

removeuser_button = customtkinter.CTkButton(master=app.frame_left, text="Remove user", command=removeuser)
removeuser_button.grid(row=4, column=0, pady=30, padx=20, sticky="w")


adduser_username = tkinter.StringVar()
adduser_password = tkinter.StringVar()

app.adduser_username = customtkinter.CTkLabel(master=app.frame_left, text='Username')
app.adduser_username.grid(row=6, column=0, pady=5, padx=20, sticky="w")

username_field = customtkinter.CTkEntry(master=app.frame_left, placeholder_text="username", width=150, height=25, textvariable=adduser_username)
username_field.grid(row=7, column=0, pady=5, padx=20, sticky="w")

app.adduser_password = customtkinter.CTkLabel(master=app.frame_left, text='Password')
app.adduser_password.grid(row=8, column=0, pady=5, padx=20, sticky="w")

password_field = customtkinter.CTkEntry(master=app.frame_left, placeholder_text="password", show="*", width=150, height=25, textvariable=adduser_password)
password_field.grid(row=9, column=0, pady=5, padx=20, sticky="w")

adduser_button = customtkinter.CTkButton(master=app.frame_left, text="add user", command=adduser)
adduser_button.grid(row=10, column=0, pady=5, padx=20, sticky="w")


app.label_mode = customtkinter.CTkLabel(master=app.frame_left, text="Appearance Mode:")
app.label_mode.grid(row=11, column=0, pady=0, padx=20, sticky="w")

app.optionmenu_1 = customtkinter.CTkOptionMenu(master=app.frame_left, values=["System", "Light", "Dark"], command=change_appearance_mode)
app.optionmenu_1.grid(row=12, column=0, pady=15, padx=20, sticky="w")

app.protocol("WM_DELETE_WINDOW", on_closing)


app.mainloop()