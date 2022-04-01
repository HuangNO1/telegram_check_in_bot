from datetime import *
import hashlib

def test_date():


    beijing = timezone(timedelta(hours=8))
    d = time(hour=4, minute=4, second=44)
    print(d.hour)
    d_str = "" + str(d) + " d"
    d_str = d_str[:-1]
    print(d_str)
    d.replace(tzinfo=timezone.utc)
    d.tzinfo.utcoffset(dt)
    print(d.tzinfo)
    print(d)

def test_tuple_to_str():
    t = (0, 1, 2, 3, 4)
    s = " ".join(str(x) for x in t)
    print(s)

if __name__=='__main__':
    test_date()
    test_tuple_to_str()