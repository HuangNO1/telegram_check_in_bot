import sqlite3
import os
import configparser

config = configparser.ConfigParser()
config.optionxform = str
config.read("../settings.ini")
SQLITE_DB_PATH = os.getcwd()
SQLITE_DB_FILE = config['data']['DB_FILE']


def init_sql() -> None:
    os.chdir(SQLITE_DB_PATH)
    # check file is exist
    if os.path.isfile(SQLITE_DB_FILE):
        print("sqlite exist")
        return
    else:
        print("File not exist, create it!")
        os.mknod(SQLITE_DB_FILE)
    conn = sqlite3.connect(SQLITE_DB_FILE)
    cur = conn.cursor()

    """
    e.g.
    chat_id=23798,
    alarm_times="\"22:44:11\",\"11:22:55\"",
    alarm_days="0,1,2,3,4,5,6",
    enable=true
    """
    cur.execute(
        """
        CREATE TABLE chat(
            chat_id INT PRIMARY KEY,
            alarm_times TEXT NOT NULL,
            alarm_days TEXT NOT NULL,
            sum_up_time TEXT NOT NULL,
            enable BOOLEAN NOT NULL
        );
        """)
    
    cur.execute(
        """
        CREATE TABLE user(
            chat_id INT,
            user_id INT,
            username TEXT NOT NULL,
            sum_days INT NOT NULL,
            continuous_days INT NOT NULL,
            is_check_in_today BOOLEAN NOT NULL,
            is_check_in_yesterday BOOLEAN NOT NULL
        );
        """
    )

    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_sql()
