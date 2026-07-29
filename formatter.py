from typing import Dict, Any, List, Optional
import html
import re

# Comprehensive dictionary to translate English API terms into clean Spanish
DETAIL_TRANSLATIONS = {
    # Cards
    "Yellow Card": "Tarjeta Amarilla",
    "Red Card": "Tarjeta Roja",
    "Yellow Card x2": "Doble Amarilla (Expulsión)",
    
    # Goals
    "Normal Goal": "Gol",
    "Penalty": "Penal",
    "Own Goal": "Gol en propia puerta",
    "Missed Penalty": "Penal fallado",
    "Penalty Missed": "Penal fallado",

    # VAR Phrases
    "Penalty awarded": "Penal concedido por el árbitro",
    "Goal Under Review - offside": "Gol en revisión por fuera de juego",
    "Goal Disallowed - offside": "Gol anulado por fuera de juego",
    "Goal Awarded": "Gol confirmado por VAR",
    "Penalty Under Review": "Penal en revisión por VAR",
    "Penalty Disallowed": "Penal no concedido por VAR",
    "Penalty Awarded": "Penal concedido por VAR",
    "Penalty confirmed": "Penal confirmado por VAR",
    "Penalty cancelled": "Penal anulado por VAR",
    "Goal cancelled": "Gol anulado por VAR",
    "Goal confirmed": "Gol confirmado por VAR",
    "Card upgrade": "Tarjeta roja tras revisión de VAR",
    "Offside": "Fuera de juego",
    "Handball": "Mano en el área",
    "Red card cancelled": "Tarjeta roja anulada por VAR",

    # Transfers
    "Free agent": "Agente Libre / Traspaso Libre",
    "Loan": "Préstamo / Cesión",
    "Transfer": "Traspaso Oficial",

    # Injury Types
    "Questionable": "Duda para el partido",
    "Out": "Baja confirmada",
    "Suspended": "Suspendido"
}

VAR_WORD_REPLACEMENTS = [
    (r"\bPenalty awarded\b", "Penal concedido"),
    (r"\bGoal Under Review\s*-\s*offside\b", "Gol en revisión por fuera de juego"),
    (r"\bGoal Disallowed\s*-\s*offside\b", "Gol anulado por fuera de juego"),
    (r"\bGoal Under Review\b", "Gol en revisión por VAR"),
    (r"\bGoal Disallowed\b", "Gol anulado por VAR"),
    (r"\bGoal Awarded\b", "Gol concedido por VAR"),
    (r"\bPenalty Under Review\b", "Penal en revisión por VAR"),
    (r"\bPenalty Disallowed\b", "Penal no concedido por VAR"),
    (r"\bPenalty Awarded\b", "Penal concedido por VAR"),
    (r"\bCard Upgrade\b", "Tarjeta roja tras revisión de VAR"),
    (r"\boffside\b", "Fuera de Juego"),
    (r"\bhandball\b", "Mano en el área"),
    (r"\bfoul\b", "Falta"),
    (r"\bpenalty confirmed\b", "Penal confirmado por VAR"),
    (r"\bgoal cancelled\b", "Gol anulado por VAR"),
    (r"\bgoal confirmed\b", "Gol confirmado por VAR"),
    (r"\bUnder Review\b", "En revisión por VAR"),
    (r"\bDisallowed\b", "Anulado por VAR"),
    (r"\bAwarded\b", "Concedido por VAR"),
    (r"\bConfirmed\b", "Confirmado por VAR"),
    (r"\bCancelled\b", "Anulado por VAR")
]

ROUND_TRANSLATIONS = {
    "Round of 32": "16vos de Final",
    "Round of 16": "Octavos de Final",
    "Quarter-finals": "Cuartos de Final",
    "Quarter-Finals": "Cuartos de Final",
    "Semi-finals": "Semifinales",
    "Semi-Finals": "Semifinales",
    "Final": "Final",
    "Group Stage": "Fase de Grupos",
    "1st Round": "1ª Ronda",
    "2nd Round": "2ª Ronda",
    "3rd Round": "3ª Ronda",
    "Preliminary Round": "Ronda Preliminar",
    "Qualifying Round": "Fase Previa",
    "Play-offs": "Playoffs",
    "Regular Season": "Fase Regular"
}

COUNTRY_FLAGS = {
    "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "Spain": "🇪🇸",
    "Italy": "🇮🇹",
    "Germany": "🇩🇪",
    "France": "🇫🇷",
    "Argentina": "🇦🇷",
    "Brazil": "🇧🇷",
    "Mexico": "🇲🇽",
    "USA": "🇺🇸",
    "Saudi-Arabia": "🇸🇦",
    "Saudi Arabia": "🇸🇦",
    "Venezuela": "🇻🇪",
    "Portugal": "🇵🇹",
    "Netherlands": "🇳🇱",
    "Belgium": "🇧🇪",
    "Turkey": "🇹🇷",
    "Colombia": "🇨🇴",
    "Chile": "🇨🇱",
    "Uruguay": "🇺🇾",
    "Ecuador": "🇪🇨",
    "Peru": "🇵🇪",
    "Paraguay": "🇵🇾",
    "Bolivia": "🇧🇴"
}

def auto_translate_text(text: str) -> str:
    """Intelligently translate any API string (VAR details, comments, injuries, transfers) to clean Spanish."""
    if not text:
        return ""
        
    text_clean = text.strip()
    if text_clean in DETAIL_TRANSLATIONS:
        return DETAIL_TRANSLATIONS[text_clean]

    res = text_clean
    for pattern, replacement in VAR_WORD_REPLACEMENTS:
        res = re.sub(pattern, replacement, res, flags=re.IGNORECASE)

    return res.strip()

def translate_round(round_str: str) -> str:
    """Translate tournament rounds/stages into clean Spanish."""
    if not round_str:
        return ""
        
    if round_str in ROUND_TRANSLATIONS:
        return ROUND_TRANSLATIONS[round_str]

    if "Regular Season - " in round_str:
        num = round_str.replace("Regular Season - ", "").strip()
        return f"Fecha {num}"
    
    if "Group Stage - " in round_str:
        num = round_str.replace("Group Stage - ", "").strip()
        return f"Fase de Grupos ({num})"

    if "Fecha " in round_str:
        return round_str

    if "Clausura - " in round_str:
        num = round_str.replace("Clausura - ", "").strip()
        return f"Clausura - Fecha {num}"

    if "Apertura - " in round_str:
        num = round_str.replace("Apertura - ", "").strip()
        return f"Apertura - Fecha {num}"

    res = round_str
    for en, es in ROUND_TRANSLATIONS.items():
        res = re.sub(re.escape(en), es, res, flags=re.IGNORECASE)

    return res

def safe_escape(val: Any) -> str:
    """Safely convert value to string and escape HTML entities, handling None gracefully."""
    if val is None or val == "None" or val == "N/A":
        return ""
    return html.escape(str(val))

def extract_fixture_meta(fixture: Dict[str, Any]) -> Dict[str, str]:
    """Extract clean metadata: country flag for domestic leagues, trophy emoji for international cups."""
    fix_info = fixture.get('fixture', {})
    league_info = fixture.get('league', {})
    venue_info = fix_info.get('venue', {})

    stadium = safe_escape(venue_info.get('name'))
    city = safe_escape(venue_info.get('city'))
    venue_str = f"{stadium} ({city})" if stadium and city else (stadium or city or "")

    raw_round = safe_escape(league_info.get('round'))
    round_str = translate_round(raw_round)
    
    league_name = safe_escape(league_info.get('name'))
    raw_country = safe_escape(league_info.get('country'))

    # Flag emoji for domestic leagues, Trophy emoji for international cups
    flag_emoji = COUNTRY_FLAGS.get(raw_country)
    
    is_international_cup = (
        raw_country in ["World", "Europe", "South-America", "Asia", "Africa", "North-America"] or
        any(k in league_name.lower() for k in ["champions", "europa", "conference", "libertadores", "sudamericana", "world cup", "nations league", "copa america"])
    )

    if is_international_cup or not flag_emoji:
        icon = "🏆"
    else:
        icon = flag_emoji

    league_full = league_name
    if round_str:
        league_full += f" - {round_str}"

    return {
        "venue": venue_str,
        "league": f"{icon} <i>{league_full}</i>",
        "league_name": league_name,
        "icon": icon
    }

def format_penalty_awarded(event: Dict[str, Any], fixture: Dict[str, Any]) -> str:
    """Format alert when referee awards a penalty before it is taken."""
    meta = extract_fixture_meta(fixture)
    home_team = safe_escape(fixture['teams']['home']['name'])
    away_team = safe_escape(fixture['teams']['away']['name'])
    home_score = fixture['goals']['home'] if fixture['goals']['home'] is not None else 0
    away_score = fixture['goals']['away'] if fixture['goals']['away'] is not None else 0
    
    elapsed = event.get('time', {}).get('elapsed', '')
    extra = event.get('time', {}).get('extra')
    time_str = f"{elapsed}+{extra}'" if extra else f"{elapsed}'"
    
    team_name = safe_escape(event.get('team', {}).get('name'))
    team_str = f"\n👤 <b>Equipo a favor:</b> {team_name}" if team_name else ""

    return (
        f"🎯 <b>¡PENAL CONCEDIDO!</b> ({time_str})\n"
        f"{meta['league']}\n\n"
        f"<b>{home_team} {home_score} - {away_score} {away_team}</b>{team_str}\n"
        f"📝 <b>Incidencia:</b> El árbitro ha cobrado falta dentro del área\n\n"
        f"#Penal #ElOnceTitular"
    )

def format_goal(event: Dict[str, Any], fixture: Dict[str, Any]) -> str:
    meta = extract_fixture_meta(fixture)
    home_team = safe_escape(fixture['teams']['home']['name'])
    away_team = safe_escape(fixture['teams']['away']['name'])
    home_score = fixture['goals']['home'] if fixture['goals']['home'] is not None else 0
    away_score = fixture['goals']['away'] if fixture['goals']['away'] is not None else 0
    
    elapsed = event.get('time', {}).get('elapsed', '')
    extra = event.get('time', {}).get('extra')
    time_str = f"{elapsed}+{extra}'" if extra else f"{elapsed}'"
    
    team_name = safe_escape(event.get('team', {}).get('name'))
    player_name = safe_escape(event.get('player', {}).get('name')) or "Desconocido"
    assist_name = safe_escape(event.get('assist', {}).get('name'))
    detail = event.get('detail', '') or ""
    comments = str(event.get('comments') or "").lower()

    # Penalty Missed / Saved / Off-target
    if "Missed Penalty" in detail or "Penalty Missed" in detail or "missed" in comments or "saved" in comments:
        is_saved = "saved" in comments or "keeper" in comments or "atajado" in comments or "parada" in comments or "stop" in comments
        if is_saved:
            return (
                f"🧤 <b>¡PENAL ATAJADO POR EL PORTERO!</b> ({time_str})\n"
                f"{meta['league']}\n\n"
                f"<b>{home_team} {home_score} - {away_score} {away_team}</b>\n\n"
                f"👤 <b>Cobrador:</b> {player_name} ({team_name})\n"
                f"🧤 <b>Incidencia:</b> ¡El guardameta adivinó el disparo y tapó el penal!\n\n"
                f"#Penal #ElOnceTitular"
            )
        else:
            return (
                f"❌ <b>¡PENAL FALLADO!</b> ({time_str})\n"
                f"{meta['league']}\n\n"
                f"<b>{home_team} {home_score} - {away_score} {away_team}</b>\n\n"
                f"👤 <b>Cobrador:</b> {player_name} ({team_name})\n"
                f"📝 <b>Incidencia:</b> El disparo salió desviado / al poste\n\n"
                f"#Penal #ElOnceTitular"
            )

    goal_title = "¡GOOOOOOL DE PENAL!" if "Penalty" in detail else "¡GOOOOOOL!"
    goal_emoji = "🎯 ⚽" if "Penalty" in detail else "⚽"
    goal_type_text = ""
    if "Own Goal" in detail:
        goal_type_text = " (Gol en Propia Puerta 🤦‍♂️)"
    elif "Penalty" in detail:
        goal_type_text = " (De Penal 🎯)"

    assist_text = f"\n🎯 <b>Asistencia:</b> {assist_name}" if assist_name else ""
    
    return (
        f"{goal_emoji} <b>{goal_title}</b> ({time_str})\n"
        f"{meta['league']}\n\n"
        f"<b>{home_team} {home_score} - {away_score} {away_team}</b>\n\n"
        f"👤 <b>Anotador:</b> {player_name} ({team_name}){goal_type_text}"
        f"{assist_text}\n\n"
        f"🔥 #EnVivo #ElOnceTitular"
    )

def format_card(event: Dict[str, Any], fixture: Dict[str, Any]) -> str:
    meta = extract_fixture_meta(fixture)
    home_team = safe_escape(fixture['teams']['home']['name'])
    away_team = safe_escape(fixture['teams']['away']['name'])
    home_score = fixture['goals']['home'] if fixture['goals']['home'] is not None else 0
    away_score = fixture['goals']['away'] if fixture['goals']['away'] is not None else 0
    
    elapsed = event.get('time', {}).get('elapsed', '')
    extra = event.get('time', {}).get('extra')
    time_str = f"{elapsed}+{extra}'" if extra else f"{elapsed}'"
    
    team_name = safe_escape(event.get('team', {}).get('name'))
    player_name = safe_escape(event.get('player', {}).get('name')) or "Desconocido"
    detail = event.get('detail', '') or ""
    
    is_red = "Red Card" in detail or "Yellow Card x2" in detail
    card_emoji = "🟥" if is_red else "🟨"
    title = "¡TARJETA ROJA!" if is_red else "¡TARJETA AMARILLA!"
    detail_es = auto_translate_text(detail)

    return (
        f"{card_emoji} <b>{title}</b> ({time_str})\n"
        f"{meta['league']}\n\n"
        f"<b>{home_team} {home_score} - {away_score} {away_team}</b>\n\n"
        f"👤 <b>Jugador:</b> {player_name} ({team_name})\n"
        f"📝 <b>Detalle:</b> {safe_escape(detail_es)}\n\n"
        f"#EnVivo #ElOnceTitular"
    )

def format_subst(event: Dict[str, Any], fixture: Dict[str, Any]) -> str:
    meta = extract_fixture_meta(fixture)
    home_team = safe_escape(fixture['teams']['home']['name'])
    away_team = safe_escape(fixture['teams']['away']['name'])
    home_score = fixture['goals']['home'] if fixture['goals']['home'] is not None else 0
    away_score = fixture['goals']['away'] if fixture['goals']['away'] is not None else 0
    
    elapsed = event.get('time', {}).get('elapsed', '')
    extra = event.get('time', {}).get('extra')
    time_str = f"{elapsed}+{extra}'" if extra else f"{elapsed}'"
    
    team_name = safe_escape(event.get('team', {}).get('name'))
    player_out = safe_escape(event.get('player', {}).get('name')) or "Jugador"
    player_in = safe_escape(event.get('assist', {}).get('name')) or "Jugador"

    return (
        f"🔄 <b>CAMBIO / SUSTITUCIÓN</b> ({time_str})\n"
        f"{meta['league']}\n\n"
        f"<b>{home_team} {home_score} - {away_score} {away_team}</b>\n\n"
        f"🛡️ <b>Equipo:</b> {team_name}\n"
        f"🟢 <b>Entra:</b> {player_in}\n"
        f"🔴 <b>Sale:</b> {player_out}\n\n"
        f"#Cambio #ElOnceTitular"
    )

def format_var(event: Dict[str, Any], fixture: Dict[str, Any]) -> str:
    meta = extract_fixture_meta(fixture)
    home_team = safe_escape(fixture['teams']['home']['name'])
    away_team = safe_escape(fixture['teams']['away']['name'])
    home_score = fixture['goals']['home'] if fixture['goals']['home'] is not None else 0
    away_score = fixture['goals']['away'] if fixture['goals']['away'] is not None else 0
    
    elapsed = event.get('time', {}).get('elapsed', '')
    time_str = f"{elapsed}'"
    detail = event.get('detail', '') or ""
    detail_es = auto_translate_text(detail) or "Revisión de VAR"
    
    comments = event.get('comments') or ""
    comments_es = auto_translate_text(comments) if comments else ""
    comm_text = f"\n💬 <b>Decisión:</b> {safe_escape(comments_es)}" if comments_es else ""

    # Check if VAR awarded a penalty
    if "penalty awarded" in detail.lower() or "penalty confirmed" in detail.lower():
        return format_penalty_awarded(event, fixture)
    
    return (
        f"📺 <b>¡REVISIÓN DE VAR!</b> ({time_str})\n"
        f"{meta['league']}\n\n"
        f"<b>{home_team} {home_score} - {away_score} {away_team}</b>\n\n"
        f"📋 <b>Incidencia:</b> {safe_escape(detail_es)}{comm_text}\n\n"
        f"#VAR #ElOnceTitular"
    )

def format_match_status(fixture: Dict[str, Any], status_code: str, statistics: Optional[List[Dict[str, Any]]] = None) -> str:
    meta = extract_fixture_meta(fixture)
    home_team = safe_escape(fixture['teams']['home']['name'])
    away_team = safe_escape(fixture['teams']['away']['name'])
    home_score = fixture['goals']['home'] if fixture['goals']['home'] is not None else 0
    away_score = fixture['goals']['away'] if fixture['goals']['away'] is not None else 0

    status_map = {
        "1H": "🟢 <b>¡INICIA EL PRIMER TIEMPO! ¡ARRANCA EL PARTIDO!</b>",
        "HT": "⏸️ <b>¡FINAL DEL PRIMER TIEMPO! DESCANSO</b>",
        "2H": "🟢 <b>¡INICIA EL SEGUNDO TIEMPO!</b>",
        "ET": "⏱️ <b>¡INICIA EL TIEMPO EXTRA!</b>",
        "BT": "⏸️ <b>PAUSA ANTES DEL TIEMPO EXTRA / PENALES</b>",
        "P": "🎯 <b>¡INICIA LA TANDA DE PENALES!</b>",
        "FT": "🏁 <b>¡FINAL DEL PARTIDO!</b>",
        "AET": "🏁 <b>¡FINAL DEL PARTIDO (TRAS TIEMPO EXTRA)!</b>",
        "PEN": "🏆 <b>¡FINAL DEL PARTIDO (DEFINIDO EN PENALES)!</b>",
        "SUSP": "⚠️ <b>¡PARTIDO SUSPENDIDO!</b>",
        "INT": "⚠️ <b>¡PARTIDO INTERRUMPIDO!</b>",
        "PST": "📅 <b>PARTIDO APLAZADO</b>",
        "CANC": "🚫 <b>PARTIDO CANCELADO</b>",
        "ABD": "❌ <b>PARTIDO ABANDONADO</b>"
    }

    header = status_map.get(status_code)
    if not header:
        return ""

    # Build stats text if available for HT or FT
    stats_text = ""
    if statistics and len(statistics) >= 2 and status_code in ["HT", "FT", "AET", "PEN"]:
        try:
            home_stats = {item['type']: item['value'] for item in statistics[0].get('statistics', [])}
            away_stats = {item['type']: item['value'] for item in statistics[1].get('statistics', [])}
            
            h_poss = home_stats.get('Ball Possession', '50%')
            a_poss = away_stats.get('Ball Possession', '50%')
            h_shots = home_stats.get('Total Shots', 0)
            a_shots = away_stats.get('Total Shots', 0)
            h_ontarget = home_stats.get('Shots on Goal', 0)
            a_ontarget = away_stats.get('Shots on Goal', 0)
            h_corners = home_stats.get('Corner Kicks', 0)
            a_corners = away_stats.get('Corner Kicks', 0)
            h_yellows = home_stats.get('Yellow Cards', 0) or 0
            a_yellows = away_stats.get('Yellow Cards', 0) or 0
            h_reds = home_stats.get('Red Cards', 0) or 0
            a_reds = away_stats.get('Red Cards', 0) or 0

            stats_text = (
                f"\n📊 <b>ESTADÍSTICAS DEL PARTIDO:</b>\n"
                f"⚽ <b>Posesión:</b> {h_poss} - {a_poss}\n"
                f"🎯 <b>Tiros a puerta:</b> {h_ontarget} - {a_ontarget}\n"
                f"👟 <b>Tiros totales:</b> {h_shots} - {a_shots}\n"
                f"🚩 <b>Córners:</b> {h_corners} - {a_corners}\n"
                f"🟨 <b>Tarjetas amarillas:</b> {h_yellows} - {a_yellows}\n"
                f"🟥 <b>Tarjetas rojas:</b> {h_reds} - {a_reds}\n"
            )
        except Exception:
            stats_text = ""

    return (
        f"{header}\n"
        f"{meta['league']}\n\n"
        f"<b>{home_team} {home_score} - {away_score} {away_team}</b>\n"
        f"{stats_text}\n"
        f"#ElOnceTitular #MinutoAMinuto"
    )

def format_lineup(lineups: List[Dict[str, Any]], fixture: Dict[str, Any]) -> str:
    if not lineups or len(lineups) < 2:
        return ""
        
    meta = extract_fixture_meta(fixture)
    home_team = safe_escape(fixture['teams']['home']['name'])
    away_team = safe_escape(fixture['teams']['away']['name'])

    home_lineup = lineups[0]
    away_lineup = lineups[1]

    def build_xi(lineup_data):
        formation = lineup_data.get('formation', '4-3-3')
        start_xi = lineup_data.get('startXI', [])
        players = [f"• {safe_escape(p['player']['name'])}" for p in start_xi]
        return formation, "\n".join(players)

    h_form, h_players = build_xi(home_lineup)
    a_form, a_players = build_xi(away_lineup)

    return (
        f"📋 <b>¡ALINEACIONES CONFIRMADAS!</b>\n"
        f"{meta['league']}\n\n"
        f"⚔️ <b>{home_team} vs {away_team}</b>\n\n"
        f"🟢 <b>{home_team}</b> ({h_form}):\n{h_players}\n\n"
        f"🔵 <b>{away_team}</b> ({a_form}):\n{a_players}\n\n"
        f"#Alineaciones #ElOnceTitular"
    )

def format_injury(injury: Dict[str, Any]) -> str:
    player_name = safe_escape(injury.get('player', {}).get('name')) or "Jugador"
    team_name = safe_escape(injury.get('team', {}).get('name')) or "Equipo"
    type_reason = safe_escape(injury.get('player', {}).get('type')) or "Lesión"
    type_reason_es = auto_translate_text(type_reason)
    reason = safe_escape(injury.get('player', {}).get('reason')) or "Sin detalles"
    reason_es = auto_translate_text(reason)
    
    return (
        f"🚑 <b>REPORTE DE LESIÓN</b>\n\n"
        f"👤 <b>Jugador:</b> {player_name}\n"
        f"🛡️ <b>Equipo:</b> {team_name}\n"
        f"🩺 <b>Tipo:</b> {safe_escape(type_reason_es)}\n"
        f"📋 <b>Detalles:</b> {safe_escape(reason_es)}\n\n"
        f"#Lesiones #ElOnceTitular"
    )

def format_transfer(transfer: Dict[str, Any]) -> str:
    player_name = safe_escape(transfer.get('player', {}).get('name')) or "Jugador"
    transfers_list = transfer.get('transfers', [])
    if not transfers_list:
        return ""
        
    latest = transfers_list[0]
    date_str = safe_escape(latest.get('date'))
    type_str = safe_escape(latest.get('type')) or "Fichaje"
    type_str_es = auto_translate_text(type_str)
    
    in_team = safe_escape(latest.get('teams', {}).get('in', {}).get('name')) or "Nuevo Club"
    out_team = safe_escape(latest.get('teams', {}).get('out', {}).get('name')) or "Ex Club"

    return (
        f"🔄 <b>OFICIAL: FICHAJE / TRASPASO</b>\n\n"
        f"👤 <b>Jugador:</b> {player_name}\n"
        f"⬅️ <b>Sale de:</b> {out_team}\n"
        f"➡️ <b>Llega a:</b> {in_team}\n"
        f"📝 <b>Tipo:</b> {safe_escape(type_str_es)}\n"
        f"📅 <b>Fecha:</b> {date_str}\n\n"
        f"#Fichajes #Mercado #ElOnceTitular"
    )
