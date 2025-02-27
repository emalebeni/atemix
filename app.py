from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import random
import uuid

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'

def get_db():
    conn = sqlite3.connect('marche.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    db = get_db()
    cursor = db.cursor()
    
    # Obtenir le nombre total de catégories
    cursor.execute("SELECT COUNT(*) FROM categories")
    total_categories = cursor.fetchone()  # Obtenez le premier élément du tuple
    
    # Obtenir le nombre total de produits
    cursor.execute("SELECT COUNT(*) FROM products")
    total_produits = cursor.fetchone()  # Obtenez le premier élément du tuple
    
    # Obtenir le nombre de produits par catégorie
    cursor.execute("""
        SELECT c.name, COUNT(p.id) 
        FROM categories c
        LEFT JOIN products p ON c.id = p.category_id 
        GROUP BY c.name
    """)
    produits_par_categorie = cursor.fetchall()  # Liste de tuples (nom_catégorie, nombre_produits)

    db.commit()
    db.close()
    
    # Préparer les données pour le graphique linéaire
    categories = [row[0] for row in produits_par_categorie]  # Extraire les noms des catégories
    produits_counts = [row[1] for row in produits_par_categorie]  # Extraire le nombre de produits

    return render_template('dashboard.html', 
                           total_categories=total_categories, 
                           total_produits=total_produits, 
                           produits_par_categorie=produits_counts,
                           categories=categories)

@app.route('/categories')
def list_categories():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    db.commit()
    db.close()
    return render_template('list_categories.html', categories=categories)

@app.route('/categories/add', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name =request.form["name"]
        description = request.form.get("description", "")
        identifier = str(uuid.uuid4())[:8]
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO categories (identifier, name, description) VALUES (?, ?, ?)", 
                       (identifier, name, description))
        db.commit()
        db.close()
        return redirect(url_for('list_categories'))
    return render_template('add_category.html')
        
@app.route('/products')
def list_products():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT products.*, categories.name as category_name FROM products JOIN categories ON products.category_id = categories.id")
    products = cursor.fetchall()
    db.commit()
    db.close()
    return render_template('list_products.html', products=products)  

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    
    if request.method == 'POST':
        name = request.form["name"]
        price = float(request.form["price"])
        stock = int(request.form["stock"])
        category_id = int(request.form["category_id"])
        description = request.form.get("description", "")
        identifier = str(uuid.uuid4())[:8]
        
        cursor.execute("INSERT INTO products (identifier, name, price, stock, category_id, description) VALUES (?,?,?,?,?, ?)", 
                       (identifier, name, price, stock, category_id, description))
        db.commit()
        db.close()
        return redirect(url_for('list_products'))
    return render_template('add_products.html', categories=categories)

@app.route('/edit_category/<string:identifier>', methods=['GET', 'POST'])
def edit_category(identifier):
    db = get_db()
    category = db.execute("SELECT * FROM categories WHERE identifier = ?", (identifier,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        db.execute("UPDATE categories SET name = ?, description = ?, updated_at = CURRENT_TIMESTAMP WHERE identifier = ?",
                   (name, description, identifier))
        db.commit()
        return redirect(url_for('list_categories'))

    return render_template('edit_category.html', category=category)


@app.route('/edit_product/<string:identifier>', methods=['GET', 'POST'])
def edit_product(identifier):
    db = get_db()
    product = db.execute("SELECT * FROM products WHERE identifier = ?", (identifier,)).fetchone()
    categories = db.execute("SELECT * FROM categories").fetchall()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        stock = request.form['stock']
        category_id = request.form['category_id']

        db.execute("UPDATE products SET name = ?, description = ?, price = ?, stock = ?, category_id = ?, updated_at = CURRENT_TIMESTAMP WHERE identifier = ?",
                   (name, description, price, stock, category_id, identifier))
        db.commit()
        return redirect(url_for('list_products'))

    return render_template('edit_product.html', product=product, categories=categories)

@app.route('/delete_category/<string:identifier>', methods=['POST'])
def delete_category(identifier):
    db = get_db()
    db.execute("DELETE FROM categories WHERE identifier = ?", (identifier,))
    db.commit()
    return redirect(url_for('list_categories'))

@app.route('/delete_product/<string:identifier>', methods=['POST'])
def delete_product(identifier):
    db = get_db()
    db.execute("DELETE FROM products WHERE identifier = ?", (identifier,))
    db.commit()
    return redirect(url_for('list_products'))

if __name__ == "__main__":
    app.run(debug=True)
