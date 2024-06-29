import re
from helper import clear
from user_operations import users
from db_connection import connect_db, Error
from datetime import datetime, timedelta

library = {}

def new_id(): #Function to return new ID for a book
    last_id = max(library.keys()) if library else 0
    return last_id + 1

class Book ():
    def __init__(self, title, author, genre, publication_date, availability_status = True):
        self.title = title
        self.author = author
        self.genre = genre
        self.publication_date = publication_date
        self.availability_status = availability_status

    def get_title(self):
        return self.title
    def get_author(self):
        return self.author
    def get_genre(self):
        return self.genre
    def get_publication_date(self):
        return self.publication_date
    def get_availability_status(self):
        return self.availability_status
    
    def set_title(self, new_title):
        self.title = new_title
    def set_author(self, new_author):
        self.author = new_author
    def set_genre(self, new_genre):
        self.genre = new_genre
    def set_publication_date(self, new_publication_date):
        self.publication_date = new_publication_date
    def set_availability_status(self, new_availability_status):
        self.availability_status = new_availability_status


def add_new_book():
    new_book_id = new_id()
    
    while True:
        title = input("Please enter the book title: \n")
        author = input("Please enter the author: \n")
        genre = input("Please enter the genre: \n")
        
        while True:
            publication_date = input("Please enter the publication date or year (YYYY or YYYY-MM-DD): \n")
            date_pattern = r'^\d{4}(-\d{2}-\d{2})?$'
            
            if re.match(date_pattern, publication_date):
                print(f"Title: {title} - Author: {author} - Genre: {genre} - Publication Date: {publication_date}")
                correct = input("Does this information look correct? (y/n) \n")
                
                if correct.lower() == 'y':
                    try:
                        new_book = Book('', '', '', '')
                        new_book.set_title(title)
                        new_book.set_author(author)
                        new_book.set_genre(genre)
                        new_book.set_publication_date(publication_date)
                        library[new_book_id] = new_book

                        conn = connect_db()
                        if conn is not None:
                            with conn.cursor() as cursor:
                                query = "INSERT INTO books (title, author, genre, publication_date) VALUES (%s, %s, %s, %s)"
                                cursor.execute(query, (title, author, genre, publication_date))
                                conn.commit()
                                print(f"{new_book.get_title()} was added successfully to the library and database!")
                        else:
                            print("Database connection error. Book was not added to the database.")

                        input("Press Enter to return to the book operations menu...")
                        clear()
                        return
                    except Exception as e:
                        print(f"An error occurred: {e}")
                elif correct.lower() == 'n':
                    clear()
                    print("Let's try again.\n")
                    break
                else:
                    clear()
                    print("Please enter 'y' for yes or 'n' for no.")
            else:
                clear()
                print("Invalid date format. Please enter a valid date or year (YYYY or YYYY-MM-DD).\n")

def borrow_book():
    if not library:
        print("No books available to borrow.")
        input("Press Enter to return to the book operations menu...")
        return

    while True:
        ans = input("Enter the ID, title, author, genre, or publication date of the book you'd like to borrow: \n")

        found_book = False
        for book_id, book_info in library.items():
            if (ans == str(book_id) or
                ans.lower() in book_info.get_title().lower() or
                ans.lower() in book_info.get_author().lower() or
                ans.lower() in book_info.get_genre().lower() or
                ans.lower() in book_info.get_publication_date().lower()):

                clear()
                print("Found a matching book in the library! \n")
                print(f'Book ID: {book_id}')
                print(f'Title: {book_info.get_title()}')
                print(f'Author: {book_info.get_author()}')
                print(f'Genre: {book_info.get_genre()}')
                print(f'Publication Date: {book_info.get_publication_date()}')
                print(f'Availability: {"Available" if book_info.get_availability_status() else "Not Available"}')
                print("-" * 20)
                found_book = True
                break
        
        if found_book and book_info.get_availability_status():
            while True:
                borrow = input(f"Would you like to borrow {book_info.get_title()}? (y/n) \n")
                if borrow.lower() == 'y':
                    user = input("Enter the user's name or user's library ID: \n")
                    found_user = False
                    for user_id, user_info in users.items():
                        if user == str(user_id) or user.lower() in user_info.get_name().lower():
                            clear()
                            print("Found a matching user! \n")
                            print(f'User Library ID: {user_id}')
                            print(f'Name: {user_info.get_name()}')
                            borrowed_books = user_info.get_borrowed_books()
                            borrowed_books_display = ", ".join(borrowed_books) if borrowed_books else "None"
                            print(f'Borrowed books: {borrowed_books_display}')
                            print("-" * 20)
                            found_user = True
                            break
                    
                    if found_user:
                        confirm = input(f"Is this the user who would like to borrow {book_info.get_title()}? (y/n) \n")
                        if confirm.lower() == 'y':
                            if not user_info.get_borrowed_books():
                                user_info.set_borrowed_books([])

                            user_info.get_borrowed_books().append(book_info.get_title())
                            book_info.set_availability_status(False)

                            conn = connect_db()
                            if conn is not None:
                                try:
                                    with conn.cursor() as cursor:
                                        borrow_date = datetime.now().date()
                                        return_date = borrow_date + timedelta(days=14)
                                        query = "INSERT INTO borrowed_books (user_id, book_id, borrow_date, return_date) VALUES (%s, %s, %s, %s)"
                                        cursor.execute(query, (user_id, book_id, borrow_date, return_date))
                                        conn.commit()
                                        print(f"{book_info.get_title()} was borrowed successfully!")
                                        input("Press Enter to return to the book operations menu...")
                                        clear()
                                        return
                                
                                except Error as e:
                                    conn.rollback()
                                    print(f"Error borrowing book: {e}")
                                    clear()
                                    return
                                finally:
                                    conn.close()
                            else:
                                print("Database connection error. Book was not borrowed.")
                                clear()
                                return
                        else:
                            print("Let's try finding the user again.")
                    else:
                        print("User not found. Please try again.")
                elif borrow.lower() == 'n':
                    clear()
                    print(f"{book_info.get_title()} borrowing was canceled and the book has been returned to the stacks.")
                    input("Press Enter to search for another book to borrow.")
                    clear()
                    break
                else:
                    print("Please enter 'y' for yes or 'n' for no.")
        
        elif found_book and not book_info.get_availability_status():
            print("Sorry. It looks like this book has already been borrowed!")
            input("Press Enter to return to the book operations menu...")
            break
        
        else:
            print("Book not found. Please try again.")

def return_book():
    if not library:
        print("No books available to return.")
        input("Press Enter to return to the book operations menu...")
        return

    while True:
        ans = input("Enter the ID, title, author, genre, or publication date of the book you'd like to return: \n")

        found_book = False
        for book_id, book_info in library.items():
            if (ans == str(book_id) or
                ans.lower() in book_info.get_title().lower() or
                ans.lower() in book_info.get_author().lower() or
                ans.lower() in book_info.get_genre().lower() or
                ans.lower() in book_info.get_publication_date().lower()):

                clear()
                print("Found a matching book in the library! \n")
                print(f'Book ID: {book_id}')
                print(f'Title: {book_info.get_title()}')
                print(f'Author: {book_info.get_author()}')
                print(f'Genre: {book_info.get_genre()}')
                print(f'Publication Date: {book_info.get_publication_date()}')
                print(f'Availability: {"Available" if book_info.get_availability_status() else "Not Available"}')
                print("-" * 20)
                found_book = True
                break
        
        if found_book:
            if not book_info.get_availability_status():
                while True:
                    return_book = input(f"Would you like to return {book_info.get_title()}? (y/n) \n")
                    if return_book.lower() == 'y':
                        user = input("Enter the user's name or user's library ID: \n")
                        found_user = False
                        for user_id, user_info in users.items():
                            if user == str(user_id) or user.lower() in user_info.get_name().lower():
                                clear()
                                print("Found a matching user! \n")
                                print(f'User Library ID: {user_id}')
                                print(f'Name: {user_info.get_name()}')
                                borrowed_books = user_info.get_borrowed_books()
                                borrowed_books_display = ", ".join(borrowed_books) if borrowed_books else "None"
                                print(f'Borrowed books: {borrowed_books_display}')
                                print("-" * 20)
                                found_user = True
                                break
                        
                        if found_user:
                            confirm = input(f"Is this the user who would like to return {book_info.get_title()}? (y/n) \n")
                            if confirm.lower() == 'y':
                                if book_info.get_title() in borrowed_books:
                                    user_info.get_borrowed_books().remove(book_info.get_title())
                                    book_info.set_availability_status(True)

                                    conn = connect_db()
                                    if conn is not None:
                                        try:
                                            with conn.cursor() as cursor:
                                                query = "DELETE FROM borrowed_books WHERE user_id = %s AND book_id = %s"
                                                cursor.execute(query, (user_id, book_id))
                                                conn.commit()
                                                print(f"{book_info.get_title()} was returned successfully!")
                                                input("Press Enter to return to the book operations menu...")
                                                clear()
                                                return
                                        
                                        except Error as e:
                                            conn.rollback()
                                            print(f"Error returning book: {e}")
                                            clear()
                                            return
                                        finally:
                                            conn.close()
                                    else:
                                        print("Database connection error. Book was not returned.")
                                        clear()
                                        return
                                else:
                                    print(f"The user does not have {book_info.get_title()} borrowed.")
                                    input("Press Enter to try again...")
                                    clear()
                                    break
                            else:
                                print("Let's try finding the user again.")
                        else:
                            print("User not found. Please try again.")
                    elif return_book.lower() == 'n':
                        clear()
                        print(f"{book_info.get_title()} is still yours to read.\n")
                        input("Press Enter to search for another book to return.")
                        clear()
                        break
                    else:
                        print("Please enter 'y' for yes or 'n' for no.")
            else:
                print("It looks like this book is already available in the library!")
                input("Press Enter to return to the book operations menu.")
                break
        else:
            print("Book not found. Please try again.")


def search_books():
    if not library:
        print("No books available to search.")
        input("Press Enter to return to the book operations menu...")
        return

    while True:
        ans = input ("Enter the ID, title, author, genre, or publication date of the book you'd like to search for: \n")
        
        found_book = False
        for book_id, book_info in library.items():
            if (ans == str(book_id) or
                ans.lower() in book_info.get_title().lower() or
                ans.lower() in book_info.get_author().lower() or
                ans.lower() in book_info.get_genre().lower() or
                ans.lower() in book_info.get_publication_date().lower()):
                
                clear()
                print ("Found a matching book in the library! \n")
                print (f'Book ID: {book_id}')
                print (f'Title: {book_info.get_title()}')
                print (f'Author: {book_info.get_author()}')
                print (f'Genre: {book_info.get_genre()}')
                print (f'Publication Date: {book_info.get_publication_date()}')
                print(f'Availability: {"Available" if book_info.get_availability_status() else "Not Available"}')
                print("-" * 20)
                found_book = True
                break
        if found_book:
             input("Press Enter to return to the book operations menu...")
             clear()
             return
        else:
                print ("Book not found. Please try again.")

def display_all_books():
    if not library:
        print("No books available to view.")
        input("Press Enter to return to the book operations menu...")
        clear()
        return
    
    print("Library List: \n")
    for book_id, book_info in library.items():
        print (f'Book ID: {book_id}')
        print (f'Title: {book_info.get_title()}')
        print (f'Author: {book_info.get_author()}')
        print (f'Genre: {book_info.get_genre()}')
        print (f'Publication Date: {book_info.get_publication_date()}')
        print(f'Availability: {"Available" if book_info.get_availability_status() else "Not Available"}')
        print("-" * 20)

    input ("Press Enter to return to the main menu...")
    clear()


def export_library():
    try:
        with open('library.txt', 'w') as file:
            for book_id, book_info in library.items():
                file.write(f"{book_id},{book_info.get_title()},{book_info.get_author()},{book_info.get_genre()},{book_info.get_publication_date()},{book_info.get_availability_status()}\n")

        conn = connect_db()
        if conn is not None:
            try:
                cursor = conn.cursor()
                for book_id, book_info in library.items():
                    title = book_info.get_title()
                    author = book_info.get_author()
                    genre = book_info.get_genre()
                    publication_date = book_info.get_publication_date()
                    availability_status = book_info.get_availability_status()
                    
                    query = """
                        INSERT INTO books (id, title, author, genre, publication_date, availability_status) 
                        VALUES (%s, %s, %s, %s, %s, %s) 
                        ON DUPLICATE KEY UPDATE title=%s, author=%s, genre=%s, publication_date=%s, availability_status=%s
                    """
                    cursor.execute(query, (book_id, title, author, genre, publication_date, availability_status, title, author, genre, publication_date, availability_status))
                
                conn.commit()
                print("Books exported successfully and updated in the database.")
            except Error as e:
                print(f"Error exporting books to database: {e}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
        else:
            print("Database connection error. Books were not exported to the database.")

    except FileNotFoundError:
        print("The file 'library.txt' was not found.")
    except Exception as e:
        print(f"An error occurred while exporting the library: {e}")

    clear()



def import_library():
    try:
        with open('library.txt', 'r') as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) != 6:
                    print(f"Skipping malformed line: {line}")
                    continue
                book_id, title, author, genre, publication_date, availability_status_str = parts
                availability_status = availability_status_str == 'True'
                
                if book_id in library:
                    existing_book = library[book_id]
                    existing_book.update_title(title)
                    existing_book.update_author(author)
                    existing_book.update_genre(genre)
                    existing_book.update_publication_date(publication_date)
                    existing_book.update_availability_status(availability_status)
                else:
                    library[int(book_id)] = Book(title, author, genre, publication_date, availability_status)  
    
        conn = connect_db()
        if conn is not None:
            try:
                cursor = conn.cursor()

                conn.begin()

                for book_id, book_info in library.items():
                    title = book_info.get_title()
                    author = book_info.get_author()
                    genre = book_info.get_genre()
                    publication_date = book_info.get_publication_date()
                    availability_status = book_info.get_availability_status()

                    if not (title and author and genre and publication_date):
                        print(f"Skipping book with missing data: ID {book_id}, Title: {title}, Author: {author}")
                        continue

                    query = """
                        SELECT * FROM books WHERE id = %s OR title = %s
                    """
                    cursor.execute(query, (book_id, title))
                    result = cursor.fetchone()

                    if result:
                        update_query = """
                            UPDATE books SET title = %s, author = %s, genre = %s, publication_date = %s, availability_status = %s WHERE id = %s
                        """
                        cursor.execute(update_query, (title, author, genre, publication_date, availability_status, book_id))
                    else:
                        insert_query = """
                            INSERT INTO books (id, title, author, genre, publication_date, availability_status) VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(insert_query, (book_id, title, author, genre, publication_date, availability_status))
                        
                conn.commit()
                print("Books imported successfully and updated in the database.")
            except Error as e:
                conn.rollback()
                print(f"Error importing books to database: {e}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
        else:
            print("Database connection error. Books were not imported to the database.")

    except FileNotFoundError:
        print("The file 'library.txt' was not found.")
    except Exception as e:
        print(f"An error occurred while importing books: {e}")

    clear()


def book_operations ():
    while True:
        ans = input ('''
        Book Operations:

        1. Add a new book
        2. Borrow a book
        3. Return a book
        4. Search for a book
        5. Display all books
        6. Return to main menu

        Please enter your selection (1-6): ''')
        if ans == '1':
            clear()
            add_new_book() # Function to add a new book
        elif ans == '2':
            clear()
            borrow_book() # Function to borrow a book
        elif ans == '3':
            clear()
            return_book() # Function to return a book
        elif ans == '4':
            clear()
            search_books() # Function to search for a book
        elif ans == '5':
            clear()
            display_all_books() # Function to display all books
        elif ans == '6':
            clear()
            break
        else:
            print('Please enter a valid number.')

if __name__ == "__main__":
    book_operations()