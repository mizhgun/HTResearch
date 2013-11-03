from mongoengine.connection import connect, disconnect, get_connection


class MockDBConnection(object):
    """A class that encapsulates the MongoDB connection"""

    def __init__(self):
        disconnect()
        connect("db_test")
        self.conn = get_connection()

    def __enter__(self):
        return self

    def __exit__(self, ext, exv, trb):
        disconnect()

    # NOTE: This method should NEVER be defined for a normal DBConnection.
    def dropall(self):
        self.conn.drop_database("db_test")