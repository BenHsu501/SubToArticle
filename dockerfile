# 使用官方 Python 映像作為基礎映像
# FROM python:latest
FROM subtoarticle:1.0.1

# 設置工作目錄
WORKDIR /app
COPY . .

# 安裝 requirements.txt 中列出的所有依賴及其他需求
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install git+https://github.com/BenHsu501/CopyCraftAPI.git \
    && apt-get update \
    && apt-get install -y sqlite3 ffmpeg vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# 定義容器啟動時執行的命令
# CMD ["python", "yourscript.py"]


