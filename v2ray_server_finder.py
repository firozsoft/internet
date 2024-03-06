import base64
import urllib.request

url = "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Splitted-By-Protocol/ss.txt"
secert = str()
with urllib.request.urlopen(url) as response:
    for line in base64.b64decode(response.read()).decode("utf8").splitlines():
        if "🇺🇸" in line or "🇬🇧" in line:
            secert += f"{line}\n"

with open("./ss.txt", "wb") as fl:
    fl.write(base64.b64encode(secert.encode()))
