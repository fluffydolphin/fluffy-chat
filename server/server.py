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
    
    

n = 0
SEPARATOR = "<sep>"
list_of_clients = {}
list_of_admins = {}
BUFFER_SIZE = 1024 * 128
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
key = b'fXpsGp9mJFfNYCTtGeB2zpY9bzjPAoaC0Fkcc13COy4='
auth_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
admin_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


auth_server.bind(("0.0.0.0", 430))
auth_server.listen(100)
s.bind(("0.0.0.0", 431))
s.listen(100)
admin_server.bind(("0.0.0.0", 432))
admin_server.listen(100)


admin_passowrd = input(f"[{INPUT}] Enter admin password: ")

conn = sqlite3.connect("./userdata.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS userdata (
    id INTEGER PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
)
""")

new_username, new_password = "admin", hashlib.sha256(admin_passowrd.encode()).hexdigest()
cur.execute("INSERT INTO userdata (username, password) VALUES (?, ?)", (new_username, new_password)) 

conn.commit() 


print(f"\n[{IMPORTANT}] Authentication server running on 0.0.0.0:430")
print(f"[{IMPORTANT}] Chat server running on 0.0.0.0:431\n")


def change_appearance_mode(new_appearance_mode):
    customtkinter.set_appearance_mode(new_appearance_mode)

def removeuser(username, admin_socket):
    
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
        
        admin_socket.send(Fernet(key).encrypt(f"Successfully removed {username}".encode()))
    else:
        admin_socket.send(Fernet(key).encrypt(f"Failed to remove {username}".encode()))


def adduser(username, password, admin_socket):
    
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

    admin_socket.send(Fernet(key).encrypt(f"Successfully added {username}".encode()))


def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)
        
def remove_admin(connection):
    if connection in list_of_admins:
        list_of_admins.remove(connection)


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
                    print(f"[{INFO}] {username}: left the chat\n")
                    msg = ": left the chat"
                    for clients in list_of_clients.values():
                        clients.send(Fernet(key).encrypt(f"{username} @ {current_time}{msg}{SEPARATOR}".encode()))
                    continue
                for clients in list_of_clients.values():
                    clients.send(Fernet(key).encrypt(message.encode()))
            else:
                remove(client_socket)
        except:
            continue
        
        
def adminthread(admin_socket):

    while True:
        try:
            message = Fernet(key).decrypt(admin_socket.recv(2048)).decode()
            if message:
                if "/exit" == message:
                    key_list = list(list_of_admins.keys())
                    val_list = list(list_of_admins.values())
                    position = val_list.index(admin_socket)
                    username = key_list[position]
                    del list_of_clients[username]
                    admin_socket.close()
                    print(f"[{INFO}] admin {username}: left the chat\n")
                    continue
                if "removeuser" in message:
                    cringe, user = message.split(SEPARATOR)
                    removeuser(user, admin_socket)
                if "adduser" in message:
                    cringe, username, passowrd = message.split(SEPARATOR)
                    adduser(username, passowrd, admin_socket)
            else:
                remove_admin(admin_socket)
        except:
            continue



def auth_service(auth_socket, n):
    auth_socket.send(Fernet(key).encrypt("login".encode()))
    login_info = Fernet(key).decrypt(auth_socket.recv(1024)).decode()
    username, password = login_info.split(SEPARATOR)
    password = hashlib.sha256(password.encode()).hexdigest()

    conn = sqlite3.connect("userdata.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM userdata WHERE username = ? AND password = ?", (username, password))

    if cur.fetchall():
        if username == "admin":
            print(f"[{INFO}] Successful admin login\n")
            auth_socket.send(Fernet(key).encrypt("successful".encode()))
            auth_socket.close() 
            admin_socket, admin_address = admin_server.accept()
            list_of_admins[n] = admin_socket
            Thread(target=adminthread, args=(admin_socket,)).start()
            n += 1
        else:
            print(f"[{INFO}] Successful login as: {username}\n")
            auth_socket.send(Fernet(key).encrypt("successful".encode()))
            auth_socket.close()
            client_socket, client_address = s.accept()
            msg = ": joined the chat"
            for clients in list_of_clients.values():
                clients.send(Fernet(key).encrypt(f"{username} @ {current_time}{msg}{SEPARATOR}".encode()))
            list_of_clients[username] = client_socket
            Thread(target=clientthread, args=(client_socket,)).start()
    else:
        print(f"[{INFO}] Failed login\n")
        auth_socket.send(Fernet(key).encrypt("failed".encode()))
        auth_socket.close()
    

while True:
    auth_socket, auth_address = auth_server.accept()
    auth_thread = Thread(target=auth_service, args=(auth_socket, n))
    auth_thread.daemon = True
    auth_thread.start()




auth_server.close()
s.close()