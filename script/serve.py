# scripts/serve.py
from livereload import Server

server = Server()

# 监控 htmlcov 目录中的所有文件
server.watch('../htmlcov')

# 在 8000 端口启动服务器
server.serve(root='./htmlcov', host='0.0.0.0', port=8000)
