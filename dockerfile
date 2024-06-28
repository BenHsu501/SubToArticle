# 使用官方 Python 映像作為基礎映像
FROM python:latest

# 設置工作目錄
WORKDIR /app

# 複製 requirements.txt 到容器中
COPY requirements.txt .

# 安裝 requirements.txt 中列出的所有依賴
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install git+https://github.com/BenHsu501/CopyCraftAPI.git

# 安裝 SQLite3 和 ffmpeg
RUN apt-get update && apt-get install -y sqlite3 ffmpeg

# 清理 apt-get 缓存
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# 複製當前目錄中的所有內容到容器的工作目錄中
COPY . .

# 定義容器啟動時執行的命令
# CMD ["python", "yourscript.py"]


