import os
import subprocess
from flask import Flask

app = Flask('')


@app.route('/')
def home():
  return 'Bot Radio Online 24/7'


# Inicia bot.py como un proceso independiente en segundo plano
subprocess.Popen(['python', 'bot.py'])

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 8080))
  app.run(host='0.0.0.0', port=port)
