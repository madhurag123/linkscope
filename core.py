"""Transactional short links and aggregate-only analytics."""
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlsplit
from datetime import datetime,timezone,timedelta
import sqlite3,secrets,re,os

def now():return datetime.now(timezone.utc)
@contextmanager
def db():
    path=Path(os.environ.get('LINKS_DB',Path(__file__).parent/'var/links.sqlite'))
    path.parent.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(path,timeout=10);con.row_factory=sqlite3.Row
    con.executescript('''
    CREATE TABLE IF NOT EXISTS links(alias TEXT PRIMARY KEY,url TEXT NOT NULL,campaign TEXT NOT NULL,created TEXT NOT NULL,expires TEXT,enabled INTEGER NOT NULL DEFAULT 1);
    CREATE TABLE IF NOT EXISTS clicks(alias TEXT NOT NULL,day TEXT NOT NULL,referrer TEXT NOT NULL,hits INTEGER NOT NULL,PRIMARY KEY(alias,day,referrer));
    ''')
    try:
        with con:yield con
    finally:con.close()
def validate_url(url):
    if not isinstance(url,str) or len(url)>2048 or any(ord(c)<33 for c in url):raise ValueError('Enter a URL of at most 2048 characters without whitespace')
    p=urlsplit(url)
    if p.scheme not in ('http','https') or not p.hostname or p.username or p.password:raise ValueError('Use a complete HTTP(S) URL without embedded credentials')
    try:p.port
    except ValueError:raise ValueError('Invalid port')
    return url

def create(url,campaign='',alias='',days=30):
    validate_url(url)
    campaign=str(campaign).strip()
    if len(campaign)>80:raise ValueError('Campaign must be at most 80 characters')
    alias=alias or secrets.token_urlsafe(6)
    if not re.fullmatch(r'[A-Za-z0-9_-]{3,32}',alias) or alias in {'api','static','health'}:raise ValueError('Alias requires 3–32 letters, digits, hyphens or underscores')
    days=int(days)
    if not 1<=days<=365:raise ValueError('Expiration must be 1–365 days')
    with db() as c:
        try:c.execute('INSERT INTO links VALUES(?,?,?,?,?,1)',(alias,url,campaign,now().isoformat(),(now()+timedelta(days=days)).isoformat()))
        except sqlite3.IntegrityError:raise ValueError('That alias is already in use')
    return alias

def resolve(alias,referrer=''):
    with db() as c:
        c.execute('BEGIN IMMEDIATE')
        row=c.execute('SELECT * FROM links WHERE alias=?',(alias,)).fetchone()
        if not row:return None
        if not row['enabled'] or datetime.fromisoformat(row['expires'])<=now():raise ValueError('This link has expired or been disabled')
        try:host=(urlsplit(referrer).hostname or 'direct')[:120]
        except ValueError:host='direct'
        c.execute('INSERT INTO clicks VALUES(?,?,?,1) ON CONFLICT(alias,day,referrer) DO UPDATE SET hits=hits+1',(alias,now().date().isoformat(),host))
        return row['url']

def disable(alias):
    with db() as c:
        if c.execute('UPDATE links SET enabled=0 WHERE alias=?',(alias,)).rowcount==0:raise ValueError('Link not found')

def analyze(params):
    with db() as c:
        rows=[dict(x) for x in c.execute('SELECT l.*,COALESCE(sum(c.hits),0) AS clicks FROM links l LEFT JOIN clicks c USING(alias) GROUP BY l.alias ORDER BY l.created DESC')]
        bars=[dict(label=x['day'],value=x['hits']) for x in c.execute('SELECT day,sum(hits) hits FROM clicks GROUP BY day ORDER BY day')]
    return dict(metrics={'Links':len(rows),'Clicks':sum(x['clicks'] for x in rows),'Active':sum(x['enabled'] and datetime.fromisoformat(x['expires'])>now() for x in rows)},rows=rows,bars=bars,chart_title='Clicks by UTC day')
