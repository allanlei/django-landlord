import os

def env_key(key='TENANT'):
    return os.environ.get(key, None)