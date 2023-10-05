import os
import shutil 
from threading import Thread
import subprocess
def installer(path):
    os.system("pyinstaller "+path)

if(os.path.isdir("dist")):
    shutil.rmtree("dist")

installer("giftedGun.spec")

shutil.copy("icon.png", "dist/giftedGun/icon.png")
shutil.copy("main.ui", "dist/giftedGun/main.ui")
shutil.copytree("drivers","dist/giftedGun/drivers")
shutil.copy("dist/giftedGun/giftedGun.exe", "dist/giftedGun/giftedGun_console.exe")
shutil.make_archive("dist/giftedGun", 'zip', "dist/giftedGun")