from datetime import datetime, date, time


def test_date():
    d = time(hour=10, minute=44, second=44)
    print(d.hour)

if __name__=='__main__':
    test_date()