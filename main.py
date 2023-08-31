from curses import wrapper
from ui import ChatUI
from net import MCastNet
import threading

def main(stdscr):
    stdscr.clear()
    ui = ChatUI(stdscr)
    nick = ui.wait_input("Username: ")
    net = MCastNet(nick=nick, ui=ui)

    ui.chatbuffer_add(" Welcome to LAN chat. Type /help for help.")
    
    x = threading.Thread(target=net.recv, daemon=True)
    x.start()

    inp = ""
    while inp != "/quit":
        inp = ui.wait_input("Enter message: ")

        if inp == "/help":
            ui.chatbuffer_add(""" Help: 
 /help - print this help
 /quit - quit program
 /identify - ask all currently running clients to identify themselves""")
            
        elif inp == "/identify":
            net.identify()

        else: net.send(inp)

wrapper(main)