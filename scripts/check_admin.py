import sqlite3, json, sys

try:
    conn = sqlite3.connect('instance/app.db')
    c = conn.cursor()
    c.execute("SELECT id,username,email,role,is_verified,password_hash FROM users WHERE email=?", ('admin@cloudshare.pro',))
    r = c.fetchone()
    if r:
        print(json.dumps({
            'id': r[0],
            'username': r[1],
            'email': r[2],
            'role': r[3],
            'is_verified': r[4],
            'password_hash': r[5]
        }))
    else:
        print('NOT_FOUND')
    conn.close()
except Exception as e:
    print('ERROR', str(e))
    sys.exit(1)
