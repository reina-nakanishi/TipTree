import os
import time
import logging
from pathlib import Path
from django.conf import settings

TEMP_DIR = settings.TEMP_DIR

LOG_DIR = settings.LOG_DIR
file_handler = logging.FileHandler(LOG_DIR/"cleanup.log",encoding="utf-8")


# 何秒以上古かったら削除するか（例：24時間 = 86400秒）
EXPIRE_SECONDS = 60 * 60 * 24

def cleanup_temp_files():
    now = time.time()

    for file in TEMP_DIR.glob("*"):
        try:
            if file.is_file():
                # 最終更新時刻
                mtime = file.stat().st_mtime
                # 一定時間以上経っていれば削除
                if now - mtime > EXPIRE_SECONDS:
                    file.unlink()
                    print(f"Deleted: {file}")
        except Exception as e:
            print(f"Failed to delete {file}: {e}")

if __name__ == "__main__":
    cleanup_temp_files()