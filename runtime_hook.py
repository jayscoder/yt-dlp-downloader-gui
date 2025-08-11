import os
import sys
import certifi

# 在运行时设置SSL证书路径
if hasattr(sys, '_MEIPASS'):
    # PyInstaller打包后的路径
    cert_path = os.path.join(sys._MEIPASS, 'certifi', 'cacert.pem')
    if os.path.exists(cert_path):
        os.environ['SSL_CERT_FILE'] = cert_path
        os.environ['REQUESTS_CA_BUNDLE'] = cert_path
    else:
        # 尝试使用certifi默认路径
        os.environ['SSL_CERT_FILE'] = certifi.where()
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
else:
    # 开发环境
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()