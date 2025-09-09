import gzip
import os

class Log:
    def __init__(self, log):
        self.name = log.get('name')
        self.log_file = log.get('logfile')
        self.break_symbol = log.get('breaksymbol', '\n')
        self.remote = log.get('remote', False)

    def format_file_contents(self, log_file = ""):
        log_file = self.log_file if not log_file else log_file
        try:
            if ".gz" in log_file:
                with gzip.open(log_file, 'rb') as file:
                    content = file.read().decode('utf-8')
            else:
                with open(log_file, "r") as file:
                    content = file.read()
        except FileNotFoundError:
            print(f"File does not exist {log_file}")
            return
        except gzip.BadGzipFile:
            print(f"Error in unzipping {log_file}")
        if self.break_symbol == r"\n":
            raw_log_list = content.splitlines()
        else:
            raw_log_list = content.split(self.break_symbol)
        log_list = []
        for item in raw_log_list:
            log_list.append(item.replace("\n", "<br>\n"))
        log_list.reverse()
        # shortened_log_list = log_list[:50]
        return log_list
    
    def file_path(self, path):
        real_path = "/".join(path.split("/")[1:])
        return "/".join((self.log_file, real_path))
    
    def format_dir_contents(self, file_path, path):
        raw_contents = os.listdir(file_path)
        contents = []
        for content in raw_contents:
            content_real_path = "/".join((path, content))
            if os.path.isfile(file_path):
                contents.append({"name": content, "path": content_real_path, "type": "File"})
            elif os.path.isdir(file_path):
                contents.append({"name": content, "path": content_real_path, "type": "Dir"})
        return contents