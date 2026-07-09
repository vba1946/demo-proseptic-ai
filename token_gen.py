"""Генератор токенов для демо-сайта."""
import os, sys, hmac, hashlib, base64, time, sqlite3, argparse
from datetime import datetime, timezone

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_SECRET = 'demo-secret-2024'
TOKEN_DURATION = 48 * 3600


def main():
    parser = argparse.ArgumentParser(description='Генератор токенов для demo-proseptic-ai')
    parser.add_argument('--domain', default='demo-proseptic-ai.up.railway.app', help='Домен демо-сайта')
    parser.add_argument('--hours', type=int, default=48, help='Срок действия (часы)')
    parser.add_argument('--unlimited', action='store_true', help='Без лимита вопросов (для разработчика)')
    parser.add_argument('--maxq', type=int, default=18, help='Лимит вопросов для этого токена')
    args = parser.parse_args()

    duration = args.hours * 3600
    expiry = int(time.time()) + duration
    maxq = 9999 if args.unlimited else args.maxq
    raw = f'{expiry}:{maxq}'
    sig = hmac.new(TOKEN_SECRET.encode(), raw.encode(), hashlib.sha256).hexdigest()[:16]
    token = base64.urlsafe_b64encode(f'{raw}:{sig}'.encode()).decode().rstrip('=')

    db_path = os.path.join(DATA_DIR, 'tokens.db')
    conn = sqlite3.connect(db_path)
    conn.execute('CREATE TABLE IF NOT EXISTS token_usage (token TEXT PRIMARY KEY, questions_used INTEGER DEFAULT 0)')
    conn.execute('INSERT OR IGNORE INTO token_usage (token, questions_used) VALUES (?, 0)', (token,))
    conn.commit()
    conn.close()

    expiry_dt = datetime.fromtimestamp(expiry, tz=timezone.utc)
    expiry_str = expiry_dt.strftime('%d.%m.%Y %H:%M MSK')

    print()
    print('=' * 60)
    print('         ДЕМО-САЙТ: СИСТЕМА С AI-КОНСУЛЬТАНТОМ')
    print('=' * 60)
    print()
    print(f'  Ссылка:  https://{args.domain}/?token={token}')
    print(f'  Срок:    {expiry_str}')
    limit_str = 'Без лимита' if args.unlimited else f'{maxq} вопросов'
    print(f'  Лимит:   {limit_str}')
    print()
    if args.unlimited:
        print('  Для разработчика: без лимита вопросов.')
    else:
        print('  Отправь эту ссылку компании для демонстрации.')
    print()


if __name__ == '__main__':
    main()
