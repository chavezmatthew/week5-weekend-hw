from helper import clear
from db_connection import connect_db, Error

authors = {}

class Author ():
    def __init__(self, name, biography):
        self.name = name
        self.biography = biography

    def get_name(self):
        return self.name
    def get_biography(self):
        return self.biography
    
    def set_name(self, new_name):
        self.name = new_name
    def set_biography(self, new_biography):
        self.biography = new_biography



def new_id(): #Function to return new author ID
    last_id = max(authors.keys()) if authors else 0
    return last_id + 1


def add_new_author():
    new_author_id = new_id()

    while True:
        name = input("Please enter the author's name: \n")
        biography = input("Please enter the author's biography: \n")
        
        print(f"Name: {name} - Biography: {biography}")
        correct = input("Does this information look correct? (y/n) \n")
        
        if correct.lower() == 'y':
            try:
                new_author = Author('', '')
                new_author.set_name(name)
                new_author.set_biography(biography)
                authors[new_author_id] = new_author

                conn = connect_db()
                if conn is not None:
                    try:
                        with conn.cursor() as cursor:
                            query = "INSERT INTO authors (name, biography) VALUES (%s, %s)"
                            cursor.execute(query, (name, biography))
                            conn.commit()
                            print(f"{new_author.get_name()} was added successfully!")
                    except Error as e:
                        print(f"Error inserting author into database: {e}")
                    finally:
                        if conn.is_connected():
                            conn.close()
                
                input("Press Enter to return to the author operations menu...")
                clear()
                return
            except Exception as e:
                print(f"An error occurred: {e}")
        elif correct.lower() == 'n':
            clear()
            print("Let's try again.\n")
        else:
            print("Please enter 'y' for yes or 'n' for no.")

def view_author_details():
    if not authors:
        print("No authors available to search.")
        input("Press Enter to return to the author operations menu...")
        return

    while True:
        ans = input ("Enter the author ID or name of the author you'd like to search for: \n")
        
        found_author = False
        for author_id, author_info in authors.items():
            if ans == str(author_id) or ans.lower() in author_info.get_name().lower():
                clear()
                print ("Found a matching author! \n")
                print (f'Author ID: {author_id}')
                print (f'Name: {author_info.get_name()}')
                print(f'Biography: {author_info.get_biography()}')
                print("-" * 20)
                found_author = True
                break
        if found_author:
             input("Press Enter to return to the author operations menu...")
             clear()
             return
        else:
                print ("Author not found. Please try again.")


def display_all_authors():
    if not authors:
        print("No authors available to search.")
        input("Press Enter to return to the author operations menu...")
        return
    
    print("Author List: \n")
    for author_id, author_info in authors.items():
        print (f'Author ID: {author_id}')
        print (f'Name: {author_info.get_name()}')
        print(f'Biography: {author_info.get_biography()}')
        print("-" * 20)

    input ("Press Enter to return to the author operations menu...")
    clear()


def export_authors():
    try:
        with open('authors.txt', 'w') as file:
            for author_id, author_info in authors.items():
                file.write(f"{author_id}\t{author_info.get_name()}\t{author_info.get_biography()}\n")
        
        conn = connect_db()
        if conn is not None:
            try:
                cursor = conn.cursor()
                for author_id, author_info in authors.items():
                    name = author_info.get_name()
                    biography = author_info.get_biography()
                    query = """
                        INSERT INTO authors (id, name, biography) 
                        VALUES (%s, %s, %s) 
                        ON DUPLICATE KEY UPDATE name=%s, biography=%s
                    """
                    cursor.execute(query, (author_id, name, biography, name, biography))
                conn.commit()
                print("Authors exported successfully and updated in the database.")
            except Error as e:
                print(f"Error exporting authors to database: {e}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
    except FileNotFoundError:
        print("The file 'authors.txt' was not found.")
    except Exception as e:
        print(f"An error occurred while exporting authors: {e}")
    clear()


def import_authors():
    authors.clear()
    try:
        with open('authors.txt', 'r') as file:
            for line in file:
                parts = line.strip().split('\t')
                if len(parts) != 3:
                    print(f"Skipping malformed line: {line}")
                    continue
                author_id, name, biography = parts
                if author_id in authors:
                    existing_author = authors[author_id]
                    existing_author.update_name(name)
                    existing_author.update_biography(biography)
                else:
                    authors[int(author_id)] = Author(name, biography)
        
        conn = connect_db()
        if conn is not None:
            try:
                cursor = conn.cursor()
                for author_id, author_info in authors.items():
                    name = author_info.get_name()
                    biography = author_info.get_biography()

                    query = """
                        SELECT * FROM authors WHERE id = %s OR name = %s
                    """
                    cursor.execute(query, (author_id, name))
                    result = cursor.fetchone()

                    if result:
                        update_query = """
                            UPDATE authors SET name = %s, biography = %s WHERE id = %s
                        """
                        cursor.execute(update_query, (name, biography, author_id))
                    else:
                        insert_query = """
                            INSERT INTO authors (id, name, biography) VALUES (%s, %s, %s)
                        """
                        cursor.execute(insert_query, (author_id, name, biography))
                        
                conn.commit()
                print("Authors imported successfully and updated in the database.")
            except Error as e:
                print(f"Error importing authors to database: {e}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
    except FileNotFoundError:
        print("The file 'authors.txt' was not found.")
    except Exception as e:
        print(f"An error occurred while importing authors: {e}")

    clear()


def author_operations ():
    while True:
        ans = input ('''
        Author Operations:

        1. Add a new author
        2. View author details
        3. Display all authors
        4. Return to main menu

        Please enter your selection (1-4): ''')
        if ans == '1':
            clear()
            add_new_author() # Function to add a new user
        elif ans == '2':
            clear()
            view_author_details() # Function to view user details
        elif ans == '3':
            clear()
            display_all_authors() # Function display all users
        elif ans == '4':
            clear()
            break # Return to main menu
        else:
            print('Please enter a valid number.')

if __name__ == "__main__":
    author_operations()