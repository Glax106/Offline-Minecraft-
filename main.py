import customtkinter as ctk
from PIL import Image
import minecraft_launcher_lib
import subprocess
import os

# উইন্ডো সেটআপ
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Atsenor Client")
root.geometry("800x500")

# ব্যাকগ্রাউন্ড ছবি সেট করা (যদি background.png আপলোড করা থাকে)
try:
    bg_image = ctk.CTkImage(light_image=Image.open("background.png"), 
                            dark_image=Image.open("background.png"), 
                            size=(800, 500))
    bg_label = ctk.CTkLabel(root, image=bg_image, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except:
    pass # ছবি না পেলে সাধারণ ব্যাকগ্রাউন্ড দেখাবে

# বাম দিকের মেনু
sidebar = ctk.CTkFrame(root, width=200, corner_radius=0, fg_color="transparent")
sidebar.pack(side="left", fill="y")

ctk.CTkLabel(sidebar, text="ATSENOR", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
ctk.CTkButton(sidebar, text="SINGLEPLAYER").pack(pady=10, padx=20)
ctk.CTkButton(sidebar, text="MULTIPLAYER").pack(pady=10, padx=20)
ctk.CTkButton(sidebar, text="SETTINGS").pack(pady=10, padx=20)
ctk.CTkButton(sidebar, text="EXIT", command=root.quit, fg_color="red", hover_color="darkred").pack(side="bottom", pady=20, padx=20)

# ডান দিকের মেইন এরিয়া
main_content = ctk.CTkFrame(root, fg_color="transparent")
main_content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

# ইউজারনেম ইনপুট
ctk.CTkLabel(main_content, text="Enter Offline Username:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(20, 5))
username_entry = ctk.CTkEntry(main_content, placeholder_text="e.g. AtsenorPlayer", width=200)
username_entry.pack(pady=5)

# ভার্সন সিলেক্ট
ctk.CTkLabel(main_content, text="Select Version:", font=ctk.CTkFont(size=14)).pack(pady=5)
version_option = ctk.CTkOptionMenu(main_content, values=["1.21.11", "1.20.4", "1.19.2"])
version_option.pack(pady=10)

# গেম স্টার্ট লজিক
def start_game():
    typed_username = username_entry.get()
    if not typed_username:
        typed_username = "AtsenorPlayer"
        
    version = version_option.get() 
    minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
    
    options = {
        "username": typed_username,
        "uuid": "",
        "token": ""
    }
    
    # বাটন টেক্সট পরিবর্তন করে ইউজারকে বোঝানো যে গেম লোড হচ্ছে
    start_btn.configure(text="Loading Game...")
    root.update()
    
    minecraft_launcher_lib.install.install_minecraft_version(version, minecraft_directory)
    command = minecraft_launcher_lib.command.get_minecraft_command(version, minecraft_directory, options)
    subprocess.run(command)
    
    start_btn.configure(text="START") # গেম খেলা শেষ হলে বাটন আবার আগের মতো হবে

start_btn = ctk.CTkButton(main_content, text="START", width=200, height=50, font=ctk.CTkFont(size=18, weight="bold"), command=start_game)
start_btn.pack(side="bottom", pady=40)

root.mainloop()

