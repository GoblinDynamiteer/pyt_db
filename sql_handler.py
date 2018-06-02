#!/usr/bin/python
# -*- coding: utf-8 -*-
import paths, os
import MySQLdb
from printout import print_class as pr

pr = pr(os.path.basename(__file__))

class sql_connection:
    def __init__(self, remote_address, login, password, port, database_name):
        self.connected = False
        self.cursor = None
        self.sql_db_conn = MySQLdb.connect(host=remote_address, user=login, passwd=password, port=port, db=database_name)
        if self.sql_db_conn:
            self.connected = True
            self.cursor = self.sql_db_conn.cursor()

    def update(self, table, column, value, column_match, match_data):
        query = f"UPDATE {table} SET {column} = %s WHERE {table}.{column_match} = %s"
        data = (value, match_data)
        if self.__run_query(query, data):
            self.__commit()
            pr.info(f"updated: {match_data} : {column} = {value}")
            return True
        else:
            pr.warning(f"failed update: {match_data} : {column} = {value}")
            return False

    def __run_query(self, query, data):
        try:
            self.cursor.execute(query, data)
            return True
        except:
            return False

    def __commit(self):
        self.sql_db_conn.commit()
