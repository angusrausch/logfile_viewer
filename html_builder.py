from jinja2 import Template
from log import Log
import os

OK_HEADER = (
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/html\r\n"
    "Set-Cookie: ServerName=logviewer\r\n"
    "\r\n"
)

def build_index(logs):
    with open("index.html") as file:
        template = Template(file.read())
    return OK_HEADER + template.render(logs=logs)

def build_log_page(log, log_file="", back_path="/"):
    log_file = log.log_file if not log_file else log_file
    
    log_contents = log.format_file_contents(log_file)
    
    with open("log.html") as file:
        template = Template(file.read())
    return OK_HEADER + template.render(log=log, log_contents=log_contents, back_path=back_path)

def build_dir_page(log, file_path, path, back_path = "/"):
    contents = log.format_dir_contents(file_path, path)
    
    with open("log_dir.html") as file:
        template = Template(file.read())
    return OK_HEADER + template.render(log=log, contents=contents, back_path=back_path)