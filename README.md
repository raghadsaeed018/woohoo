# Snugglez - A virtual pet simulator with finance options
#### Video Demo:  https://youtu.be/0xPieNia1Z0?si=Z1N9zif8KbrTVRc3
#### Description:

# Briefly: 
My CS50 final project is a virtual pet simulator called Snugglez, it also has finance options such as buying and selling pets. it's a web application built using HTML, CSS and JavaScript mostly for the client side, and Python with the flask framework and SQLite for the server side.

# app.py:
In app.py, theres the flask application, where there are routes defined, and what function these routes do when called. The main routes are ['/', 'login', 'register', 'logout', 'shop', 'sell', 'inventory']. There are also some other routes such as 'Pet action', theyre made for Ajax requests that are written in multiple .html files in the javascript parts.

# helpers.py: 
there are only 2 functions in helpers.py, one called apology that re-renders the current page with a message in a hidden badge 
in that html page. And the other function is decorator function called 'login_required', its useful in app.py for the routes that require login before accessing. 

# templates:
In templates, there are all the html files, all of them extending from layout.html, and each file's name describes what it displays and what it does. Index shows the pets the current logged in user owns, and they also can snuggle with their pets there (feed them, pet them, give them accessories, and boost their happiness). Inventory shows all the food and accessories the current logged in user owns. login and register are forms that do as they say. The shop is where all the available pets, food, and accessories available in the database are displayed where the user can purchase and browse through them. And lastly, in layout.html theres the basic layout of the website, which is mostly inspired from the finance problem set. Each of these files include the amout of coins the user owns. 

# static:
Static has styles.css which has all the css for all the html files, mostly in a inheritance style. It includes mostly the styles i personally preferred for my website, other than that, its all using bootstrap for styling and building the website. Static includes a .ico file that has the logo of the website, that is visible in the nav bar and the tab of the website. Static also includes all the images used in the web app which is usually rendered using a sqlite query from the database. 

# woohoo.db:
This is the database connected to phpLiteAdmin where i have 3 tables, one called users which has all the users registered in my website (their username, a hash of their password, and the cash they own), and one called animals which has all the pets, food, and accessories available in the shop, and one called portfolio which has all the pets and food and accessories every user owns, using a foreign key for both the user and the item they own. 


This was my final project for CS50!