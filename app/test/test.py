from datetime import *
import hashlib
import pytz

def test_date():
    beijing = timezone(timedelta(hours=8))
    d = time(hour=4, minute=4, second=44)
    print(d.hour)
    d_str = "" + str(d) + " d"
    d_str = d_str[:-1]
    print(d_str)
    d.replace(tzinfo=pytz.timezone('Asia/Taipei'))
    print(d.tzinfo)
    print(d)
    dddd = time(hour=6, minute=27, tzinfo=pytz.timezone('Asia/Kolkata'))
    print(dddd)
    print(dddd.tzinfo)


def test_tuple_to_str():
    t = (0, 1, 2, 3, 4)
    s = " ".join(str(x) for x in t)
    print(s)

if __name__=='__main__':
    test_date()
    test_tuple_to_str()