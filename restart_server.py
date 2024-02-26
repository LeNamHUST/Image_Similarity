import psutil
import subprocess
import time

def check_ram_usage():
    ram = psutil.virtual_memory()
    ram_usage = ram.available / (1024**3)  
    return ram_usage

def restart_api():
    command = "pm2 restart all"
    subprocess.Popen(command, shell=True)

if __name__ == "__main__":
    while True:
        ram_usage = check_ram_usage()
        print('ram:', ram_usage)
        if ram_usage < 3:
            print('restart 2 process')
            restart_api()
            print('restart end')
        time.sleep(120)