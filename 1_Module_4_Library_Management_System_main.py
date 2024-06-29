import atexit
from helper import clear
from book_operations import book_operations, export_library, import_library
from user_operations import user_operations, export_users, import_users
from author_operations import author_operations, export_authors, import_authors

def main ():

    try:
        import_library()
        import_users()
        import_authors()
    except Exception as e:
        print(f"Error during initialization: {e}")
        return

    atexit.register(export_library)
    atexit.register(export_users)
    atexit.register(export_authors)

    while True:
        ans = input('''
        Welcome to the Library Management System!

        Menu:
        1. Book operations
        2. User operations
        3. Author operations
        4. Quit

        Please enter your selection (1-4): ''')
        if ans == '1':
            clear()
            book_operations()  # Function for book operations
        elif ans == '2':
            clear()
            user_operations()  # Function for user operations
        elif ans == '3':
            clear()
            author_operations()  # Function for author operations
        elif ans == '4':
            print("\nThanks for using our library management system!\n")
            input("Press Enter to exit...")
            clear()
            break
        else:
            print('Please enter a valid number.')


if __name__ == "__main__":
    main()