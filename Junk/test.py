# -*- coding: utf-8 -*-
"""
Merge dbs
"""

import sqlite3
import os

class MergeYears(object):
    logs_directory = "D://Mahjong group project data"
    db_file = ''
    is_tonpu = False
    is_3p = False

    def __init__(self, logs_directory, db_file, is_3p, is_tonpu):
        """
        :param logs_directory: directory where to store downloaded logs
        :param db_file: to save log ids
        :param is_3p: 1 or 0
        :param is_tonpu: 1 or 0
        """
        self.logs_directory = logs_directory
        self.db_file = db_file
        self.is_3p = is_3p
        self.is_tonpu = is_tonpu


    def merge(self):
        """
        Init logs table and add basic indices
        :return:
        """
        print('Set up new database {}'.format(self.db_file))

        with sqlite3.connect(self.db_file) as conn1:
            cursor = conn1.cursor()
            cursor.execute("""
            CREATE TABLE logs(log_id text primary key,
                              year text,
                              log_content text);
            """)
            cursor.execute("CREATE INDEX year ON logs (year);")

            print('Inserting new ids to the database...')
            for year in range(2016, 2021):
                print(year)
                with sqlite3.connect(self.logs_directory + str(year) + '.db') as conn2:
                    c2 = conn2.cursor()
                    print("Connecting...")
                    c2.execute("SELECT log_id, log_content FROM logs WHERE is_hirosima=? AND is_tonpusen=? AND log_id LIKE(?)",
                               [self.is_3p, self.is_tonpu, '%d%%' % year])

                    for item in c2.fetchall():
                        cursor.execute('INSERT INTO logs VALUES (?, ?, ?);',
                                       [item[0], str(year), item[1]])
        print('Done')

MergeYears('./', 'es4p.db', 0, 0).merge()
MergeYears('./', 'es3p.db', 1, 0).merge()
MergeYears('./', 'e4p.db', 0, 1).merge()