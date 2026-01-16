# 使用 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录下的所有文件到容器中
COPY . /app

# 安装依赖
# 注意：原仓库有 setup.py，我们可以直接安装
RUN pip install --no-cache-dir .

# 设置容器启动命令
# 假设安装后命令是 autoremove-torrents
ENTRYPOINT ["autoremove-torrents"]
# 默认参数，用户运行时可以覆盖
CMD ["--help"]
