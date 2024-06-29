from helper import clear
from db_connection import connect_db, Error

users = {}

class User:
    def __init__(self, name, library_id, borrowed_books=None):
        self.name = name
        self.library_id = library_id
        self.borrowed_books = borrowed_books if borrowed_books is not None else []

    def get_name(self):
        return self.name
    
    def get_library_id(self):
        return self.library_id
    
    def get_borrowed_books(self):
        return self.borrowed_books
    
    def set_name(self, new_name):
        self.name = new_name
    
    def set_library_id(self, new_library_id):
        self.library_id = new_library_id
    
    def set_borrowed_books(self, new_borrowed_books):
        self.borrowed_books = new_borrowed_books


def new_id(): #Function to return new user ID
    last_id = max(users.keys()) if users else 0
    return last_id + 1


def add_new_user():
    new_user_library_id = new_id()

    while True:
        name = input("Please enter the user's name: \n")
        while True:
            print (f"Name: {name}")
            correct = input ("Does this information look correct? (y/n) \n")
            if correct.lower() == 'y':
                #Create new user
                new_user = User(name, new_user_library_id)
                new_user.set_library_id(new_user_library_id)
                users[new_user_library_id] = new_user

                conn = connect_db ()
                if conn is not None:
                    try:
                        cursor = conn.cursor()
                        query = "INSERT INTO users (name) VALUES (%s)"
                        cursor.execute(query, (name,))
                        conn.commit()
                    except Error as e:
                        print(f"Error: {e}")
                    finally:
                        if conn and conn.is_connected():
                            cursor.close()
                            conn.close()
                clear()
                print(f"{new_user.get_name()} was added successfully!")
                input("Press Enter to return to the user operations menu...")
                clear()
                return
            elif correct.lower() == 'n':
                clear()
                print("Let's try again.\n")
                break
            else:
                print("Please enter 'y' for yes or 'n' for no.")

def view_user_details():
    if not users:
        print("No users available to search.")
        input("Press Enter to return to the user operations menu...")
        return

    while True:
        ans = input ("Enter the Library ID or name of the user you'd like to search for: \n")
        
        found_user = False
        for user_library_id, user_info in users.items():
            if ans == str(user_library_id) or ans.lower() in user_info.get_name().lower():
                clear()
                print ("Found a matching user! \n")
                print (f'User Library ID: {user_library_id}')
                print (f'Name: {user_info.get_name()}')
                borrowed_books = user_info.get_borrowed_books()
                borrowed_books_display = ", ".join(borrowed_books) if borrowed_books else "None"
                print(f'Borrowed books: {borrowed_books_display}')
                print("-" * 20)
                found_user = True
                break
        if found_user:
             input("Press Enter to return to the user operations menu...")
             clear()
             return
        else:
                print ("User not found. Please try again.")


def display_all_users():
    if not users:
        print("No users available to display.")
        input("Press Enter to return to the user operations menu...")
        return
    
    print("User List:\n")
    for user_library_id, user_info in users.items():
        print(f'User Library ID: {user_library_id}')
        print(f'Name: {user_info.get_name()}')
        borrowed_books = user_info.get_borrowed_books()
        borrowed_books_display = ", ".join(borrowed_books) if borrowed_books else "None"
        print(f'Borrowed books: {borrowed_books_display}')
        print("-" * 20)

    input("Press Enter to return to the user operations menu...")
    clear()

def export_users():
    try:
        with open('users.txt', 'w') as file:
            for user_id, user_info in users.items():
                borrowed_books = ','.join(user_info.get_borrowed_books()) if user_info.get_borrowed_books() else ''
                file.write(f"{user_id},{user_info.get_name()},{borrowed_books}\n")

        conn = connect_db()
        if conn is not None:
            try:
                cursor = conn.cursor()
                for user_id, user_info in users.items():
                    name = user_info.get_name()
                    borrowed_books = ','.join(user_info.get_borrowed_books()) if user_info.get_borrowed_books() else ''
                    query = """
                        INSERT INTO users (id, name, borrowed_books) 
                        VALUES (%s, %s, %s) 
                        ON DUPLICATE KEY UPDATE name=%s, borrowed_books=%s
                    """
                    cursor.execute(query, (user_id, name, borrowed_books, name, borrowed_books))
                conn.commit()
                print("Users exported successfully and updated in the database.")
            except Error as e:
                print(f"Error exporting users to database: {e}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
    except FileNotFoundError:
        print("The file 'users.txt' was not found.")
    except Exception as e:
        print(f"An error occurred while exporting users: {e}")

def import_users():
    global users

    try:
        with open('users.txt', 'r') as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) < 2:
                    print(f"Skipping malformed line: {line}")
                    continue
                user_id = int(parts[0])
                name = parts[1]
                borrowed_books = parts[2:] if len(parts) > 2 else []
                borrowed_books = borrowed_books if borrowed_books != [''] else []

                if user_id in users:
                    existing_user = users[user_id]
                    existing_user.set_name(name)
                    existing_user.set_borrowed_books(borrowed_books)
                else:
                    users[user_id] = User(name, user_id, borrowed_books)
        
        conn = connect_db()
        if conn is not None:
            try:
                cursor = conn.cursor()
                for user_id, user_info in users.items():
                    name = user_info.get_name()
                    borrowed_books = ','.join(user_info.get_borrowed_books()) if user_info.get_borrowed_books() else 'None'

                    query = """
                        SELECT * FROM users WHERE id = %s OR name = %s
                    """
                    cursor.execute(query, (user_id, name))
                    result = cursor.fetchone()

                    if result:
                        update_query = """
                            UPDATE users SET name = %s, borrowed_books = %s WHERE id = %s
                        """
                        cursor.execute(update_query, (name, borrowed_books, user_id))
                    else:
                        insert_query = """
                            INSERT INTO users (id, name, borrowed_books) VALUES (%s, %s, %s)
                        """
                        cursor.execute(insert_query, (user_id, name, borrowed_books))
                        
                conn.commit()
                print("Users imported successfully and updated in the database.")
            except Error as e:
                print(f"Error importing users to database: {e}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
    except FileNotFoundError:
        print("The file 'users.txt' was not found.")
    except Exception as e:
        print(f"An error occurred while importing users: {e}")


def user_operations ():
    while True:
        ans = input ('''
        User Operations:

        1. Add a new user
        2. View user details
        3. Display all users
        4. Return to main menu

        Please enter your selection (1-4): ''')
        if ans == '1':
            clear()
            add_new_user() # Function to add a new user
        elif ans == '2':
            clear()
            view_user_details() # Function to view user details
        elif ans == '3':
            clear()
            display_all_users() # Function display all users
        elif ans == '4':
            clear()
            break # Return to main menu
        else:
            print('Please enter a valid number.')

if __name__ == "__main__":
    user_operations()