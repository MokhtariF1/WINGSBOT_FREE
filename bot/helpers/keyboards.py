from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..db import query_db


def build_start_menu_keyboard() -> InlineKeyboardMarkup:
    buttons_data = query_db(
        "SELECT text, target, is_url, row, col FROM buttons WHERE menu_name = 'start_main' ORDER BY row, col"
    )

    trial_status = query_db("SELECT value FROM settings WHERE key = 'free_trial_status'", one=True)
    if not trial_status or trial_status.get('value') != '1':
        buttons_data = [b for b in buttons_data if b.get('target') != 'get_free_config']

    keyboard = []
    if buttons_data:
        max_row = max((b['row'] for b in buttons_data), default=0)
        keyboard_rows = [[] for _ in range(max_row + 1)]
        for b in buttons_data:
            btn = (
                InlineKeyboardButton(b['text'], url=b['target'])
                if b['is_url']
                else InlineKeyboardButton(b['text'], callback_data=b['target'])
            )
            if 0 < b['row'] <= len(keyboard_rows):
                # Adjust for 1-based row from DB vs 0-based list index
                keyboard_rows[b['row'] - 1].append(btn)
        keyboard = [row for row in keyboard_rows if row]

    # --- Fallback Logic ---
    # Ensures core buttons are present if not defined in the database
    missing = lambda target: not any((b.get('target') == target) for b in (buttons_data or []))
    
    # Top row: Buy + Get Free
    top_row = []
    if missing('buy_config_main'):
        top_row.append(InlineKeyboardButton("\U0001F4E1 خرید کانفیگ", callback_data='buy_config_main'))
    if trial_status and trial_status.get('value') == '1' and missing('get_free_config'):
        top_row.append(InlineKeyboardButton("\U0001F381 دریافت تست", callback_data='get_free_config'))
    if top_row:
        keyboard.append(top_row)

    # Subsequent rows in pairs
    row_fill_targets = [
        ('my_services', "\U0001F4DD سرویس‌های من"),
        ('wallet_menu', "\U0001F4B3 کیف پول من"),
        ('support_menu', "\U0001F4AC پشتیبانی"),
        ('tutorials_menu', "\U0001F4D6 آموزش‌ها"),
        ('referral_menu', "\U0001F517 معرفی به دوستان"),
        ('reseller_menu', "\U0001F4B5 دریافت نمایندگی"),
    ]
    
    # Get all targets already on the keyboard to avoid adding duplicates
    existing_targets = {b.get('target') for b in (buttons_data or [])}
    
    current_row = []
    for target, text in row_fill_targets:
        if target not in existing_targets:
            current_row.append(InlineKeyboardButton(text, callback_data=target))
            if len(current_row) == 2:
                keyboard.append(current_row)
                current_row = []
    
    if current_row:
        keyboard.append(current_row)

    return InlineKeyboardMarkup(keyboard) if keyboard else None
