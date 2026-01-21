import sys
import os

# Adiciona o diretório pai (onde está o app.py) ao path do Python
# Isto é necessário porque o Vercel pode executar este ficheiro noutro contexto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from app import app as application # 'application' é o nome que o Vercel espera
