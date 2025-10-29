import sqlite3
import os
from werkzeug.security import check_password_hash

def show_users():
    # Chemin vers la base de données
    db_path = os.path.join(os.path.dirname(__file__), 'users.db')
    
    # Vérifier si la base de données existe
    if not os.path.exists(db_path):
        print("La base de données n'existe pas encore.")
        print("Veuillez d'abord exécuter votre application Flask pour initialiser la base de données.")
        return
    
    # Se connecter à la base de données
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Récupérer tous les utilisateurs
    cursor.execute("SELECT id, name, email, password_hash, created_at FROM users ORDER BY id ASC")
    users = cursor.fetchall()
    
    print("=== Liste des utilisateurs ===")
    if not users:
        print("Aucun utilisateur trouvé dans la base de données.")
    else:
        for user in users:
            print(f"{user['id']} - {user['name']} - {user['email']} - {user['created_at']}")
    
    # Fermer la connexion
    conn.close()

if __name__ == "__main__":
    show_users()
