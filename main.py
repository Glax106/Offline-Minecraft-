import customtkinter as ctk
from PIL import Image
import minecraft_launcher_lib
import subprocess
import os
import sys
import threading
import json

# উইন্ডো বেসিক সেটআপ
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Atsenor Client")
root.geometry("800x500")
root.resizable(False, False)

# ডাটা সেভ করার ফাইল পাথ (লঞ্চারের ফোল্ডারেই একটি ছোট JSON ফাইল তৈরি হবে)
CONFIG_FILE = "launcher_config.json"

# আগের সেভ করা ইউজারনেম লোড করার ফাংশন
def load_saved_username():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return data.get("username", "")
        except:
            return ""
    return ""

# নতুন ইউজারনেম সেভ করার ফাংশন
def save_username(username):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"username": username}, f)
    except:
        pass

# রিসোর্স পাথ খোঁজার ফাংশন (EXE বানানোর পর ছবি ও লোগো চেনার জন্য)
def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ১. কাস্টম লোগো/আইকন সেট করা
try:
    logo_path = get_resource_path("logo.ico")
    root.iconbitmap(logo_path)
except:
    pass

# ২. ব্যাকগ্রাউন্ড ছবি সেট করা
try:
    bg_path = get_resource_path("background.png")
    bg_image = ctk.CTkImage(light_image=Image.open(bg_path), 
                            dark_image=Image.open(bg_path), 
                            size=(800, 500))
    bg_label = ctk.CTkLabel(root, image=bg_image, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except:
    pass

# বাম দিকের মেনু প্যানেল
sidebar = ctk.CTkFrame(root, width=200, corner_radius=0, fg_color="transparent")
sidebar.pack(side="left", fill="y")

ctk.CTkLabel(sidebar, text="ATSENOR", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
ctk.CTkButton(sidebar, text="SINGLEPLAYER").pack(pady=10, padx=20)
ctk.CTkButton(sidebar, text="MULTIPLAYER").pack(pady=10, padx=20)
ctk.CTkButton(sidebar, text="SETTINGS").pack(pady=10, padx=20)
ctk.CTkButton(sidebar, text="EXIT", command=root.quit, fg_color="red", hover_color="darkred").pack(side="bottom", pady=20, padx=20)

# ডান দিকের মূল কন্টেন্ট এরিয়া
main_content = ctk.CTkFrame(root, fg_color="transparent")
main_content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

# অফলাইন ইউজারনেম ইনপুট বক্স
ctk.CTkLabel(main_content, text="Enter Offline Username:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(20, 5))
username_entry = ctk.CTkEntry(main_content, placeholder_text="e.g. AtsenorPlayer", width=200)
username_entry.pack(pady=5)

# আগে কোনো নাম সেভ করা থাকলে তা ইনপুট বক্সে অটো-ফিল করা
saved_name = load_saved_username()
if saved_name:
    username_entry.insert(0, saved_name)

# ভার্সন সিলেকশন ড্রপডাউন (মোজাং সার্ভার থেকে সব রিলিজড ভার্সন লোড হবে)
ctk.CTkLabel(main_content, text="Select Version:", font=ctk.CTkFont(size=14)).pack(pady=5)

try:
    all_versions = [v["id"] for v in minecraft_launcher_lib.utils.get_version_list() if v["type"] == "release"]
except:
    all_versions = ["1.21.11", "1.20.4", "1.19.2"] # ব্যাকআপ লিস্ট

version_option = ctk.CTkOptionMenu(main_content, values=all_versions)
version_option.pack(pady=10)

# ব্যাকগ্রাউন্ড থ্রেডে গেম রান করার লজিক (যাতে UI ফ্রিজ বা Not Responding না হয়)
def launch_game_thread():
    typed_username = username_entry.get().strip() or "AtsenorPlayer"
    
    # প্লেয়ার কারেন্টলি যে নামটা টাইপ করেছে, সেটা ফাইলে সেভ/আপডেট করা
    save_username(typed_username)
    
    version = version_option.get() 
    minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
    
    options = {
        "username": typed_username,
        "uuid": "",
        "token": ""
    }
    
    try:
        # ১. গেমের ফাইল ডাউনলোড (আগে ডাউনলোড করা থাকলে এই ধাপটি স্কিপ হবে)
        start_btn.configure(text="Checking Files...", state="disabled")
        minecraft_launcher_lib.install.install_minecraft_version(version, minecraft_directory)
        
        # ২. সঠিক জাভা রানটাইম সেটআপ করা
        start_btn.configure(text="Setting up Java...")
        java_path = minecraft_launcher_lib.runtime.get_executable_pathForVersion(version, minecraft_directory)
        if java_path:
            options["executablePath"] = java_path
            
        # ৩. গেমের রান কমান্ড তৈরি করা
        command = minecraft_launcher_lib.command.get_minecraft_command(version, minecraft_directory, options)
        
        # ৪. কাস্টম লঞ্চার উইন্ডোটি পুরোপুরি বন্ধ করে দেওয়া
        root.destroy()
        
        # ৫. শুধুমাত্র ভ্যানিলা মাইনক্রাফট রান করা
        subprocess.run(command)
        
    except Exception as e:
        print(f"Launch Error: {e}")
        # কোনো এরর হলে বাটন আবার সচল করা (যদি উইন্ডো বন্ধ না হয়ে থাকে)
        try:
            start_btn.configure(text="START", state="normal")
        except:
            pass

def start_game():
    threading.Thread(target=launch_game_thread, daemon=True).start()

# স্টার্ট বাটন
start_btn = ctk.CTkButton(main_content, text="START", width=200, height=50, font=ctk.CTkFont(size=18, weight="bold"), command=start_game)
start_btn.pack(side="bottom", pady=40)

root.mainloop()
                    
