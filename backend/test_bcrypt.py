import hashlib
from passlib.context import CryptContext
print('passlib version', __import__('passlib').__version__)
print('bcrypt version', __import__('bcrypt').__version__)
pw='password123'
sha = hashlib.sha256(pw.encode()).hexdigest()
print('sha len', len(sha), sha)
ctx = CryptContext(schemes=['bcrypt'], deprecated='auto')
try:
    h = ctx.hash(sha)
    print('bcrypt hash ok', h[:30])
except Exception as e:
    print('bcrypt hash failed', type(e).__name__, e)
ctx2 = CryptContext(schemes=['bcrypt_sha256'], deprecated='auto')
try:
    h2 = ctx2.hash(pw)
    print('bcrypt_sha256 hash ok', h2[:30])
except Exception as e:
    print('bcrypt_sha256 hash failed', type(e).__name__, e)
