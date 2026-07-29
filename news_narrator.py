import logging
import hashlib
import re
import html
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from typing import List, Dict, Any, Optional, Tuple
import httpx
from state_manager import StateManager
from config import GEMINI_API_KEY

logger = logging.getLogger("NewsNarrator")

# Target RSS sources covering Tier 1 insiders, international press, and official press conferences
TARGET_RSS_FEEDS = [
    # Fabrizio Romano & Tier 1 Transfers
    "https://news.google.com/rss/search?q=Fabrizio+Romano+fichajes+OR+transfer+OR+here+we+go&hl=es-419&gl=MX&ceid=MX:es-419",
    # Spanish Press: Marca, AS, Sport, Mundo Deportivo
    "https://news.google.com/rss/search?q=site:marca.com+OR+site:as.com+OR+site:sport.es+OR+site:mundodeportivo.com+fichajes+futbol&hl=es-419&gl=MX&ceid=MX:es-419",
    # International Press: BBC Sport, The Athletic, L'Equipe, Bild
    "https://news.google.com/rss/search?q=site:bbc.com/sport+OR+site:theathletic.com+OR+site:lequipe.fr+OR+site:bild.de+football+transfer&hl=en-US&gl=US&ceid=US:en",
    # Official Press Conferences & Top Clubs (Real Madrid, Barcelona, Man City)
    "https://news.google.com/rss/search?q=%22Real+Madrid%22+OR+%22FC+Barcelona%22+OR+%22Manchester+City%22+OR+Guardiola+OR+Ancelotti+OR+Arteta+declaraciones+OR+conferencia&hl=es-419&gl=MX&ceid=MX:es-419"
]

INVICTOS_SYSTEM_PROMPT = """Eres el redactor estrella de 'El Once Titular', la comunidad deportiva líder. Tu trabajo es transformar noticias deportivas crudas (sobre fichajes, declaraciones de entrenadores o primicias de periodistas como Fabrizio Romano, Marca, AS, BBC, L'Equipe) en publicaciones virales para Telegram con el estilo narrativo único de 'Invictos / Juez Central'.

REGLAS DE ESTILO INVICTOS:
1. TÍTULO EN MAYÚSCULAS IMPACTANTE CON EMOJIS (ej. 🚨 ¡¡BOMBAZO DE ÚLTIMA HORA EN LA PREMIER LEAGUE!! o ⚪ ¡¡EL SUEÑO DEL REAL MADRID SIGUE VIVO!!).
2. PÁRRAFO PRINCIPAL EMOTIVO: Narrado con pasión, mencionando la edad del jugador, su contexto futbolístico, clubes involucrados y el valor de la decisión.
3. CITA A LA FUENTE: Si la noticia menciona a Fabrizio Romano, David Ornstein, Marca, AS, L'Equipe, The Athletic o rueda de prensa oficial, MENTIONALO EXPLÍCITAMENTE (ej. "Según la información confirmada por Fabrizio Romano...").
4. PREGUNTA DE CIERRE EN MAYÚSCULAS: Una frase corta final para generar interacción con los aficionados (ej. ¿HACE BIEN EN SALIR DEL CITY, SEÑORES? o ¿SE IMAGINAN A ESTE CRACK EN EL CAMP NOU?).
5. LÍNEA DE COMPETICIÓN / MERCADO Y HASHTAGS al final (ej. 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League / Mercado de Fichajes \n 🔥 #Fichajes #Mercado #ElOnceTitular).
6. Mantén el idioma strictly en ESPAÑOL fluido y profesional.
7. No uses formato Markdown pesado (solo <b>negrita</b>, <i>cursiva</i> y HTML limpio compatible con Telegram).

Noticia base:
{raw_title}
{raw_summary}
"""

class NewsNarratorEngine:
    def __init__(self):
        self.state_manager = StateManager()
        self.http_client = httpx.AsyncClient(timeout=15.0, follow_redirects=True)

    async def fetch_rss_items(self, feed_url: str) -> List[Dict[str, Any]]:
        """Fetch fresh items from a Google News RSS feed (strictly within last 6 hours)."""
        items = []
        now_utc = datetime.now(timezone.utc)
        max_age = timedelta(hours=6)

        try:
            resp = await self.http_client.get(feed_url)
            if resp.status_code == 200:
                content = resp.text
                item_blocks = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
                for block in item_blocks[:5]:
                    title_m = re.search(r'<title>(.*?)</title>', block, re.DOTALL)
                    link_m = re.search(r'<link>(.*?)</link>', block, re.DOTALL)
                    pub_m = re.search(r'<pubDate>(.*?)</pubDate>', block, re.DOTALL)
                    
                    title = html.unescape(title_m.group(1)).strip() if title_m else ""
                    link = link_m.group(1).strip() if link_m else ""
                    pub_str = pub_m.group(1).strip() if pub_m else ""

                    # Filter out old news by publication date
                    is_fresh = True
                    if pub_str:
                        try:
                            pub_dt = parsedate_to_datetime(pub_str)
                            if now_utc - pub_dt > max_age:
                                is_fresh = False
                        except Exception:
                            pass

                    if is_fresh and title:
                        source_name = ""
                        if " - " in title:
                            parts = title.rsplit(" - ", 1)
                            title = parts[0].strip()
                            source_name = parts[1].strip()

                        items.append({
                            "title": title,
                            "link": link,
                            "source": source_name
                        })
        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_url}: {e}")
        return items

    async def snapshot_news_on_startup(self):
        """Mark all pre-existing news items on startup as processed so old news is never published."""
        logger.info("Initializing startup snapshot for news feeds (suppressing pre-existing news)...")
        for feed in TARGET_RSS_FEEDS:
            items = await self.fetch_rss_items(feed)
            for item in items:
                title = item["title"]
                news_hash = hashlib.md5(title.encode('utf-8')).hexdigest()
                self.state_manager.mark_processed(f"news_{news_hash}")

    async def generate_invictos_post_with_ai(self, raw_title: str, raw_summary: str, source_name: str) -> Optional[str]:
        """Generate narrative Invictos-style Telegram post using Google Gemini API or intelligent template engine."""
        if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY":
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                prompt_text = INVICTOS_SYSTEM_PROMPT.format(
                    raw_title=raw_title,
                    raw_summary=f"{raw_summary} (Fuente: {source_name})" if source_name else raw_summary
                )
                payload = {
                    "contents": [{"parts": [{"text": prompt_text}]}]
                }
                resp = await self.http_client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        generated_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        if generated_text:
                            return generated_text.strip()
            except Exception as e:
                logger.error(f"Error calling Gemini AI API: {e}")

        # Intelligent Fallback Redactor (Invictos style) if GEMINI_API_KEY is not set
        source_tag = f"Según los informes de {source_name}" if source_name else "Según la información de fuentes de élite"
        clean_title = html.escape(raw_title)
        
        return (
            f"🚨 <b>¡¡BOMBAZO EN EL MERCADO DE FICHAJES!!</b>\n\n"
            f"Atención a la información que llega desde Europa. {clean_title}.\n\n"
            f"📝 {source_tag}, las negociaciones y movimientos avanzan rápidamente entre los clubes involucrados. Un movimiento que promete sacudir el panorama del fútbol mundial.\n\n"
            f"¿QUÉ OPINAN DE ESTE MOVIMIENTO, SEÑORES?\n\n"
            f"🌍 <i>Mercado de Fichajes / Primicia Internacional</i>\n"
            f"🔥 #Fichajes #Mercado #ElOnceTitular"
        )

    async def get_latest_news_posts(self) -> List[Tuple[str, str]]:
        """Fetch fresh news items from Tier 1 sources (published < 6h ago), format via AI, and return (post_text, news_id)."""
        posts = []
        for feed in TARGET_RSS_FEEDS:
            items = await self.fetch_rss_items(feed)
            for item in items:
                title = item["title"]
                source = item["source"]
                
                news_hash = hashlib.md5(title.encode('utf-8')).hexdigest()
                news_id = f"news_{news_hash}"
                
                if self.state_manager.is_processed(news_id):
                    continue

                formatted_post = await self.generate_invictos_post_with_ai(
                    raw_title=title,
                    raw_summary=title,
                    source_name=source
                )

                if formatted_post:
                    posts.append((formatted_post, news_id))
                    break
        return posts
