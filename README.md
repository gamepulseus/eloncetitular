# El Once Titular - Telegram Automation Bot ⚽

Bot de Telegram completamente automatizado para publicar actualizaciones de fútbol minuto a minuto, alineaciones confirmadas, lesiones y fichajes en tiempo real usando la API de **API-Football (v3.football.api-sports.io)**.

## 🚀 Características

- ⚽ **Minuto a Minuto**: Publicación automática de Goles (con anotador, asistencia y marcador).
- 🟥 **Tarjetas Rojas y Amarillas**: Alertas de expulsiones y amonestaciones clave.
- 📺 **Alertas de VAR**: Incidencias revisadas por el árbitro en video.
- 📋 **Alineaciones Confirmadas**: Formaciones tácticas y XI inicial antes del inicio del partido.
- 🚑 **Reporte de Lesiones**: Lesionados del día por liga.
- 🔄 **Noticias de Fichajes**: Mercado de pases y traspasos.
- 🧠 **Antiduplicados**: Almacenamiento de estado para garantizar que ningún evento se publique dos veces.

---

## 🛠️ Requisitos e Instalación

1. **Python 3.10+** instalado.
2. Instalar las dependencias del proyecto:
   ```bash
   pip install -r requirements.txt
   ```

---

## ⚙️ Configuración (.env)

Asegúrate de configurar las variables en el archivo `.env`:

```ini
API_FOOTBALL_KEY=cbb0f106154c72d158f3de7d4db9f27b
API_FOOTBALL_BASE_URL=https://v3.football.api-sports.io

# Telegram
TELEGRAM_BOT_TOKEN=8822719172:AAE_adfmCnxpKBkAtXifH37SE529gHiye70
TELEGRAM_CHANNEL_ID=@ElOnceTitular

# Twitter / X Credentials (developer.twitter.com)
TWITTER_API_KEY=tu_api_key
TWITTER_API_SECRET=tu_api_secret
TWITTER_ACCESS_TOKEN=tu_access_token
TWITTER_ACCESS_TOKEN_SECRET=tu_access_token_secret
TWITTER_BEARER_TOKEN=tu_bearer_token

# Intervalos de escaneo (en segundos)
LIVE_POLL_INTERVAL=30
INJURIES_POLL_INTERVAL=1800

# Ligas objetivo (IDs separados por coma, ej: 39=Premier League, 140=La Liga, 135=Serie A, 2=Champions League)
TARGET_LEAGUES=39,140,135,78,61,2
```

### Pasos para vincular con Twitter / X:
1. Ve al portal de desarrolladores de Twitter: [developer.twitter.com](https://developer.twitter.com).
2. Crea un **Project & App** con permisos de **Read and Write** (Lectura y Escritura).
3. Genera tus claves: **API Key**, **API Key Secret**, **Access Token** y **Access Token Secret**.
4. Pégalas en el archivo `.env` en los campos correspondientes. El bot comenzará automáticamente a publicar cada actualización simultáneamente en Telegram y Twitter/X.

### Pasos para vincular con Telegram:
1. Abre Telegram y busca [@BotFather](https://t.me/BotFather).
2. Crea un bot usando `/newbot` y copia el **HTTP API Token**. Pégalo en `TELEGRAM_BOT_TOKEN`.
3. Agrega tu bot como **Administrador** en tu canal de Telegram con permiso para enviar mensajes.
4. En `TELEGRAM_CHANNEL_ID`, pon el nombre de usuario de tu canal (ejemplo: `@eloncetitular`) o el ID del canal.

---

## 🏃 Ejecución

Para iniciar el bot en segundo plano o consola:
```bash
python main.py
```

Para probar la conexión con la API de API-Football y verificar el consumo de cuota:
```bash
python test_bot.py
```
