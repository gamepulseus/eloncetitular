import asyncio
import logging
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from telegram_bot import TelegramBroadcaster

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestTelegram")

async def main():
    broadcaster = TelegramBroadcaster()
    logger.info(f"Sending test message to channel: {broadcaster.channel_id}")
    
    welcome_text = (
        "⚽ <b>¡BIENVENIDOS A EL ONCE TITULAR!</b> ⚽\n\n"
        "🤖 <i>Bot de actualización en vivo inicializado correctamente.</i>\n\n"
        "🔥 A partir de este momento recibirás:\n"
        "• ⚽ Goles y Asistencias en tiempo real\n"
        "• 📋 Alineaciones confirmadas antes de cada partido\n"
        "• 🟥 Tarjetas rojas, amarillas y revisiones de VAR\n"
        "• 📊 Resumen de estadísticas al descanso y final del partido\n"
        "• 🚑 Reporte de lesiones y 🔄 Noticias de fichajes\n\n"
        "#ElOnceTitular #FútbolEnVivo"
    )
    
    success = await broadcaster.send_message(welcome_text)
    if success:
        logger.info("✅ Mensaje enviado exitosamente al canal de Telegram!")
    else:
        logger.error("❌ No se pudo enviar el mensaje. Verifica que el bot sea Administrador en el canal.")

if __name__ == "__main__":
    asyncio.run(main())
