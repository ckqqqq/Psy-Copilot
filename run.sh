# run.sh

# 打印当前工作目录
echo "Current directory: $(pwd)"

# 列出当前目录的文件
echo "Listing directory contents:"
ls -l

# 打印端口配置和环境变量
echo "PORT: $PORT"
echo "HOST: $HOST"
echo "WEB_PORT: $WEB_PORT"
echo "HTTP_PORT: $HTTP_PORT"

# 运行 Streamlit 应用
python -m streamlit run Main_V2.py --server.port 8000 --server.address 0.0.0.0