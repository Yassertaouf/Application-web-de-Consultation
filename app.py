from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "farire_secret_key"

# Configuration Email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'taouf.yasser@gmail.com'
app.config['MAIL_PASSWORD'] = 'fpqw uhhm vnyk dlno'  
app.config['MAIL_DEFAULT_SENDER'] = 'taouf.yasser@gmail.com'

mail = Mail(app)

# Configuration des uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Taoufiki20061222",
            database="farire_db"
        )
        return db
    except Error as e:
        print(f"Erreur de connexion MySQL : {e}")
        return None

def envoyer_notification_admin(sujet, message):
    """Fonction pour envoyer des notifications à l'admin"""
    try:
        msg = Message(
            subject=sujet,
            recipients=['taouf.yasser@gmail.com'],
            sender=app.config['MAIL_DEFAULT_SENDER']
        )
        msg.html = message
        mail.send(msg)
        print(f"Email envoyé à l'admin: {sujet}")
        return True
    except Exception as e:
        print(f"Erreur envoi email admin: {e}")
        return False

def envoyer_newsletter_produit(produit_data):
    """Fonction pour envoyer une newsletter à TOUS les clients"""
    try:
        db = get_db_connection()
        if not db:
            return False

            
            
        cursor = db.cursor(dictionary=True)
        
        # Recuperer TOUS les clients
        cursor.execute("SELECT email, name FROM clients")
        clients = cursor.fetchall()
        cursor.close()
        db.close()
        
        if not clients:
            print("Aucun client dans la base")
            return True
            
        sujet = f"Nouveau produit chez Farire - {produit_data['nom']}"
        
        message_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .product-info {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                .price {{ font-size: 24px; color: #28a745; font-weight: bold; }}
                .button {{ display: inline-block; background: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Nouveau Produit Disponible !</h1>
                    <p>Decouvrez notre derniere addition</p>
                </div>
                
                <h2>{produit_data['nom']}</h2>
                
                <div class="product-info">
                    <p><strong>Description :</strong><br>
                    {produit_data.get('description', 'Decouvrez ce nouveau produit exceptionnel!')}</p>
                    
                    <div class="price">{produit_data['prix']} DH</div>
                    
                    <p><strong>Categorie :</strong> {produit_data.get('categorie_nom', 'General')}</p>
                    <p><strong>Stock disponible :</strong> {produit_data['stock']} unites</p>
                </div>
                
                <div style="text-align: center;">
                    <a href="http://localhost:5000/produit" class="button">Voir tous nos produits</a>
                </div>
                
                <div class="footer">
                    <p>Merci de votre fidelite,<br><strong>L'equipe Farire</strong></p>
                    <p>Contact: +212 XXX XXX XXX<br>Email: contact@farire.com</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Envoyer à chaque client
        emails_envoyes = 0
        for client in clients:
            try:
                msg = Message(
                    subject=sujet,
                    recipients=[client['email']],
                    sender=app.config['MAIL_DEFAULT_SENDER']
                )
                msg.html = message_html
                mail.send(msg)
                emails_envoyes += 1
                print(f"Newsletter envoyee à: {client['email']}")
                
            except Exception as e:
                print(f"Erreur envoi à {client['email']}: {e}")
        
        print(f"Newsletters envoyees à {emails_envoyes}/{len(clients)} clients")
        return True
        
    except Exception as e:
        print(f"Erreur newsletter: {e}")
        return False

def init_database():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Taoufiki20061222"
        )
        cursor = db.cursor()
        
        cursor.execute("CREATE DATABASE IF NOT EXISTS farire_db")
        cursor.execute("USE farire_db")
        
        # Table clients
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                telephone VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table admins
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table devis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devis (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                sujet VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                statut VARCHAR(20) DEFAULT 'nouveau'
            )
        ''')
        
        # Table categories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(100) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table produits
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produits (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                description TEXT,
                prix DECIMAL(10,2) NOT NULL,
                categorie_id INT,
                image_url VARCHAR(500),
                stock INT DEFAULT 0,
                statut ENUM('actif', 'inactif') DEFAULT 'actif',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (categorie_id) REFERENCES categories(id)
            )
        ''')
        
        # Table services
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                description TEXT,
                prix DECIMAL(10,2),
                duree_estimee VARCHAR(50),
                statut ENUM('actif', 'inactif') DEFAULT 'actif',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Verifier si un admin existe
        cursor.execute("SELECT COUNT(*) FROM admins")
        if cursor.fetchone()[0] == 0:
            hashed_password = generate_password_hash('admin123')
            cursor.execute(
                "INSERT INTO admins (name, email, password) VALUES (%s, %s, %s)",
                ('Administrateur', 'admin@farire.com', hashed_password)
            )
        
        # Inserer des categories par defaut
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            categories = [
                ('PC Bureautique', 'Ordinateurs pour le bureau'),
                ('Imprimantes', 'Differentes modeles et types'),
                ('Papier', 'Papier impression et fournitures'),
                ('Chaises Gamer', 'Chaises gaming et bureau'),
                ('Accessoires', 'Accessoires informatiques')
            ]
            cursor.executemany(
                "INSERT INTO categories (nom, description) VALUES (%s, %s)",
                categories
            )
        
        db.commit()
        cursor.close()
        db.close()
        print("Base de données initialisée avec succès")
        
    except Error as e:
        print(f"Erreur d'initialisation: {e}")

# Page d'accueil
@app.route('/')
def home():
    return render_template('Home.html')

# Route pour traiter les messages de contact
@app.route('/contact', methods=['POST'])
def contact():
    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        email = request.form.get('email', '').strip()
        sujet = request.form.get('sujet', '').strip()
        message = request.form.get('message', '').strip()
        
        if not nom or not email or not sujet or not message:
            flash("Tous les champs sont obligatoires", "danger")
            return redirect(url_for('home'))
        
        db = get_db_connection()
        if db:
            cursor = db.cursor()
            try:
                cursor.execute(
                    "INSERT INTO devis (nom, email, sujet, message) VALUES (%s, %s, %s, %s)",
                    (nom, email, sujet, message)
                )
                db.commit()
                flash("Votre message a ete envoye avec succes", "success")
            except Error as e:
                db.rollback()
                flash("Erreur lors de l'envoi du message", "danger")
            finally:
                cursor.close()
                db.close()
        
        return redirect(url_for('home'))

# Page de connexion admin
@app.route('/login-admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db_connection()
        if db:
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM admins WHERE email=%s", (email,))
            admin = cursor.fetchone()
            cursor.close()
            db.close()

            if admin:
                stored_password = admin['password']
                
                if stored_password and stored_password.startswith(('pbkdf2:', 'scrypt:')):
                    if check_password_hash(stored_password, password):
                        session['admin_id'] = admin['id']
                        session['admin_name'] = admin['name']
                        session['role'] = 'admin'
                        flash("Connexion admin reussie", "success")
                        return redirect(url_for('dashboard'))
                    else:
                        flash("Mot de passe incorrect", "danger")
                else:
                    if stored_password == password:
                        new_hashed_password = generate_password_hash(password)
                        db = get_db_connection()
                        if db:
                            cursor = db.cursor()
                            cursor.execute(
                                "UPDATE admins SET password=%s WHERE email=%s",
                                (new_hashed_password, email)
                            )
                            db.commit()
                            cursor.close()
                            db.close()
                        
                        session['admin_id'] = admin['id']
                        session['admin_name'] = admin['name']
                        session['role'] = 'admin'
                        flash("Connexion admin reussie", "success")
                        return redirect(url_for('dashboard'))
                    else:
                        flash("Identifiants admin incorrects", "danger")
            else:
                flash("Admin non trouve", "danger")

    return render_template('login-admin.html')

# Dashboard admin
@app.route('/dashboard')
def dashboard():
    if 'role' not in session or session['role'] != 'admin':
        flash("Acces refuse", "danger")
        return redirect(url_for('login_admin'))
    
    db = get_db_connection()
    total_clients = 0
    recent_clients = []
    total_devis = 0
    nouveaux_devis = 0
    recent_devis = []
    total_produits = 0
    
    if db:
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT COUNT(*) as total FROM clients")
            total_clients = cursor.fetchone()['total']
            
            cursor.execute("SELECT name, email, created_at FROM clients ORDER BY created_at DESC LIMIT 6")
            recent_clients = cursor.fetchall()
            
            cursor.execute("SELECT COUNT(*) as total FROM devis")
            total_devis = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as nouveaux FROM devis WHERE statut = 'nouveau'")
            nouveaux_devis = cursor.fetchone()['nouveaux']
            
            cursor.execute("SELECT id, nom, email, sujet, created_at, statut FROM devis ORDER BY created_at DESC LIMIT 6")
            recent_devis = cursor.fetchall()
            
            cursor.execute("SELECT COUNT(*) as total FROM produits")
            total_produits = cursor.fetchone()['total']
            
        except Error as e:
            flash("Erreur lors de la recuperation des donnees", "danger")
        finally:
            cursor.close()
            db.close()
    
    return render_template('dashboard.html', 
                         total_clients=total_clients,
                         recent_clients=recent_clients,
                         total_devis=total_devis,
                         nouveaux_devis=nouveaux_devis,
                         recent_devis=recent_devis,
                         total_produits=total_produits,
                         admin_name=session.get('admin_name'),
                         now=datetime.now())

# ROUTE DEBUG DEVIS
@app.route('/debug-devis')
def debug_devis():
    db = get_db_connection()
    if not db:
        return "ERREUR: Impossible de se connecter à la base"
    
    cursor = db.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM devis ORDER BY created_at DESC")
        devis = cursor.fetchall()
        
        result = "<h1>DEBUG DEVIS</h1>"
        result += f"<p>Total devis: {len(devis)}</p>"
        result += "<table border='1'><tr><th>ID</th><th>Nom</th><th>Email</th><th>Sujet</th><th>Statut</th><th>Date</th></tr>"
        
        for d in devis:
            result += f"""
                <tr>
                    <td>{d['id']}</td>
                    <td>{d['nom']}</td>
                    <td>{d['email']}</td>
                    <td>{d['sujet']}</td>
                    <td>{d['statut']}</td>
                    <td>{d['created_at'].strftime('%d/%m/%Y %H:%M') if d['created_at'] else 'N/A'}</td>
                </tr>
            """
        
        result += "</table>"
        result += "<p><a href='/dashboard'>Retour au dashboard</a></p>"
        
        return result
        
    except Exception as e:
        return f"Erreur: {e}"
    finally:
        cursor.close()
        db.close()

# ROUTE DEBUG IMAGES
@app.route('/debug-images')
def debug_images():
    """Page de debogage pour voir toutes les images uploadées"""
    if 'role' not in session or session['role'] != 'admin':
        flash("Accès refuse", "danger")
        return redirect(url_for('login_admin'))
    
    # Lister tous les fichiers dans le dossier uploads
    upload_folder = app.config['UPLOAD_FOLDER']
    images = []
    
    if os.path.exists(upload_folder):
        for filename in os.listdir(upload_folder):
            if allowed_file(filename):
                file_path = os.path.join(upload_folder, filename)
                file_size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
                images.append({
                    'name': filename,
                    'size': file_size,
                    'path': f'static/uploads/{filename}'
                })
    
    # Recuperer les produits avec leurs images
    db = get_db_connection()
    produits_images = []
    if db:
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, nom, image_url FROM produits WHERE image_url IS NOT NULL")
            produits_images = cursor.fetchall()
        except Error as e:
            print(f"Erreur DB: {e}")
        finally:
            cursor.close()
            db.close()
    
    return render_template('debug_images.html',
                         images=images,
                         produits_images=produits_images,
                         total_images=len(images),
                         admin_name=session.get('admin_name'))

# PAGE PRODUITS
@app.route('/produit')
def produit():
    db = get_db_connection()
    produits_par_categorie = {}
    
    if db:
        cursor = db.cursor(dictionary=True)
        try:
            # Recuperer TOUS les produits actifs
            cursor.execute("""
                SELECT p.*, c.nom as categorie_nom 
                FROM produits p 
                LEFT JOIN categories c ON p.categorie_id = c.id 
                WHERE p.statut = 'actif'
                ORDER BY c.nom, p.created_at DESC
            """)
            produits_dynamiques = cursor.fetchall()
            
            print(f"Produits trouves: {len(produits_dynamiques)}")
            
            for produit in produits_dynamiques:
                print(f"  - {produit['nom']}: image_url = '{produit['image_url']}'")
                
                # Grouper par categorie
                categorie = produit['categorie_nom'] or 'Non categorise'
                if categorie not in produits_par_categorie:
                    produits_par_categorie[categorie] = []
                
                produit['type'] = 'dynamique'
                produits_par_categorie[categorie].append(produit)
                
        except Error as e:
            print(f"ERREUR recuperation produits: {e}")
            flash("Erreur lors du chargement des produits", "danger")
        finally:
            cursor.close()
            db.close()
    
    client_info = {
        'name': session.get('user_name'),
        'email': session.get('user_email')
    }
    
    return render_template('Produit.html', 
                         client=client_info,
                         produits_par_categorie=produits_par_categorie)

# AJOUTER UN PRODUIT
@app.route('/admin/produits/ajouter', methods=['GET', 'POST'])
def ajouter_produit():
    if 'role' not in session or session['role'] != 'admin':
        flash("Acces refuse", "danger")
        return redirect(url_for('login_admin'))
    
    if request.method == 'POST':
        print("=" * 50)
        print("DEBUT AJOUT PRODUIT")
        print("=" * 50)
        
        # Recuperation des données
        nom = request.form.get('nom')
        description = request.form.get('description')
        prix = request.form.get('prix')
        categorie_id = request.form.get('categorie_id')
        stock = request.form.get('stock')
        
        print(f"Donnees recues:")
        print(f"   - Nom: {nom}")
        print(f"   - Prix: {prix}")
        print(f"   - Categorie ID: {categorie_id}")
        print(f"   - Stock: {stock}")
        print(f"   - Description: {description}")
        
        # Verification des champs obligatoires
        if not nom or not prix or not categorie_id or not stock:
            flash("Tous les champs obligatoires doivent être remplis", "danger")
            return redirect(url_for('ajouter_produit'))
        
        # GESTION DE L'IMAGE
        image_filename = None
        
        if 'image' in request.files:
            file = request.files['image']
            print(f"Fichier recu: {file.filename}")
            
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
                    filename = timestamp + filename
                    
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    image_filename = filename
                    print(f"Image sauvegardee: {image_filename}")
                else:
                    print("Format de fichier non supporte")
                    flash("Format de fichier non supporte", "danger")
                    return redirect(url_for('ajouter_produit'))
        
        # INSERTION DANS LA BASE DE DONNEES
        db = get_db_connection()
        if not db:
            print("Erreur de connexion à la base de données")
            flash("Erreur de connexion à la base de données", "danger")
            return redirect(url_for('ajouter_produit'))
        
        cursor = db.cursor()
        try:
            print(f"Insertion en base de données...")
            cursor.execute("""
                INSERT INTO produits (nom, description, prix, categorie_id, image_url, stock)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nom, description, float(prix), int(categorie_id), image_filename, int(stock)))
            
            db.commit()
            product_id = cursor.lastrowid
            
            # NOTIFICATION EMAIL DIRECTE
            try:
                print("Envoi notification nouveau produit...")
                
                cursor_select = db.cursor(dictionary=True)
                cursor_select.execute("""
                    SELECT p.*, c.nom as categorie_nom 
                    FROM produits p 
                    LEFT JOIN categories c ON p.categorie_id = c.id 
                    WHERE p.id = %s
                """, (product_id,))
                produit_data = cursor_select.fetchone()
                cursor_select.close()
                
                # Notification à l'admin
                sujet_admin = f"Nouveau produit ajoute - {produit_data['nom']}"
                message_admin = f"""
                <h2>NOUVEAU PRODUIT AJOUTE</h2>
                
                <p><strong>Details du produit :</strong></p>
                <ul>
                    <li><strong>Nom :</strong> {produit_data['nom']}</li>
                    <li><strong>Prix :</strong> {produit_data['prix']} DH</li>
                    <li><strong>Categorie :</strong> {produit_data.get('categorie_nom', 'Non categorise')}</li>
                    <li><strong>Stock :</strong> {produit_data['stock']} unites</li>
                    <li><strong>Description :</strong> {produit_data.get('description', 'Aucune description')}</li>
                </ul>
                
                <p><strong>Informations techniques :</strong></p>
                <ul>
                    <li><strong>Image :</strong> {produit_data.get('image_url', 'Aucune image')}</li>
                    <li><strong>Ajoute par :</strong> Administrateur</li>
                    <li><strong>Date :</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</li>
                </ul>
                
                <p><strong>Actions :</strong></p>
                <ul>
                    <li>Verifier l'image du produit</li>
                    <li>Controler le stock</li>
                    <li>Promouvoir le produit</li>
                </ul>
                
                <br>
                <p>Cordialement,<br>Systeme de notification Farire</p>
                """
                
                envoyer_notification_admin(sujet_admin, message_admin)
                
                # Newsletter aux clients
                print("Envoi newsletter aux clients...")
                envoyer_newsletter_produit(produit_data)
                
            except Exception as e:
                print(f"Notification echouee: {e}")
            # FIN NOTIFICATION
            
            print(f"PRODUIT AJOUTE AVEC SUCCES")
            print(f"   - ID du produit: {product_id}")
            print(f"   - Image en base: {image_filename}")
            
            flash("Produit ajoute avec succes! Les clients ont ete notifies.", "success")
            
        except Error as e:
            db.rollback()
            print(f"ERREUR DB: {e}")
            flash(f"Erreur lors de l'ajout du produit: {e}", "danger")
        finally:
            cursor.close()
            db.close()
        
        print("=" * 50)
        print("FIN AJOUT PRODUIT")
        print("=" * 50)
        
        return redirect(url_for('admin_produits'))
    
    # GET - Afficher le formulaire
    db = get_db_connection()
    categories = []
    if db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categories ORDER BY nom")
        categories = cursor.fetchall()
        cursor.close()
        db.close()
    
    return render_template('ajouter_produit.html', 
                         categories=categories,
                         admin_name=session.get('admin_name'))

# Gestion des produits (Admin)
@app.route('/admin/produits')
def admin_produits():
    if 'role' not in session or session['role'] != 'admin':
        flash("Acces refuse", "danger")
        return redirect(url_for('login_admin'))
    
    db = get_db_connection()
    produits = []
    categories = []
    
    if db:
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT p.*, c.nom as categorie_nom 
                FROM produits p 
                LEFT JOIN categories c ON p.categorie_id = c.id 
                ORDER BY p.created_at DESC
            """)
            produits = cursor.fetchall()
            
            cursor.execute("SELECT * FROM categories ORDER BY nom")
            categories = cursor.fetchall()
            
        except Error as e:
            flash("Erreur lors de la recuperation des produits", "danger")
        finally:
            cursor.close()
            db.close()
    
    return render_template('admin_produits.html', 
                         produits=produits, 
                         categories=categories,
                         admin_name=session.get('admin_name'))

# Modifier un produit
@app.route('/admin/produits/modifier/<int:id>', methods=['GET', 'POST'])
def modifier_produit(id):
    if 'role' not in session or session['role'] != 'admin':
        flash("Acces refuse", "danger")
        return redirect(url_for('login_admin'))
    
    db = get_db_connection()
    if not db:
        flash("Erreur de connexion a la base de donnees", "danger")
        return redirect(url_for('admin_produits'))
    
    if request.method == 'POST':
        nom = request.form['nom']
        description = request.form['description']
        prix = float(request.form['prix'])
        categorie_id = int(request.form['categorie_id'])
        stock = int(request.form['stock'])
        statut = request.form['statut']
        
        # Recuperer l'image actuelle
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT image_url FROM produits WHERE id=%s", (id,))
        produit_actuel = cursor.fetchone()
        cursor.close()
        
        image_url = produit_actuel['image_url'] if produit_actuel else None
        
        # Verifier si une nouvelle image est uploadée
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    
                    # Creer le dossier si necessaire
                    if not os.path.exists(app.config['UPLOAD_FOLDER']):
                        os.makedirs(app.config['UPLOAD_FOLDER'])
                    
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    
                    # Mettre à jour avec la nouvelle image
                    image_url = filename
                    flash(f"Nouvelle image '{filename}' uploadée avec succes", "success")
                else:
                    flash("Format d'image non supporte", "danger")
                    return redirect(url_for('modifier_produit', id=id))
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE produits 
                SET nom=%s, description=%s, prix=%s, categorie_id=%s, image_url=%s, stock=%s, statut=%s
                WHERE id=%s
            """, (nom, description, prix, categorie_id, image_url, stock, statut, id))
            db.commit()
            flash("Produit modifie avec succes", "success")
        except Error as e:
            db.rollback()
            flash("Erreur lors de la modification du produit", "danger")
        finally:
            cursor.close()
            db.close()
        
        return redirect(url_for('admin_produits'))
    
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produits WHERE id=%s", (id,))
    produit = cursor.fetchone()
    cursor.execute("SELECT * FROM categories ORDER BY nom")
    categories = cursor.fetchall()
    cursor.close()
    db.close()
    
    if not produit:
        flash("Produit non trouve", "danger")
        return redirect(url_for('admin_produits'))
    
    return render_template('modifier_produit.html', 
                         produit=produit, 
                         categories=categories,
                         admin_name=session.get('admin_name'))

# Supprimer un produit
@app.route('/admin/produits/supprimer/<int:id>')
def supprimer_produit(id):
    if 'role' not in session or session['role'] != 'admin':
        flash("Acces refuse", "danger")
        return redirect(url_for('login_admin'))
    
    db = get_db_connection()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM produits WHERE id=%s", (id,))
            db.commit()
            flash("Produit supprime avec succes", "success")
        except Error as e:
            db.rollback()
            flash("Erreur lors de la suppression du produit", "danger")
        finally:
            cursor.close()
            db.close()
    
    return redirect(url_for('admin_produits'))

# Gestion des services (Admin)
@app.route('/admin/services')
def admin_services():
    if 'role' not in session or session['role'] != 'admin':
        flash("Acces refuse", "danger")
        return redirect(url_for('login_admin'))
    
    db = get_db_connection()
    services = []
    
    if db:
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM services ORDER BY created_at DESC")
            services = cursor.fetchall()
        except Error as e:
            flash("Erreur lors de la recuperation des services", "danger")
        finally:
            cursor.close()
            db.close()
    
    return render_template('admin_services.html', 
                         services=services,
                         admin_name=session.get('admin_name'))

# Page d'inscription client
@app.route('/register-client', methods=['GET', 'POST'])
def register_client():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm-password', '').strip()

        if not name or not email or not password:
            flash("Les champs nom, email et mot de passe sont obligatoires", "danger")
            return render_template('register-client.html')

        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas", "danger")
            return render_template('register-client.html')

        hashed_password = generate_password_hash(password)

        db = get_db_connection()
        if db:
            cursor = db.cursor()
            try:
                cursor.execute("SELECT id FROM clients WHERE email=%s", (email,))
                if cursor.fetchone():
                    flash("Cet email est deja utilise", "danger")
                    return render_template('register-client.html')

                cursor.execute(
                    "INSERT INTO clients (name, email, password) VALUES (%s, %s, %s)", 
                    (name, email, hashed_password)
                )
                db.commit()
                
                # NOTIFICATION EMAIL DIRECTE
                try:
                    print("Envoi notification nouveau client...")
                    
                    cursor_select = db.cursor(dictionary=True)
                    cursor_select.execute("SELECT * FROM clients WHERE email=%s", (email,))
                    client_data = cursor_select.fetchone()
                    cursor_select.close()
                    
                    sujet = f"Nouveau client inscrit - {client_data['name']}"
                    message_html = f"""
                    <h2>NOUVEAU CLIENT INSCRIT</h2>
                    
                    <p><strong>Informations du client :</strong></p>
                    <ul>
                        <li><strong>Nom :</strong> {client_data['name']}</li>
                        <li><strong>Email :</strong> {client_data['email']}</li>
                        <li><strong>Telephone :</strong> {client_data.get('telephone', 'Non renseigne')}</li>
                        <li><strong>Date d'inscription :</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</li>
                    </ul>
                    
                    <p><strong>Actions possibles :</strong></p>
                    <ul>
                        <li>Contacter le client pour le welcome call</li>
                        <li>Ajouter à la newsletter</li>
                        <li>Envoyer des offres speciales</li>
                    </ul>
                    
                    <br>
                    <p>Cordialement,<br>Systeme de notification Farire</p>
                    """
                    
                    envoyer_notification_admin(sujet, message_html)
                    
                except Exception as e:
                    print(f"Notification echouee: {e}")
                # FIN NOTIFICATION
                
                flash("Compte client cree avec succes", "success")
                return redirect(url_for('login_client'))
                
            except Error as e:
                db.rollback()
                flash("Erreur lors de la creation du compte", "danger")
            finally:
                cursor.close()
                db.close()

    return render_template('register-client.html')

# Page de connexion client
@app.route('/login-client', methods=['GET', 'POST'])
def login_client():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db_connection()
        if db:
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM clients WHERE email=%s", (email,))
            user = cursor.fetchone()
            
            if user:
                stored_password = user['password']
                
                if stored_password and stored_password.startswith(('pbkdf2:', 'scrypt:')):
                    if check_password_hash(stored_password, password):
                        session['user_id'] = user['id']
                        session['user_name'] = user['name']
                        session['user_email'] = user['email']
                        session['role'] = 'client'
                        flash(f"Connexion reussie. Bienvenue {user['name']}!", "success")
                        return redirect(url_for('produit'))
                    else:
                        flash("Email ou mot de passe incorrect", "danger")
                else:
                    if stored_password == password:
                        new_hashed_password = generate_password_hash(password)
                        db_update = get_db_connection()
                        if db_update:
                            cursor_update = db_update.cursor()
                            cursor_update.execute(
                                "UPDATE clients SET password=%s WHERE email=%s",
                                (new_hashed_password, email)
                            )
                            db_update.commit()
                            cursor_update.close()
                            db_update.close()
                        
                        session['user_id'] = user['id']
                        session['user_name'] = user['name']
                        session['user_email'] = user['email']
                        session['role'] = 'client'
                        flash(f"Connexion reussie. Bienvenue {user['name']}!", "success")
                        return redirect(url_for('produit'))
                    else:
                        flash("Email ou mot de passe incorrect", "danger")
            else:
                flash("Email ou mot de passe incorrect", "danger")
            
            cursor.close()
            db.close()

    return render_template('login-client.html')

# Page Services
@app.route('/service')
def service():
    return render_template('Service.html')

# Page de profil client
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash("Veuillez vous connecter", "danger")
        return redirect(url_for('login_client'))
    
    db = get_db_connection()
    if db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clients WHERE id=%s", (session['user_id'],))
        client = cursor.fetchone()
        cursor.close()
        db.close()
        
        if client:
            return render_template('profile.html', client=client)
    
    flash("Client non trouve", "danger")
    return redirect(url_for('produit'))

# Deconnexion
@app.route('/logout')
def logout():
    session.clear()
    flash("Deconnexion reussie", "success")
    return redirect(url_for('home'))

    
    # Lister les fichiers existants
    files = os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else []
    print(f"Fichiers dans uploads: {len(files)}")
    for file in files:
        print(f"   - {file}")
    
    init_database()

if __name__ == '__main__':
    
    app.run(debug=True)