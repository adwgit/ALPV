# app/database.py
##import os
import redis
import psycopg2
from psycopg2 import pool
from datetime import datetime


class Database:
    def __init__(self):
        self.conn_pool = psycopg2.pool.SimpleConnectionPool(1, 10,
                                                            dbname='your_redshift_db_name',
                                                            user='your_redshift_user',
                                                            password='your_redshift_password',
                                                            host='your_redshift_host',
                                                            port='your_redshift_port'
                                                            )
        self.redis_cache = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.create_tables()

    def get_connection(self):
        return self.conn_pool.getconn()

    def release_connection(self, conn):
        self.conn_pool.putconn(conn)

    def create_tables(self):
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS List (
                                id INT IDENTITY(1,1) PRIMARY KEY,
                                name VARCHAR(255) NOT NULL,
                                type VARCHAR(50) NOT NULL
                             )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS ListItem (
                                id INT IDENTITY(1,1) PRIMARY KEY,
                                list_id INT NOT NULL,
                                value VARCHAR(255) NOT NULL,
                                comment TEXT,
                                created_by VARCHAR(255),
                                created_at TIMESTAMP,
                                updated_by VARCHAR(255),
                                updated_at TIMESTAMP,
                                FOREIGN KEY (list_id) REFERENCES List(id)
                             )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
                                id INT IDENTITY(1,1) PRIMARY KEY,
                                username VARCHAR(255) UNIQUE NOT NULL,
                                password VARCHAR(255) NOT NULL,
                                role VARCHAR(50) NOT NULL
                             )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS UserActions (
                                id INT IDENTITY(1,1) PRIMARY KEY,
                                username VARCHAR(255) NOT NULL,
                                action VARCHAR(255) NOT NULL,
                                timestamp TIMESTAMP NOT NULL
                             )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS Notifications (
                                id INT IDENTITY(1,1) PRIMARY KEY,
                                list_id INT NOT NULL,
                                threshold INT NOT NULL,
                                notified BOOLEAN NOT NULL DEFAULT FALSE,
                                FOREIGN KEY (list_id) REFERENCES List(id)
                             )''')
            cursor.execute('''CREATE INDEX idx_listitem_value ON ListItem (value)''')
            cursor.execute('''CREATE INDEX idx_listitem_list_id ON ListItem (list_id)''')
            cursor.execute('''CREATE INDEX idx_useractions_username ON UserActions (username)''')
            conn.commit()
        self.release_connection(conn)

    def retrieve_list(self, list_id):
        cache_key = f'list_{list_id}'
        cached_data = self.redis_cache.get(cache_key)
        if cached_data:
            return eval(cached_data)

        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM ListItem WHERE list_id = %s", (list_id,))
            data = {row[2]: row for row in cursor.fetchall()}
            self.redis_cache.set(cache_key, str(data), ex=60 * 5)  # Cache for 5 minutes
        self.release_connection(conn)
        return data

    def store_list(self, list_id, value, comment, author):
        self.redis_cache.delete(f'list_{list_id}')
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute('''INSERT INTO ListItem (list_id, value, comment, created_by, created_at, updated_by, updated_at)
                              VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                           (list_id, value, comment, author, datetime.now(), author, datetime.now()))
            conn.commit()
        self.release_connection(conn)

    def update_list(self, list_id, old_value, new_value, comment, author):
        self.redis_cache.delete(f'list_{list_id}')
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute('''UPDATE ListItem
                              SET value = %s, comment = %s, updated_by = %s, updated_at = %s
                              WHERE list_id = %s AND value = %s''',
                           (new_value, comment, author, datetime.now(), list_id, old_value))
            conn.commit()
        self.release_connection(conn)

    def delete_value(self, list_id, value):
        self.redis_cache.delete(f'list_{list_id}')
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute('''DELETE FROM ListItem WHERE list_id = %s AND value = %s''', (list_id, value))
            conn.commit()
        self.release_connection(conn)

    def change_list_type(self, list_id, new_type):
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute('''UPDATE List SET type = %s WHERE id = %s''', (new_type, list_id))
            conn.commit()
        self.release_connection(conn)

    def log_action(self, username, action):
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute('''INSERT INTO UserActions (username, action, timestamp)
                              VALUES (%s, %s, %s)''', (username, action, datetime.now()))
            conn.commit()
        self.release_connection(conn)

    def get_action_count(self):
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute('''SELECT action, COUNT(*) FROM UserActions GROUP BY action''')
            results = cursor.fetchall()
        self.release_connection(conn)
        return results

    def get_user_action_count(self, username):
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute('''SELECT action, COUNT(*) FROM UserActions WHERE username = %s GROUP BY action''',
                           (username,))
            results = cursor.fetchall()
        self.release_connection(conn)
        return results

    def add_notification(self, list_id, threshold):
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute('''INSERT INTO Notifications (list_id, threshold) VALUES (%s, %s)''', (list_id, threshold))
            conn.commit()
        self.release_connection(conn)

    def get_notifications(self):
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute('''SELECT * FROM Notifications WHERE notified = FALSE''')
            results = cursor.fetchall()
        self.release_connection(conn)
        return results

    def mark_notification_as_sent(self, notification_id):
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute('''UPDATE Notifications SET notified = TRUE WHERE id = %s''', (notification_id,))
            conn.commit()
        self.release_connection(conn)

    def get_list_count(self, list_id):
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute('''SELECT COUNT(*) FROM ListItem WHERE list_id = %s''', (list_id,))
            count = cursor.fetchone()[0]
        self.release_connection(conn)
        return count
