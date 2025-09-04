import socket
import select
import sys
import os
import yaml
from jinja2 import Template

OK_HEADER = """
HTTP/1.1 200 OK\r
Content-Type: text/html\r
Set-Cookie: ServerName=steveserver\r
\r
"""

def load_yaml(yaml_file="./config.yaml"):
    if not os.path.isfile(yaml_file):
        print(f"No {yaml_file} file.\nPlease create a {yaml_file} file and fill it as per the README")
    try:
        with open (yaml_file, "r") as file:
            data = yaml.safe_load(file)
            rawhostaddress = data["hostaddress"]
            rawhostport = data["hostport"]
            try:
                hostport = int(rawhostport)
            except ValueError:
                print(f"String \"{rawhostport}\" cannot be converted to INT")
                exit()
            hostaddress = (rawhostaddress, hostport)
            logs = data["logs"]
            return hostaddress, logs
    except yaml.YAMLError as e:
        print(f"Error with YAML: {e}")
        exit()

def open_file(filename):
    with open(filename, 'r') as file:
        return file.read()
    
def format_file_contents(log_file, break_symbol):
    with open(log_file, "r") as file:
        content = file.read()
    if break_symbol == r"\n":
        raw_log_list = content.splitlines()
    else:
        raw_log_list = content.split(break_symbol)
    log_list = []
    for item in raw_log_list:
        log_list.append(item.replace("\n", "<br>\n"))
    log_list.reverse()
    shortened_log_list = log_list[:50]
    return shortened_log_list

def build_index(logs):
    with open("index.html.template") as file:
        template = Template(file.read())
    return OK_HEADER + template.render(logs=logs)

def build_log_page(log):
    log_file = log["logfile"]
    break_symbol = log.get("breaksymbol", "---")
    try:
        log_contents = format_file_contents(log_file, break_symbol)
    except FileNotFoundError:
        print(f"File does not exist {log_file}")
        return
    with open("log.html.template") as file:
        template = Template(file.read())
    return OK_HEADER + template.render(log=log, log_contents=log_contents)

if __name__ == "__main__":
    hostaddress, logs = load_yaml()

    listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    listener_socket.bind(hostaddress)
    listener_socket.listen(1)
    print(f"Server listening @ {hostaddress[0]}:{hostaddress[1]}")

    index_html = build_index(logs)

    while True:
        read_ready_sockets, _, _ = select.select([listener_socket], [], [], 1)  # Wait up to 1 second

        for ready_socket in read_ready_sockets:
            client_socket, client_address = ready_socket.accept()

            message = client_socket.recv(4096)
            path = message.split()[1].decode('utf-8')

            if path == "" or path == "/":
                http_response = index_html
                print("INDEX")
            if "/log/" in path:
                try:
                    log_index = int(path.split("/")[-1])
                    print(f"Log: {log_index}")
                    http_response = build_log_page(logs[log_index])
                    if http_response is None:
                        http_response = index_html
                except IndexError:
                    print("Index out of range")
                    http_response = index_html
            else:
                print(path)

            client_socket.sendall(http_response.encode("utf-8"))

            try:
                client_socket.close()
            except OSError:
                pass
