from threading import Thread
import socket, customtkinter, tkinter, sys, time, pyperclip
from cryptography.fernet import Fernet



SEPARATOR = "<sep>"
SEPZ = "<sepz>"
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
key = b'fXpsGp9mJFfNYCTtGeB2zpY9bzjPAoaC0Fkcc13COy4='
auth_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
login_failed = None



def change_appearance_mode(new_appearance_mode):
    customtkinter.set_appearance_mode(new_appearance_mode)
    

def send_login(event=None):
    global auth_server, server_ip, username, room_number
    try:
        try:
            server_ip = auth_ip.get()
            server_ip = str(server_ip)
            auth_server.connect((server_ip, 430))
            username  = my_username.get()
            password = my_password.get()
            room_number = room_num.get()
            auth_server.send(Fernet(key).encrypt(f"{room_number}{SEPARATOR}{username}{SEPARATOR}{password}".encode()))
            out_mesg = Fernet(key).decrypt(auth_server.recv(1024)).decode()
            if out_mesg == "successful":
                auth_server.close()
                login_app.destroy()
            if out_mesg == "already in":
                auth_server.close()
                login_failed.configure(text="This user is already logged in")
                auth_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if out_mesg == "failed":
                auth_server.close()
                login_failed.configure(text="Invalid username or password")
                auth_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.gaierror:
            login_failed.configure(text="Invalid IP address")
    except TimeoutError:
        login_failed.configure(text="Connection failed")


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
        s.send(Fernet(key).encrypt(f"{room_number}{SEPZ}/exit".encode()))
        s.close()
    except OSError: 
        pass
    app.destroy()
    sys.exit()
    

def send(event=None):
    while True:
        msg = my_msg.get()
        if msg == "/exit":
            s.send(Fernet(key).encrypt(msg.encode()))
            s.close()
            s.close()
            sys.exit()
        s.send(Fernet(key).encrypt(f"{room_number}{SEPZ}{username} @ {current_time}{SEPARATOR}{msg}".encode()))
        my_msg.set("")
        break

def listen():
    while True:
        try:
            output_user, output = Fernet(key).decrypt(s.recv(1024)).decode().split(SEPARATOR)
            if output == "/serverexit":
                s.close()
                app.destroy()
                sys.exit()
            msg_list.insert(tkinter.END, f"")
            msg_list.insert(tkinter.END, f"{output_user}")
            msg_list.insert(tkinter.END, f"{output}")
            msg_list.yview(tkinter.END)
        except:
            break
        
def copy_room_key():
    pyperclip.copy(room_number)
           


customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

login_app = customtkinter.CTk()
login_app.geometry("380")
login_app.title("Login")
login_app.grid_columnconfigure(1, weight=1)
login_app.grid_rowconfigure(0, weight=1)
login_app.bind("<Return>", send_login)

login_app.login_frame = customtkinter.CTkFrame(master=login_app, width=10, corner_radius=10)
login_app.login_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nswe")


auth_ip = tkinter.StringVar()
my_username = tkinter.StringVar()
my_password = tkinter.StringVar()
room_num = tkinter.StringVar()

login_app.auth_ip = customtkinter.CTkLabel(master=login_app.login_frame, text='Host Address')
login_app.auth_ip.pack(pady=7, padx=60)

auth_ip_field = customtkinter.CTkEntry(master=login_app.login_frame, placeholder_text="Host Address", width=200, height=25, textvariable=auth_ip)
auth_ip_field.pack(pady=7, padx=60)

login_app.login_username = customtkinter.CTkLabel(master=login_app.login_frame, text='Username')
login_app.login_username.pack(pady=7, padx=60)

username_field = customtkinter.CTkEntry(master=login_app.login_frame, placeholder_text="Username", width=200, height=25, textvariable=my_username)
username_field.pack(pady=7, padx=60)

login_app.login_password = customtkinter.CTkLabel(master=login_app.login_frame, text='Password')
login_app.login_password.pack(pady=7, padx=60)

password_field = customtkinter.CTkEntry(master=login_app.login_frame, placeholder_text="Password", show="*", width=200, height=25, textvariable=my_password)
password_field.pack(pady=7, padx=60)

login_app.room_num = customtkinter.CTkLabel(master=login_app.login_frame, text='Room Name/Number')
login_app.room_num.pack(pady=7, padx=60)

room_num_field = customtkinter.CTkEntry(master=login_app.login_frame, placeholder_text="Room Number", width=200, height=25, textvariable=room_num)
room_num_field.pack(pady=7, padx=60)


login_button = customtkinter.CTkButton(master=login_app.login_frame, text="Login", command=send_login)
login_button.pack(pady=20, padx=60)

login_failed = customtkinter.CTkLabel(master=login_app.login_frame, text='')
login_failed.pack(pady=5, padx=60)

login_app.protocol("WM_DELETE_WINDOW", on_closing_login)

login_app.mainloop()


s.connect((server_ip, 431))


app = customtkinter.CTk()
app.geometry("1000x650")
app.title("fluffy chat")
app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(0, weight=1)


app.bind("<Return>", send)

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


app.label_2 = customtkinter.CTkLabel(master=app.frame_left, text='fluffy chat', font=("Roboto Medium", 20))
app.label_2.grid(row=1, column=0, pady=10, padx=20)


copy_room_key_button = customtkinter.CTkButton(master=app.frame_left, text="Copy Room Key", command=copy_room_key)
copy_room_key_button.grid(row=3, column=0, pady=10, padx=20)


messages_frame = tkinter.Frame(app.frame_right)
my_msg = tkinter.StringVar()
scrollbar = tkinter.Scrollbar(messages_frame, bg='#0f0f0f')
msg_list = tkinter.Listbox(messages_frame, height=10, width=110, yscrollcommand=scrollbar.set, bg="grey38",fg='white', font=("Roboto Medium", 12))
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack(pady=15, padx=40, fill="both", expand=True)

entry_field = customtkinter.CTkEntry(master=app.frame_right, placeholder_text="command", width=500, height=25, textvariable=my_msg)
entry_field.pack(pady=20, padx=60)
send_button = customtkinter.CTkButton(master=app.frame_right, text="Send", command=send)
send_button.pack(pady=20, padx=60)


app.label_mode = customtkinter.CTkLabel(master=app.frame_left, text="Appearance Mode:")
app.label_mode.grid(row=11, column=0, pady=0, padx=20, sticky="w")

app.optionmenu_1 = customtkinter.CTkOptionMenu(master=app.frame_left, values=["System", "Light", "Dark"], command=change_appearance_mode)
app.optionmenu_1.grid(row=12, column=0, pady=15, padx=20, sticky="w")


app.label_username = customtkinter.CTkLabel(master=app.frame_left, text=f"Logged in as {username}")
app.label_username.grid(row=13, column=0, pady=15, padx=20, sticky="w")


app.protocol("WM_DELETE_WINDOW", on_closing)

Thread(target=listen).start()

app.mainloop()


auth_server.close()
s.close()