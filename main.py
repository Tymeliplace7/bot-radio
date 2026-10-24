# --- EJECUCIÓN SIMULTÁNEA SEGURA ---
if __name__ == '__main__':
  # 1. Iniciar Flask en un hilo independiente para satisfacer el health check de Render
  threading.Thread(target=run_flask, daemon=True).start()

  # 2. Iniciar bot con manejo de rate limit y reconexión suave
  token = os.environ.get('DISCORD_TOKEN')
  if not token:
    print('❌ ERROR: Variable DISCORD_TOKEN no configurada.')
  else:
    print('Iniciando servicio...')
    while True:
      try:
        bot.run(token)
        break
      except discord.errors.HTTPException as e:
        if e.status == 429:
          print(
              '⚠️ Discord/Cloudflare aplicó Rate Limit. Esperando 60 segundos'
              ' para reintentar...'
          )
          import time

          time.sleep(60)
        else:
          print(f'❌ Error HTTP en bot: {e}')
          break
      except Exception as e:
        print(f'❌ Error inesperado: {e}')
        break
