create database retailer;
use retailer;

-- create tables for retailer table
create table users (
	name varchar(65), -- optional field filled out by user
    email varchar(100) not null,
    username varchar(45) not null,
    password varchar(45) not null,
    type enum("admin","vendor","customer") not null,
    
    unique(username),
    primary key(email)
);

desc users;

-- product table

create table products (
	product_name varchar(255) not null,
    product_id int not null auto_increment,
    email varchar(100) not null,
    product_description longtext,
    warranty_date datetime,
    inventory int,
    price double(45,2),
    
    primary key (product_id),
    foreign key (email) references users(email)    
);

desc products;

-- product size table

create table product_sizes (
	product_id int not null,
    size varchar(5) not null,
    
    foreign key (product_id) references products(product_id)
);
desc product_sizes;

-- product colors table

create table product_colors (
	product_id int not null,
    color varchar(45) not null,
    
    foreign key (product_id) references products(product_id)
);
desc product_colors;

-- product image table

create table product_images (
	product_id int not null,
    image_link varchar(255) not null,
    
    foreign key (product_id) references products(product_id)
);
desc product_images;

-- product discounts table

create table product_discounts (
	product_id int not null,
    until_date datetime,
    discount int not null,
    
    foreign key (product_id) references products(product_id)
);
desc product_discounts;

-- product reviews table

create table product_reviews (
	product_id int not null,
    email varchar(100) not null,
    rating int not null,
    review_description longtext,
    review_image_link varchar(255),
    review_date timestamp default current_timestamp,
    
    foreign key (product_id) references products(product_id),
    foreign key (email) references users(email) 
);
desc product_reviews;


-- chats table
create table chats (
	email1 varchar(100),
    email2 varchar(100),
    chat_id int not null auto_increment,
    
    primary key (chat_id),
    foreign key (email1) references users(email), 
    foreign key (email2) references users(email) 
);
desc chats;

-- chat messages table

create table chat_messages (
	chat_id int not null,
    sent_from varchar(100),
    message longtext not null,
    image_link varchar(255),
    message_time timestamp default current_timestamp,
    
    foreign key (sent_from) references users(email),
    foreign key (chat_id) references chats (chat_id)
);

desc chat_messages;

-- cart table
create table carts (
	email varchar(100) not null,
    cart_id int not null auto_increment,
    
    primary key (cart_id),
    foreign key (email) references users(email) 
);
desc carts;

-- cart item table
create table cart_items (
	product_id int not null,
    size varchar(5),
    color varchar(45),
    cart_id int not null,
    
    foreign key (product_id) references products(product_id),
    foreign key (cart_id) references carts(cart_id) 
);
desc cart_items;

-- order table
create table orders (
	email varchar(100) not null,
    order_id int not null auto_increment,
    status enum("pending","confirmed","processing","shipped") default "pending",
    date_delivered datetime default null,    
    
    primary key (order_id),
    foreign key (email) references users(email)
);
desc orders;

-- order items table
create table order_items (
	product_id int not null,
    size varchar(5),
    color varchar(45),
    order_id int not null,
    
    foreign key (product_id) references products(product_id),
    foreign key (order_id) references orders(order_id) 
);
desc order_items;

-- returns table

create table returns (
	order_id int not null,
    email varchar(100) not null,
    return_id int not null auto_increment,
    title varchar(100) not null,
    return_description longtext not null,
    return_image_link varchar(255),
    demand enum("return","refund","warranty") not null,
    return_status enum("pending","confirmed","rejected","processing","complete") default "pending",
    
    primary key (return_id),
    foreign key (order_id) references orders(order_id),
    foreign key (email) references users(email)    
);
desc returns;