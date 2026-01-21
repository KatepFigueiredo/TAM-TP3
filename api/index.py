import sys
import os

# Adiciona o diretório pai (onde está o app.py) ao path do Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from app import app # O Vercel procura por uma variável chamada 'app' ou 'handler'
