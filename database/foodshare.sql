CREATE DATABASE foodshare;
USE foodshare;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100),
    role ENUM('restaurant','delivery','beneficiary','admin')
);

CREATE TABLE food (
    id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_id INT,
    food_name VARCHAR(100),
    quantity INT,
    pickup_time VARCHAR(50),
    expiry_time VARCHAR(50),
    description TEXT,
    status ENUM('available','collected') DEFAULT 'available',
    FOREIGN KEY (restaurant_id) REFERENCES users(id)
);
