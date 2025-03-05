import sqlite3

con = sqlite3.connect("tutorial.db") # connect to the database

cur = con.cursor() # instantiate a cursor obj, cursor obj provides methods to interact with the 
#                    database by executing SQL commands on the database connection object (con)




