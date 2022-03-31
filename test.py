from datetime import datetime, date, time


def test_date():
    d = time(hour=4, minute=4, second=44)
    print(d.hour)
    d_str = "" + str(d) + " d"
    d_str = d_str[:-1]
    print(d_str)

def test_tuple_to_str():
    t = (0, 1, 2, 3, 4)
    s = " ".join(str(x) for x in t)
    print(s)


if __name__=='__main__':
    test_date()
    test_tuple_to_str()