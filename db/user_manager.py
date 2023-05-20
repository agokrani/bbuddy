from db.manager import DatabaseManager
from schema.user import User, UserInDB

class UserManager: 
    def __init__(self, table_name="users"):
        self.table_name = table_name
        #self._create_table_if_not_exists()

    def _create_table_if_not_exists(self, db):
        cursor = db.cursor
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id SERIAL PRIMARY KEY,
                firstName VARCHAR(50) NOT NULL, 
                lastName VARCHAR(50) NOT NULL,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(50) UNIQUE NOT NULL,
                phone VARCHAR(50), 
                password_hash VARCHAR(100) NOT NULL
            );
        """)
        db.commit()
    
    def insert_user(self, db, username, email, password, firstName, lastName, phone):
        cursor = db.cursor()
        cursor.execute(f"""
            INSERT INTO {self.table_name} (username, email, password_hash, firstName, lastName, phone)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, username, email;
        """, (username, email, password, firstName, lastName, phone))
        user = cursor.fetchone()
        
        db.commit()
        return User(id=user[0], username=user[1], email=user[2])
    
    def get_user_by_email(self, db, email):
        cursor = db.cursor()
        cursor.execute(f"""
            SELECT id, username, email, password_hash, firstName, lastName, phone
            FROM {self.table_name}
            WHERE email = %s;
        """, (email,))
        user = cursor.fetchone()

        if user is not None: 
            return UserInDB(id=user[0], username=user[1], email=user[2], password=user[3], firstName=user[4], lastName=user[5], phone=user[6])

    def get_user_by_username(self, db, username):
        cursor = db.cursor()
        cursor.execute(f"""
            SELECT id, username, email, password_hash, firstName, lastName, phone
            FROM {self.table_name}
            WHERE username = %s;
        """, (username,))
        user = cursor.fetchone()
        
        if user is not None: 
            return UserInDB(id=user[0], username=user[1], email=user[2], password=user[3], firstName=user[4], lastName=user[5], phone=user[6])


user_manager = UserManager()