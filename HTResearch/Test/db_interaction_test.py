from DataAccess import dto

class DatabaseInteractionTestSuite():

    mongodb_name = 'db_test'

    def __init__(self):
        print "New DatabaseInteractionTestSuite running"
        self.run_test()

    def init_database(self):
        from mongoengine.connection import connect, disconnect
        disconnect()
        connect(self.mongodb_name)
        print 'Creating mongo test-database ' + self.mongodb_name

    def destroy_database(self):
        from mongoengine.connection import get_connection, disconnect
        connection = get_connection()
        connection.drop_database(self.mongodb_name)
        print 'Dropping mongo test-database: ' + self.mongodb_name
        disconnect()

    def run_test(self):
        self.init_database()
        my_contact = ContactDTO()
        my_contact.first_name = "Jordan"
        my_contact.last_name = "Degner"
        my_contact.email = "jdegner0129@gmail.com"
        DAOFactory.GetInstance(ContactDAO).Create(my_contact)
        self.destroy_database()

if __name__:
    my_suite = DatabaseAccessTestSuite()