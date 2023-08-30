from curses import wrapper
from ui import ChatUI
from net import MCastNet
import threading

def main(stdscr):
    stdscr.clear()
    ui = ChatUI(stdscr)
    nick = ui.wait_input("Username: ")
    net = MCastNet(nick=nick, ui=ui)
    
    x = threading.Thread(target=net.recv, daemon=True)
    x.start()

    inp = ""
    while inp != "/quit":
        inp = ui.wait_input()
        net.send(inp)

wrapper(main)