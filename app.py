import base64
import binascii
import hashlib
import hmac
import urllib.parse

from flask import abort, Flask, redirect, request

app = Flask(__name__)

SECRET = open('keys/secret').read().strip()

def secret_hmac(msg):
    return hmac.new(SECRET, msg, digestmod=hashlib.sha256).digest()

@app.route("/test")
def test():
    try:
        username = request.headers['X-WEBAUTH-USER'].strip()
        return "Logged in as {}".format(username)
    except KeyError:
        return "No username, something is very wrong!"

@app.route("/")
def do_it():
    sso = request.args.get('sso')
    sig = request.args.get('sig')

    got_sig = secret_hmac(sso.encode())

    if not hmac.compare_digest(binascii.unhexlify(sig), got_sig):
        abort(404)
    
    username = request.headers['X-WEBAUTH-USER'].strip()

    sso_parse = urllib.parse.parse_qs(base64.b64decode(sso).decode())
    nonce = sso_parse['nonce'][0]
    return_sso_url = sso_parse['return_sso_url'][0]

    r = urllib.parse.urlencode({
        'require_activation': 'false',
        'external_id': username,
        'username': username,
        'email': username + '@ocf.berkeley.edu',
        'nonce': nonce,
    })

    r64 = base64.b64encode(r.encode())

    r2 = {
        'sso': r64.decode(),
        'sig': binascii.hexlify(secret_hmac(r64)).decode(),
    }

    redir_url = return_sso_url + '?' + urllib.parse.urlencode(r2)

    return redirect(redir_url, code=302)
