CREATE DATABASE library;

USE library;


CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(250) NOT NULL,
    author VARCHAR (250) NOT NULL,
    genre VARCHAR (250) NOT NULL,
    publication_date VARCHAR(250),
    availability_status BOOLEAN DEFAULT 1
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(250) NOT NULL,
    borrowed_books VARCHAR (250)
);

CREATE TABLE authors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(250) NOT NULL,
    biography VARCHAR (1000)
);

CREATE TABLE borrowed_books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    borrow_date DATE,
    return_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (book_id) REFERENCES books(id)
);

SELECT * FROM books;
SELECT * FROM users;
SELECT * FROM authors;
SELECT * FROM borrowed_books;