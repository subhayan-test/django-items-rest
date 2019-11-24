# Sample Django rest framework application

## Some words about the solution
There are 3 different apps inside the main `app`
1. **core** : This app is the core of the application. It stores all the models used in the application
2. **user** : The default user model of the Django authentication system have been modified to include the email address as the `USERNAME_FIELD`
3. **items** : This includes the views/serializers etc to work with out item models .
4. **shopping_cart** : Includes the views/serializers etc to work with our shopping_cart resource

As specified in the task wording there are two types of users :
1. Suppliers : Can buy items
2. Purchasers: Provide the items that can be bought by the suppliers.

Only purchasers can create items in the app and the suppliers can view and add them to their cart .

## How to run the test cases in the application

The solution provided includes a `dockerfile` and a `docker-compose.yml` file. Hence the solution has been dockerized. We can run the test cases as follows:
1. Migrate to the home directory of the app. It contains the following files:
```
(coding-challenge-scoutbee) ~/Desktop/Studies/Codes/coding-challenge-scoutbee:$ ls -ltr
total 48
-rw-r--r--   1 subhayanbhattacharya  staff   310 Nov 15 12:31 dockerfile
-rw-r--r--   1 subhayanbhattacharya  staff   281 Nov 16 11:44 Pipfile
-rw-r--r--   1 subhayanbhattacharya  staff  9767 Nov 16 11:44 Pipfile.lock
-rw-r--r--   1 subhayanbhattacharya  staff   397 Nov 17 19:59 docker-compose.yml
drwxr-xr-x  14 subhayanbhattacharya  staff   448 Nov 18 20:29 app

```
2. Activate the virtualenv using `pipenv install`(The pipfile has been included in the solution) and then `pipenv shell`
3. Run : `docker-compose run app sh -c "pytest -s -v"`

## Checking the test coverage

The code coverage `html` files are stored inside the directory `htmlcov` inside the `app` folder

## Running the application

The application can be run using the following command : `docker-compose up`


## Details about available endpoints

### Creating a user in the system

1. Endpoint : **/api/user/create/**
2. Example Payloads:
```
{
	"email" : "subhayan.here@gmail.com",
	"password": "subhayan",
	"name": "Subhayan Bhattacharya",
	"role" : "Supplier"
}
```
```
{
	"email" : "subhayan.bhattacharya@hotmail.com",
	"password": "subhayan",
	"name": "Subhayan Bhattacharya 2",
	"role" : "Purchaser"
}
```
3. Supported HTTP method : **POST**

### Getting an access token for a user(logging in)

1. Endpoint : **/api/user/token/**
2. Example payload:
```
{
	"email" : "subhayan.bhattacharya@hotmail.com",
	"password": "subhayan"
}
```
3. Supported HTTP method : **POST**

### Getting information about the logged in user(Check the user profile)
1. Endpoint : **/api/user/me/**
2. Header information:
**Authorization JWT access-token**
3. Supported HTTP method : **GET**

### Creating an item(Can only be done by a purchaser)
1. Endpoint : **/api/items/my_items/**
2. Header information:
**Authorization JWT access-token**
3. Supported HTTP method : **POST**
4. Example payload:
```
{
	"name" : "Chair",
	"description": "Sample Chair description",
	"price" : 50,
	"is_draft" : false
}
```

### Getting the list of all created items by the logged in user(Can only be done by the purchaser)
1. Endpoint : **/api/items/my_items/**
2. Header information:
**Authorization JWT access-token**
3. Supported HTTP method : **GET**

### Make changes to an existing item for the logged in user(Can be done by purchaser only)
1. Endpoint : **/api/items/my_items/item/<int:pk>/**
2. Header information:
**Authorization JWT access-token**
3. Supported HTTP method : **PUT, PATCH, DELETE**

### Getting the list of all the items created by all purchasers in the app(Endpoint accessible by purchaser and supplier)
1. Endpoint : **/api/items/all_items/**
2. Header information:
**Authorization JWT access-token**
3. Supported HTTP method : **GET**

### Accessing the details of a single item(Endpoint only accessible by the supplier)
1. Endpoint : **/api/items/item/1/**
2. Header information:
**Authorization JWT access-token**
3. Supported HTTP method : **GET**

### Viewing shopping cart entry for logged in user(Only for item supplier)
1. Endpoint : **/api/shopping_cart/my_cart/**
2. Header information:
**Authorization JWT access-token**
3. Supported HTTP method : **GET**

### Adding an item to shopping cart(Only for supplier)
1. Endpoint : **/api/shopping_cart/my_cart/**
2. Header information:
**Authorization JWT access-token**
3. Supported HTTP method : **POST**
4. Payload:
```
{
  "item_id" : 1
}
```
