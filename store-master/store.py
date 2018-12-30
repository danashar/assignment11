from bottle import route, run, template, static_file, get, post, delete, request, os
from sys import argv
import json
import pymysql

connection = pymysql.connect(host="localhost",
                             user="root",
                             password="root9090",
                             db="store",
                             charset="utf8",
                             cursorclass=pymysql.cursors.DictCursor)


@get("/admin")
def admin_portal():
    return template("pages/admin.html")


@get("/")
def index():
    return template("index.html")


@get('/js/<filename:re:.*\.js>')
def javascripts(filename):
    return static_file(filename, root='js')


@get('/css/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='css')


@get('/images/<filename:re:.*\.(jpg|png|gif|ico)>')
def images(filename):
    return static_file(filename, root='images')


@route('/category', method='POST')
def add_category():
    result = {}
    result["STATUS"] = 'ERROR'
    try:
        category = request.forms.get('name')
        if not category:
            result["MSG"] = 'Name parameter is missing'
            result["CODE"] = 400
            return json.dumps(result)
        with connection.cursor() as cursor:
            sql_query = "SELECT * FROM categories WHERE name='{}'".format(category)
            cursor.execute(sql_query)
            response = cursor.fetchone()
            if response:
                result["MSG"] = 'Category already exists'
                result["CODE"] = 200
            else:
                sql_query = "INSERT INTO categories (name) VALUES ('{}')".format(category)
                cursor.execute(sql_query)
                result["STATUS"] = 'SUCCESS'
                result["CODE"] = 201
                result["CAT_ID"] = cursor.lastrowid
                connection.commit()
    except:
        result["MSG"] = 'Internal error'
        result["CODE"] = 500
    return json.dumps(result)


@route('/category/<id>', method='DELETE')
def delete_cat(id):
    result = {}
    result['STATUS'] = 'ERROR'
    try:
        with connection.cursor() as cursor:
            sql_query = "SELECT * FROM categories WHERE cat_id={}".format(id)
            cursor.execute(sql_query)
            response = cursor.fetchone()
            if not response:
                result["MSG"] = 'Category not found'
                result["CODE"] = 404
                return json.dumps(result)
            sql_query = "DELETE FROM categories WHERE cat_id={}".format(id)
            cursor.execute(sql_query)
            connection.commit()
            result["CODE"] = 201
            result["STATUS"] = 'SUCCESS'
    except:
        result["MSG"] = 'Internal error'
        result["CODE"] = 500
    return json.dumps(result)


@route('/categories', method='GET')
def categories():
    result = {}
    try:
        with connection.cursor() as cursor:
            sql_query = "SELECT cat_id as id, name FROM categories"
            cursor.execute(sql_query)
            result['CATEGORIES'] = cursor.fetchall()
        result['CODE'] = 200
        result['STATUS'] = 'SUCCESS'
    except:
        result['CODE'] = 500
        result['STATUS'] = 'ERROR'
        result['MSG'] = 'Internal error'
    return json.dumps(result)


@route('/product', method='POST')
def product():
    result = {}
    try:
        title = request.forms["title"]
        desc = request.forms["desc"]
        price = request.forms["price"]
        img_url = request.forms["img_url"]
        category = request.forms["category"]
        id = request.forms["id"]
        favorite = 1 if 'favorite' in request.forms else 0
        if not title or not desc or not price or not img_url or not category:
            result["STATUS"] = "ERROR"
            result["MSG"] = 'missing parameters'
            result["CODE"] = 400
            return json.dumps(result)
        else:
            with connection.cursor() as cursor:
                sql_cat = "SELECT * FROM categories WHERE cat_id={}".format(category)
                cursor.execute(sql_cat)
            if not cursor.fetchone():
                result["STATUS"] = "ERROR"
                result["MSG"] = 'Category not found'
                result["CODE"] = 404
                return json.dumps(result)
        if id:
            with connection.cursor() as cursor:
                sql_update_product = "UPDATE products SET title='{}', desc='{}', price={}, img_url='{}', category={}, favorite='{}' WHERE product_id={};".format(title, desc, price, img_url, category, favorite, id)
                cursor.execute(sql_update_product)
                connection.commit()
                result["STATUS"] = "SUCCESS"
                result["PRODUCT_ID"] = id
                result["CODE"] = 201
        else:
            with connection.cursor() as cursor:
                sql_add_product = "INSERT INTO products (title, description, price, img_url, category, favorite) VALUES ('{}', '{}', {}, '{}', {}, '{}')".format(title, desc, price, img_url, category, favorite)
                cursor.execute(sql_add_product)
                connection.commit()
                result["STATUS"] = "SUCCESS"
                result["PRODUCT_ID"] = cursor.lastrowid
                result["CODE"] = 201
    except Exception as e:
        print(e)
        result["STATUS"] = "ERROR"
        result["CODE"] = 500
        result["MSG"] = 'Internal error'
    return json.dumps(result)


@get('/product/<id>')
def product(id):
    result = {}
    try:
        with connection.cursor() as cursor:
            sql = "SELECT title FROM products WHERE id={}".format(id)
            cursor.execute(sql)
            if not cursor.fetchone():
                result["STATUS"] = "ERROR"
                result["MSG"] = 'Product not found'
                result["CODE"] = 404
                return json.dumps(result)
            else:
                sql = "SELECT category, description, price, title, favorite, img_url, id FROM products WHERE id={}".format(id)
                cursor.execute(sql)
                result["PRODUCT"] = cursor.fetchone()
                result["STATUS"] = "SUCCESS"
                result["CODE"] = 200
    except:
        result["STATUS"] = "ERROR"
        result["CODE"] = 500
        result["MSG"] = 'internal error'
    return json.dumps(result)

@delete('/product/<id>')
def delete_product(id):
    result = {}
    try:
        with connection.cursor() as cursor:
            sql_query = "SELECT title FROM products WHERE id={}".format(id)
            cursor.execute(sql_query)
            if not cursor.fetchone():
                result["STATUS"] = "ERROR"
                result["MSG"] = 'product not found'
                result["CODE"] = 404
                return json.dumps(result)
            else:
                sql_query = "DELETE FROM products WHERE id={}".format(id)
                cursor.execute(sql_query)
                connection.commit()
                result["PRODUCT"] = cursor.fetchone()
                result["STATUS"] = "SUCCESS"
                result["CODE"] = 201
    except:
        result["STATUS"] = "ERROR"
        result["CODE"] = 500
        result["MSG"] = 'internal error'
    return json.dumps(result)


@get('/products')
def products():
    result = {}
    try:
        with connection.cursor() as cursor:
            sql_query = "SELECT category, description, price, title, favorite, img_url, id FROM products"
            cursor.execute(sql_query)
            result["PRODUCTS"] = cursor.fetchall()
            result["STATUS"] = "SUCCESS"
            result["CODE"] = 200
    except:
        result["STATUS"] = "ERROR"
        result["CODE"] = 500
        result["MSG"] = 'internal error'
    return json.dumps(result)


@get('/category/<id>/products')
def products(id):
    result = {}
    try:
        with connection.cursor() as cursor:
            sql_query = "SELECT title FROM products WHERE category={}".format(id)
            cursor.execute(sql_query)
            if not cursor.fetchone():
                result["STATUS"] = "ERROR"
                result["CODE"] = 404
                return json.dumps(result)
            else:
                sql_query = "SELECT category, description, price, title, favorite, img_url, id FROM products WHERE category={}".format(id)
                cursor.execute(sql_query)
                result["PRODUCTS"] = cursor.fetchall()
                result["STATUS"] = "SUCCESS"
                result["CODE"] = 200
    except:
        result["STATUS"] = "ERROR"
        result["CODE"] = 500
        result["MSG"] = 'internal error'
    return json.dumps(result)

run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
