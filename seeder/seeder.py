from db.database import createOpenLdapSchema


def seeder():
    print("\n\n")
    print("seeder is running:")
    createOpenLdapSchema()
    print("seeder finished.")
    print("\n\n")
