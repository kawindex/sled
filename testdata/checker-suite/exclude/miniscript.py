import json

import parsled


if __name__ == "__main__":
    with open("p01.json", mode="r", encoding="utf-8") as fr:
        data = json.load(fr)
    
    with open("p01-mini.sd", mode="w", encoding="utf-8") as fw:
        s = parsled.to_sled({"outermost": data}, minify=True, ascii_only=True)
        fw.write(s)
