from server import run, load_yaml

import pytest
import threading
import time
import requests
import os

@pytest.fixture(scope="session")
def yaml():
    yaml_output = load_yaml()
    host_address = f"{yaml_output[0][0]}:{yaml_output[0][1]}"
    logs = yaml_output[1]
    return host_address, logs

def make_request(address):
    try:
        return requests.get(f"http://{address}", timeout=3)        

    except requests.exceptions.ConnectionError:
        pytest.fail("Failed to connect to the server. Is it running?")

def check_string_order(string, substrings):
    substring_index = 0
    for substring in substrings:
        index = string.find(substring)
        # Asserts that string is in order 
        assert index >= substring_index
        substring_index = index

@pytest.fixture(scope="session")
def server():
    stop_server_flag = threading.Event()
    thread = threading.Thread(target=run, args=(stop_server_flag,), daemon=True)
    thread.start()
    time.sleep(1)
    yield
    stop_server_flag.set()
    thread.join(timeout=5)

def test_index_page(server, yaml):
    """Tests that the server's home page returns a 200 OK status."""
    host_address = yaml[0]
    logs = yaml[1]

    response = make_request(host_address)

    assert response.status_code == 200
    
    assert "Welcome To LogFileViewer" in response.text

    for keyword in logs:
        assert keyword in response.text

def test_basic_log(server, yaml):
    host_address = yaml[0]
    request_address = f"{host_address}/log/basic"

    response = make_request(request_address)

    sub_strings_in_order = [
        "ENDFILE",
        "STARTFILE"
    ]
    check_string_order(response.text, sub_strings_in_order)

def test_compressed_log(server, yaml):
    host_address = yaml[0]
    request_address = f"{host_address}/log/compressed"

    response = make_request(request_address)

    sub_strings_in_order = [
        "ENDFILE",
        "STARTFILE",
    ]
    check_string_order(response.text, sub_strings_in_order)

def test_break_char(server, yaml):
    host_address = yaml[0]
    request_address = f"{host_address}/log/break_char"

    response = make_request(request_address)

    sub_strings_in_order = [
        "THIS SHOULD BE THE FIRST LINE",
        "THIS IS THE END NOW :)",
        "TEST THE BREAK CHAR",
        "ANOTHER LINE",
        "THIS SHOULD BE THE LAST LINE"
    ]
    check_string_order(response.text, sub_strings_in_order)

def test_directory(server, yaml):
    host_address = yaml[0]
    log = yaml[1]["directory"]
    request_address = f"{host_address}/log/directory"

    response = make_request(request_address)
    
    directory_contents = os.listdir(log.log_file)

    for directory_item in directory_contents:
        assert directory_item in response.text

def test_sub_directory(server, yaml):
    host_address = yaml[0]
    log = yaml[1]["directory"]
    request_address = f"{host_address}/log/directory/directory"

    response = make_request(request_address)
    
    directory_contents = os.listdir(log.log_file + "/directory")

    for directory_item in directory_contents:
        assert directory_item in response.text

