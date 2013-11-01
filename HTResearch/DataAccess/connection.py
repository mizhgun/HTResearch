from mongoengine.connection import connect, disconnect, get_connection


class DBConnection(object):
    """A class that encapsulates the MongoDB connection"""
    
    DB_NAME = "researchData"

    def __enter__(self):
        disconnect()
        connect(self.DB_NAME)
        self.conn = get_connection()
        return self

    def dropall(self):
        self.conn.drop_database(self.DB_NAME)

    def __exit__(self, ext, exv, trb):
        disconnect()