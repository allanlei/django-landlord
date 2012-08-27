import string
import random

def randomStr(length=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(length))