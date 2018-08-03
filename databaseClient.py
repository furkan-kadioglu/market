import psycopg2
import hashlib as hsh
def name_hashPass(name,passw):
    return {'user': name,'pass':hsh.sha1(passw.encode()).hexdigest()}
def register_user(name,passw):
    if(not checkUserName(name)):
        connection = psycopg2.connect(dbname='postgres',
                                      user='postgres',
                                      password='admin',
                                      host='localhost',
                                      port='5432')
    
        cursor = connection.cursor()
        cursor.execute("INSERT INTO user_information VALUES (%(user)s,%(pass)s);",
                        name_hashPass(name,passw))
        connection.commit()
        connection.close()
    else :
        return False
    return check_user(name,passw)

def check_user(name,passw):
    connection = psycopg2.connect(dbname='postgres',
                                  user='postgres',
                                  password='admin',
                                  host='localhost',
                                  port='5432')
    
    cursor = connection.cursor()
    cursor.execute(
        ("SELECT * FROM user_information "
        "WHERE (username = %(user)s) AND (passwords = %(pass)s);"), 
        name_hashPass(name,passw))
    lst = cursor.fetchall() 
    connection.close()
    return len(lst) != 0

def checkUserName (name):
    connection = psycopg2.connect(dbname='postgres',
                                  user='postgres',
                                  password='admin',
                                  host='localhost',
                                  port='5432')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM user_information WHERE (username = %(user)s);",
                    {'user':name})
    lst = cursor.fetchall() 
    connection.close()
    return len(lst) != 0