from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize limiter with Key = Client IP
# default_limits can be set here if we want a global fallback, 
# but we are collecting explicit limits for now.
limiter = Limiter(key_func=get_remote_address)
