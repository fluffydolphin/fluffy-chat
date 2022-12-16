import sqlite3, sys, socket, hashlib, time, os, hashlib, maskpass, customtkinter, tkinter
from threading import Thread
from tkinter import *
from cryptography.fernet import Fernet


''' Colors '''
MAIN = '\033[38;5;50m'
PLOAD = '\033[38;5;119m'
GREEN = '\033[38;5;47m'
BLUE = '\033[0;38;5;12m'
ORANGE = '\033[0;38;5;214m'
RED = '\033[1;31m'
END = '\033[0m'
BOLD = '\033[1m'


''' MSG Prefixes '''
INFO = f'{MAIN}Info{END}'
EXIT = f'{MAIN}Exited{END}'
WARN = f'{ORANGE}Warning{END}'
IMPORTANT = WARN = f'{ORANGE}Important{END}'
FAILED = f'{RED}Fail{END}'
DEBUG = f'{ORANGE}Debug{END}'
INPUT = f'{BLUE}Input{END}'
REMOTE = WARN = f'{ORANGE}Remote{END}'
CLEAR = f'{PLOAD}CLEARED{END}'


print(f"""{PLOAD}
  ______   __             ______    ______                            __                    __     
 /      \ /  |           /      \  /      \                          /  |                  /  |    
/$$$$$$  |$$ | __    __ /$$$$$$  |/$$$$$$  |__    __         _______ $$ |____    ______   _$$ |_   
$$ |_ $$/ $$ |/  |  /  |$$ |_ $$/ $$ |_ $$//  |  /  |       /       |$$      \  /      \ / $$   |  
$$   |    $$ |$$ |  $$ |$$   |    $$   |   $$ |  $$ |      /$$$$$$$/ $$$$$$$  | $$$$$$  |$$$$$$/   
$$$$/     $$ |$$ |  $$ |$$$$/     $$$$/    $$ |  $$ |      $$ |      $$ |  $$ | /    $$ |  $$ | __ 
$$ |      $$ |$$ \__$$ |$$ |      $$ |     $$ \__$$ |      $$ \_____ $$ |  $$ |/$$$$$$$ |  $$ |/  |
$$ |      $$ |$$    $$/ $$ |      $$ |     $$    $$ |      $$       |$$ |  $$ |$$    $$ |  $$  $$/ 
$$/       $$/  $$$$$$/  $$/       $$/       $$$$$$$ |       $$$$$$$/ $$/   $$/  $$$$$$$/    $$$$/  
                                           /  \__$$ |           {END}fluffy chat v1.0 | fluffydolphin{PLOAD}                       
                                           $$    $$/                                               
                                            $$$$$$/                                                      
{END}""")
    
    

SEPARATOR = "<sep>"
list_of_clients = {}
BUFFER_SIZE = 1024 * 128
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
key = b'fXpsGp9mJFfNYCTtGeB2zpY9bzjPAoaC0Fkcc13COy4='
auth_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


auth_server.bind(("0.0.0.0", 430))
auth_server.listen(100)
s.bind(("0.0.0.0", 431))
s.listen(100)


print(f"\n[{IMPORTANT}] Authentication server running on 0.0.0.0:430")
print(f"[{IMPORTANT}] Chat server running on 0.0.0.0:430\n")


def on_closing(event=None):
    if list_of_clients == None:
        for clients in list_of_clients.values():
            clients.send(Fernet(key).encrypt("/serverexit".encode()))
    s.close()
    app.destroy()
    sys.exit()

def change_appearance_mode(new_appearance_mode):
    customtkinter.set_appearance_mode(new_appearance_mode)

def removeuser():
    username = removeuser_username.get() 
    
    conn = sqlite3.connect("userdata.db")
    cur = conn.cursor()

    username_valid = "SELECT * FROM userdata WHERE username = ?"
    cur.execute(username_valid, (username,))

    if cur.fetchall():
        
        sqliteConnection = sqlite3.connect('userdata.db')
        cursor = sqliteConnection.cursor()

        sql_update_query = """DELETE from userdata where username = ?"""
        cursor.execute(sql_update_query, (username,))
        sqliteConnection.commit()
        
        removeuser_username.set("")
    else:
        print(f"[{INFO}] no user found")
        removeuser_username.set("")

def adduser():
    username = adduser_username.get()
    password = adduser_password.get()
    
    conn = sqlite3.connect("./userdata.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS userdata (
        id INTEGER PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL
    )
    """)
    
    new_username, new_password = username, hashlib.sha256(password.encode()).hexdigest()
    cur.execute("INSERT INTO userdata (username, password) VALUES (?, ?)", (new_username, new_password)) 
    
    conn.commit() 
    
    adduser_username.set("")
    adduser_password.set("")

def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)


def clientthread(client_socket):

    while True:
        try:
            message = Fernet(key).decrypt(client_socket.recv(2048)).decode()
            if message:
                if "/exit" == message:
                    key_list = list(list_of_clients.keys())
                    val_list = list(list_of_clients.values())
                    position = val_list.index(client_socket)
                    username = key_list[position]
                    del list_of_clients[username]
                    client_socket.close()
                    for clients in list_of_clients.values():
                        clients.send(Fernet(key).encrypt(f"{username}: left the chat".encode()))
                    continue
                for clients in list_of_clients.values():
                    clients.send(Fernet(key).encrypt(message.encode()))
            else:
                remove(client_socket)
        except:
            continue


def auth_service(auth_socket):
    auth_socket.send(Fernet(key).encrypt("login".encode()))
    login_info = Fernet(key).decrypt(auth_socket.recv(1024)).decode()
    username, password = login_info.split(SEPARATOR)
    password = hashlib.sha256(password.encode()).hexdigest()

    conn = sqlite3.connect("userdata.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM userdata WHERE username = ? AND password = ?", (username, password))

    if cur.fetchall():
        auth_socket.send(Fernet(key).encrypt("successful".encode()))
        auth_socket.close()
        client_socket, client_address = s.accept()
        for clients in list_of_clients.values():
            clients.send(Fernet(key).encrypt(f"{current_time} @ {username}: joined the chat".encode()))
        list_of_clients[username] = client_socket
        Thread(target=clientthread, args=(client_socket,)).start()
    else:
        auth_socket.send(Fernet(key).encrypt("failed".encode()))
        auth_socket.close()
    

def main():
    while True:
        auth_socket, auth_address = auth_server.accept()
        auth_thread = Thread(target=auth_service, args=(auth_socket,))
        auth_thread.daemon = True
        auth_thread.start()


main_thread = Thread(target=main)
main_thread.daemon = True
main_thread.start()



app = customtkinter.CTk()
app.geometry("235x600")
app.title("fluffy chat")
app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(0, weight=1)

app.frame_left = customtkinter.CTkFrame(master=app, width=180, corner_radius=10)
app.frame_left.grid(row=0, column=0, sticky="nswe", padx=20, pady=20)

app.frame_left.grid_rowconfigure(0, minsize=10) 
app.frame_left.grid_rowconfigure(5, weight=1)
app.frame_left.grid_rowconfigure(8, minsize=20)
app.frame_left.grid_rowconfigure(11, minsize=10)

app.label_2 = customtkinter.CTkLabel(master=app.frame_left, text='fluffy chat', text_font=("Roboto Medium", 22))
app.label_2.grid(row=1, column=0, pady=10, padx=20)


removeuser_username = tkinter.StringVar()

app.adduser_username = customtkinter.CTkLabel(master=app.frame_left, text='Username', text_font=("Roboto Medium", 10))
app.adduser_username.grid(row=2, column=0, pady=5, padx=20, sticky="w")

username_field = customtkinter.CTkEntry(master=app.frame_left, placeholder_text="username", text_font=("Roboto Medium", 12), width=150, height=25, textvariable=removeuser_username)
username_field.grid(row=3, column=0, pady=5, padx=20, sticky="w")

removeuser_button = customtkinter.CTkButton(master=app.frame_left, text="Remove user", command=removeuser, relief='groove', text_font=("Roboto Medium", 11))
removeuser_button.grid(row=4, column=0, pady=30, padx=20, sticky="w")


adduser_username = tkinter.StringVar()
adduser_password = tkinter.StringVar()

app.adduser_username = customtkinter.CTkLabel(master=app.frame_left, text='Username', text_font=("Roboto Medium", 10))
app.adduser_username.grid(row=6, column=0, pady=5, padx=20, sticky="w")

username_field = customtkinter.CTkEntry(master=app.frame_left, placeholder_text="username", text_font=("Roboto Medium", 12), width=150, height=25, textvariable=adduser_username)
username_field.grid(row=7, column=0, pady=5, padx=20, sticky="w")

app.adduser_password = customtkinter.CTkLabel(master=app.frame_left, text='Password', text_font=("Roboto Medium", 10))
app.adduser_password.grid(row=8, column=0, pady=5, padx=20, sticky="w")

password_field = customtkinter.CTkEntry(master=app.frame_left, placeholder_text="password", show="*", text_font=("Roboto Medium", 12), width=150, height=25, textvariable=adduser_password)
password_field.grid(row=9, column=0, pady=5, padx=20, sticky="w")

adduser_button = customtkinter.CTkButton(master=app.frame_left, text="add user", command=adduser, relief='groove', text_font=("Roboto Medium", 11))
adduser_button.grid(row=10, column=0, pady=5, padx=20, sticky="w")


app.label_mode = customtkinter.CTkLabel(master=app.frame_left, text="Appearance Mode:", text_font=("Roboto Medium", 10))
app.label_mode.grid(row=11, column=0, pady=0, padx=20, sticky="w")

app.optionmenu_1 = customtkinter.CTkOptionMenu(master=app.frame_left, values=["System", "Light", "Dark"], command=change_appearance_mode, text_font=("Roboto Medium", 10))
app.optionmenu_1.grid(row=12, column=0, pady=15, padx=20, sticky="w")

app.protocol("WM_DELETE_WINDOW", on_closing)


app.mainloop()


auth_server.close()
s.close()