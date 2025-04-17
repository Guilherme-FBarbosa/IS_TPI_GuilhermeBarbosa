import sys
import os

sys.path.insert(0, "/var/www/biblionline/servidor/grpc")
sys.path.insert(0, "/var/www/biblionline/servidor/grpc/venv/lib/python3.12/site-packages")  # ajuste se a versão for diferente

from gateway_flask import app as application
