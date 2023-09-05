import socket
import struct
#import multitasking
from sys import exit as sysexit
from os import _exit as osexit

class MCastNet:
    def __init__(self, nick, ui, port=5005):
        
        self.port = port
        self.nick = nick
        self.nicktable = {}
        self.ui = ui

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        #self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("224.0.0.111", self.port))

        mreq = struct.pack("4sl", socket.inet_aton("224.0.0.111"), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5) # Set TTL

        self.sock.sendto(f"1{self.nick}".encode(), ("224.0.0.111", self.port))

    def send(self, msg: str):
        self.sock.sendto(f"0{msg}".encode(), ("224.0.0.111", self.port))

    def identify(self):
        self.sock.sendto(f"3".encode(), ("224.0.0.111", self.port))

    #@multitasking.task
    def recv(self):
        while True:
            data = self.sock.recvfrom(4096)
            msg, src = (data[0], data[1][0])
            msg = msg.decode()
            
            if msg[0] == "0": # Normal message
                msg = msg[1:]
                if src in self.nicktable:
                    nick = self.nicktable[src]
                else: nick = src
                self.ui.chatbuffer_add(f" {nick}: {msg}")

            elif msg[0] == "1": # Join message
                msg = msg[1:]

                self.nicktable[src] = msg
                self.ui.userlist.append(msg)
                self.ui.redraw_userlist()
                self.ui.chatbuffer_add(f" {msg} joined.")

            elif msg[0] == "2": # Leave message
                msg = msg[1:]
                try:
                    self.ui.userlist.remove(msg)
                    self.ui.redraw_userlist()
                    self.nicktable.pop(src)
                    self.ui.chatbuffer_add(f" {msg} left.")
                except ValueError: pass

            elif msg[0] == "3": # Request for identification
                self.sock.sendto(f"4{self.nick}".encode(), ("224.0.0.111", self.port))

            elif msg[0] == "4": # Response to 3
                msg = msg[1:]
                self.nicktable[src] = msg
                self.ui.userlist.append(msg)
                self.ui.redraw_userlist()

            self.ui.redraw_ui()
    
    def __del__(self):
        self.sock.sendto(f"2{self.nick}".encode(), ("224.0.0.111", self.port))
        #multitasking.killall(None, None)
