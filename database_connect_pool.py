import json
import threading
from queue import Queue

import pymysql


class InitConnectionPool:
    class DatabaseConnectPool:
        def __init__(self, database_config_name, max_connections=10):
            self.max_connections = max_connections
            self.queue = Queue(maxsize=max_connections)
            self.lock = threading.Lock()
            with open(database_config_name, 'r') as json_file:
                data = json.load(json_file)
            self.secret_key = data["secret_key"]


            for _ in range(max_connections):
                connection = self.create_connection(host=data["host"], user=data["user"], password=data["password"],
                                                    db_name=data["database_name"], port=data["port"])
                self.queue.put(connection)

        def create_connection(self, host, user, password, db_name, port):
            return pymysql.connect(host=host, user=user, port=port, password=password, db=db_name)

        def get_connection(self):
            return self.queue.get()

        def relese_connection(self, connection):
            if connection:
                self.queue.put(connection)

        def close_pool(self):
            with self.lock:
                if self.queue.full():
                    while not self.queue.empty():
                        connection = self.queue.get()
                        connection.close()

                    return True
                return False

    connection_pool: DatabaseConnectPool = None

    @classmethod
    def init_connection_pool_entity(cls, database_config_name, max_connections):
        cls.connection_pool = InitConnectionPool.DatabaseConnectPool(database_config_name, max_connections)

    @classmethod
    def get_pool_instance(cls):
        assert cls.connection_pool
        return cls.connection_pool
