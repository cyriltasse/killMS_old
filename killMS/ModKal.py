import getpass
import time

if not(getpass.getuser() in ["tasse","cyril","nadeem"]):
    time.sleep(1)
    exit()
