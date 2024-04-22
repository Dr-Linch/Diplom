import random


def make_otp():
    otp = []
    for i in range(0,4):
        simbol = random.randint(0, 9)
        otp.append(str(simbol))
    otp = ''.join(otp)
    return otp
