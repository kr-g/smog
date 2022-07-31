import sys
import os
import subprocess
import threading

print(os.getcwd())

cmd = ["-h"]
# cmd = ["config","-h"]
# cmd = ["config","-db-check"]
# cmd = ["config","-db-mig"]
# cmd = ["hash","-h"]
# cmd = ["hash","/home/benutzer/Bilder/20220521.jpeg"]
# cmd = ["xmp","-h"]
# cmd = ["xmp","-types"]
# cmd = ["xmp","-list","/home/benutzer/Bilder/20220521.jpeg"]
# cmd = ["xmp","-list","/home/benutzer/Bilder/20220521.jpeg","-tags"]
# cmd = ["xmp","-list","/home/benutzer/Bilder/20220521.jpeg","-xml"]
# cmd = ["scan", "-h"]
# cmd = ["scan"]
# cmd = ["scan", "/home/benutzer/Bilder/20220508-0609 pfalz" ]
# cmd = ["scan", "/home/benutzer/Bilder/20220508-0609 pfalz", "-tag", "pfalz2" ]
# cmd = ["col", ]
# cmd = ["tag", "-h"]
# cmd = ["tag", "-all"]
# cmd = ["tag", "-tag", "pfalz2", "-rm"]

args = [
    "python3",
    "run_main.py",
    "-timer",
    *cmd,
]
print(args)

proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

while True:
    output = proc.stdout.readline()
    if len(output) == 0:
        break

    print(output.decode(), end="")

rc = proc.poll()
print(rc)
