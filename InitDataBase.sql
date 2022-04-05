--Any value in this table can be null
create table Users
(
    userID      varchar(20) primary key,
    email       varchar(20),
    firstName   varchar(20),
    lastName    varchar(20),
    phoneNumber varchar(20),
    birthDate   DATE,
    address varchar(20),
    city varchar(20),
    state varchar(2),
    zipcode varchar(10)

    --make sure all data is there for the address to exist

);
--
-- ALTER table Users --make sure all data is there for the address to exist
-- ADD CONSTRAINT ck_address0 CHECK (address is null OR (address is not null and city is not null and state is not null and zipcode is not null));

--
create table Products (
    pid varchar(20),
    pName varchar(20),
    department varchar(20),
    price numeric(12,2)
);
create table Warehouses (
    wid varchar(20) primary key,
    address varchar(20),
    city varchar(20),
    state varchar(2),
    zipcode varchar(10)
);

--make sure all data is there for the address to exist
-- ALTER TABLE Warehouses
-- ADD CONSTRAINT ck_address2 CHECK (address is null OR (address is not null and city is not null and state is not null and zipcode is not null));
--Stores are classified as a type of warehouse
create table Stores (
    sid varchar(20) primary key,
    wid varchar(20) references Warehouses (wid),
    nickname varchar(20)
);
create table Inventory (
    quantity int,
    held_At varchar(20) references Warehouses (wid),
    pid varchar(20) references Products (pid),
);
create table Sales(
    saleID varchar(20) primary key,
    userID varchar(20) references Users (userID),
    pid varchar(20) references Products (pid),
    wid varchar(20) references Warehouses (wid),
    quantity int
);
create table Shipments (
    trackingID varchar(20) primary key,
    saleID varchar(20) references Sales (saleID),
    address varchar(20),
    city varchar(20),
    state varchar(2),
    zipcode varchar(10)
    );

--make sure all data is there for the address to exist
-- ALTER TABLE Shipments
-- ADD CONSTRAINT ck_address3 CHECK (address is null OR (address is not null and city is not null and state is not null and zipcode is not null));

-- ALTER TABLE USERS
-- DROP CONSTRAINT ck_address0
-- drop table USERS;