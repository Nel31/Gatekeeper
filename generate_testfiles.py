import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_test_files():
    # Données de base
    prenoms = ['Pierre', 'Marie', 'Jean', 'Sophie', 'Laurent', 'Isabelle', 'Michel', 'Nathalie',
               'Alain', 'Catherine', 'Philippe', 'Sylvie', 'Patrick', 'Véronique', 'Bernard',
               'Sandrine', 'Christophe', 'Valérie', 'Thierry', 'Christine', 'Eric', 'Florence',
               'Didier', 'Anne', 'Frédéric', 'Stéphanie', 'Nicolas', 'Céline', 'Olivier', 'Martine',
               'Alexandre', 'Emmanuelle', 'Sébastien', 'Aurélie', 'François', 'Delphine']
    
    noms = ['Martin', 'Bernard', 'Dubois', 'Thomas', 'Robert', 'Richard', 'Petit', 'Durand',
            'Leroy', 'Moreau', 'Simon', 'Laurent', 'Lefebvre', 'Michel', 'Garcia', 'David',
            'Bertrand', 'Roux', 'Vincent', 'Fournier', 'Morel', 'Girard', 'André', 'Lefèvre',
            'Mercier', 'Dupont', 'Lambert', 'Bonnet', 'François', 'Martinez', 'Rousseau',
            'Blanc', 'Guerin', 'Muller', 'Perrin', 'Henry', 'Roussel', 'Nicolas', 'Perrot']
    
    # Profils avec variations
    profils_base = {
        'Développeur': ['Développeur', 'Developpeur', 'Dev'],
        'Chef de projet': ['Chef de projet', 'Chef projet', 'Chef de Projet'],
        'Administrateur système': ['Administrateur système', 'Admin système', 'Administrateur systeme'],
        'Analyste': ['Analyste', 'Analyste fonctionnel', 'Analyste Fonctionnel'],
        'Ingénieur': ['Ingénieur', 'Ingenieur', 'Ing.'],
        'Technicien': ['Technicien', 'Technicien support', 'Tech. Support'],
        'Manager': ['Manager', 'Manageur', 'Chef d\'équipe'],
        'Assistant': ['Assistant', 'Assistant(e)', 'Assistante'],
        'Comptable': ['Comptable', 'Comptable général', 'Compta'],
        'Commercial': ['Commercial', 'Chargé commercial', 'Commercial(e)']
    }
    
    # Directions avec variations
    directions_base = {
        'DSI': ['DSI', 'D.S.I.', 'Direction des Systèmes d\'Information'],
        'Direction Marketing': ['Direction Marketing', 'Marketing', 'Dir. Marketing'],
        'Direction RH': ['Direction RH', 'Ressources Humaines', 'RH'],
        'Direction Financière': ['Direction Financière', 'Finance', 'Dir. Financière'],
        'Direction Commerciale': ['Direction Commerciale', 'Commercial', 'Dir. Commerciale'],
        'Direction Technique': ['Direction Technique', 'Technique', 'Dir. Tech.'],
        'Direction Générale': ['Direction Générale', 'DG', 'Dir. Générale'],
        'Service Informatique': ['Service Informatique', 'Service IT', 'S.I.'],
        'Service Comptabilité': ['Service Comptabilité', 'Comptabilité', 'Compta'],
        'Service Client': ['Service Client', 'Service Clients', 'Support Client']
    }
    
    # Changements de profils réels
    profil_changes = [
        ('Développeur', 'Chef de projet'),
        ('Assistant', 'Manager'),
        ('Technicien', 'Ingénieur'),
        ('Analyste', 'Chef de projet'),
        ('Commercial', 'Manager'),
        ('Comptable', 'Chef comptable'),
        ('Développeur', 'Architecte SI'),
        ('Assistant RH', 'Responsable RH')
    ]
    
    # Changements de directions réels
    direction_changes = [
        ('DSI', 'Direction Marketing'),
        ('Direction RH', 'Direction Financière'),
        ('Service Informatique', 'Direction Technique'),
        ('Direction Commerciale', 'Direction Générale'),
        ('Service Comptabilité', 'Direction Financière')
    ]
    
    # Date d'extraction
    extraction_date = datetime.now()
    
    # Initialiser les listes
    rh_data = []
    ext_data = []
    user_counter = 1
    
    # 1. Sans anomalie (20 lignes)
    for i in range(20):
        code = f"U{str(user_counter).zfill(4)}"
        nom_prenom = f"{random.choice(noms)} {random.choice(prenoms)}"
        profil_key = random.choice(list(profils_base.keys()))
        profil = profils_base[profil_key][0]
        direction_key = random.choice(list(directions_base.keys()))
        direction = directions_base[direction_key][0]
        last_login = (extraction_date - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
        
        rh_data.append({
            'CODE_UTILISATEUR': code,
            'NOM_UTILISATEUR': nom_prenom,
            'PROFIL': profil,
            'LIBELLE SERVICE': direction
        })
        
        ext_data.append({
            'Identifiant': code,
            'Nom et Prénoms': nom_prenom,
            'Profil utilisateur': profil,
            'Direction': direction,
            'DATE DE DERNIERE CONNEXION': last_login,
            'DATE_EXTRACTION': extraction_date.strftime('%Y-%m-%d'),
            'ACTIF': 0
        })
        user_counter += 1
    
    # 2. Compte non RH (15 lignes)
    for i in range(15):
        code = f"U{str(user_counter).zfill(4)}"
        nom_prenom = f"{random.choice(noms)} {random.choice(prenoms)}"
        profil = random.choice(list(profils_base.keys()))
        direction = random.choice(list(directions_base.keys()))
        last_login = (extraction_date - timedelta(days=random.randint(1, 90))).strftime('%Y-%m-%d')
        
        # Seulement dans extraction
        ext_data.append({
            'Identifiant': code,
            'Nom et Prénoms': nom_prenom,
            'Profil utilisateur': profil,
            'Direction': direction,
            'DATE DE DERNIERE CONNEXION': last_login,
            'DATE_EXTRACTION': extraction_date.strftime('%Y-%m-%d'),
            'ACTIF': 0
        })
        user_counter += 1
    
    # 3. Changements réels de profil (15 lignes)
    for i in range(15):
        code = f"U{str(user_counter).zfill(4)}"
        nom_prenom = f"{random.choice(noms)} {random.choice(prenoms)}"
        old_profil, new_profil = random.choice(profil_changes)
        direction = random.choice(list(directions_base.keys()))
        last_login = (extraction_date - timedelta(days=random.randint(1, 60))).strftime('%Y-%m-%d')
        
        rh_data.append({
            'CODE_UTILISATEUR': code,
            'NOM_UTILISATEUR': nom_prenom,
            'PROFIL': new_profil,
            'LIBELLE SERVICE': direction
        })
        
        ext_data.append({
            'Identifiant': code,
            'Nom et Prénoms': nom_prenom,
            'Profil utilisateur': old_profil,
            'Direction': direction,
            'DATE DE DERNIERE CONNEXION': last_login,
            'DATE_EXTRACTION': extraction_date.strftime('%Y-%m-%d'),
            'ACTIF': 0
        })
        user_counter += 1
    
    # 4. Variations mineures profil (10 lignes)
    for i in range(10):
        code = f"U{str(user_counter).zfill(4)}"
        nom_prenom = f"{random.choice(noms)} {random.choice(prenoms)}"
        profil_key = random.choice(list(profils_base.keys()))
        profil_rh = profils_base[profil_key][0]
        profil_ext = profils_base[profil_key][random.randint(1, len(profils_base[profil_key])-1)]
        direction = random.choice(list(directions_base.keys()))
        last_login = (extraction_date - timedelta(days=random.randint(1, 45))).strftime('%Y-%m-%d')
        
        rh_data.append({
            'CODE_UTILISATEUR': code,
            'NOM_UTILISATEUR': nom_prenom,
            'PROFIL': profil_rh,
            'LIBELLE SERVICE': direction
        })
        
        ext_data.append({
            'Identifiant': code,
            'Nom et Prénoms': nom_prenom,
            'Profil utilisateur': profil_ext,
            'Direction': direction,
            'DATE DE DERNIERE CONNEXION': last_login,
            'DATE_EXTRACTION': extraction_date.strftime('%Y-%m-%d'),
            'ACTIF': 0
        })
        user_counter += 1
    
    # 5. Changements réels direction (10 lignes)
    for i in range(10):
        code = f"U{str(user_counter).zfill(4)}"
        nom_prenom = f"{random.choice(noms)} {random.choice(prenoms)}"
        profil = random.choice(list(profils_base.keys()))
        old_dir, new_dir = random.choice(direction_changes)
        last_login = (extraction_date - timedelta(days=random.randint(1, 50))).strftime('%Y-%m-%d')
        
        rh_data.append({
            'CODE_UTILISATEUR': code,
            'NOM_UTILISATEUR': nom_prenom,
            'PROFIL': profil,
            'LIBELLE SERVICE': new_dir
        })
        
        ext_data.append({
            'Identifiant': code,
            'Nom et Prénoms': nom_prenom,
            'Profil utilisateur': profil,
            'Direction': old_dir,
            'DATE DE DERNIERE CONNEXION': last_login,
            'DATE_EXTRACTION': extraction_date.strftime('%Y-%m-%d'),
            'ACTIF': 0
        })
        user_counter += 1
    
    # 6. Variations mineures direction (10 lignes)
    for i in range(10):
        code = f"U{str(user_counter).zfill(4)}"
        nom_prenom = f"{random.choice(noms)} {random.choice(prenoms)}"
        profil = random.choice(list(profils_base.keys()))
        direction_key = random.choice(list(directions_base.keys()))
        direction_rh = directions_base[direction_key][0]
        direction_ext = directions_base[direction_key][random.randint(1, len(directions_base[direction_key])-1)]
        last_login = (extraction_date - timedelta(days=random.randint(1, 40))).strftime('%Y-%m-%d')
        
        rh_data.append({
            'CODE_UTILISATEUR': code,
            'NOM_UTILISATEUR': nom_prenom,
            'PROFIL': profil,
            'LIBELLE SERVICE': direction_rh
        })
        
        ext_data.append({
            'Identifiant': code,
            'Nom et Prénoms': nom_prenom,
            'Profil utilisateur': profil,
            'Direction': direction_ext,
            'DATE DE DERNIERE CONNEXION': last_login,
            'DATE_EXTRACTION': extraction_date.strftime('%Y-%m-%d'),
            'ACTIF': 0
        })
        user_counter += 1
    
    # 7. Inactifs (10 lignes)
    for i in range(10):
        code = f"U{str(user_counter).zfill(4)}"
        nom_prenom = f"{random.choice(noms)} {random.choice(prenoms)}"
        profil = random.choice(list(profils_base.keys()))
        direction = random.choice(list(directions_base.keys()))
        last_login = (extraction_date - timedelta(days=random.randint(121, 365))).strftime('%Y-%m-%d')
        
        rh_data.append({
            'CODE_UTILISATEUR': code,
            'NOM_UTILISATEUR': nom_prenom,
            'PROFIL': profil,
            'LIBELLE SERVICE': direction
        })
        
        ext_data.append({
            'Identifiant': code,
            'Nom et Prénoms': nom_prenom,
            'Profil utilisateur': profil,
            'Direction': direction,
            'DATE DE DERNIERE CONNEXION': last_login,
            'DATE_EXTRACTION': extraction_date.strftime('%Y-%m-%d'),
            'ACTIF': 0
        })
        user_counter += 1
    
    # 8. Cas combinés (10 lignes)
    for i in range(10):
        code = f"U{str(user_counter).zfill(4)}"
        nom_prenom = f"{random.choice(noms)} {random.choice(prenoms)}"
        
        if i < 4:  # Inactif + changement profil
            old_profil, new_profil = random.choice(profil_changes)
            direction = random.choice(list(directions_base.keys()))
            last_login = (extraction_date - timedelta(days=random.randint(150, 300))).strftime('%Y-%m-%d')
            
            rh_data.append({
                'CODE_UTILISATEUR': code,
                'NOM_UTILISATEUR': nom_prenom,
                'PROFIL': new_profil,
                'LIBELLE SERVICE': direction
            })
            
            ext_data.append({
                'Identifiant': code,
                'Nom et Prénoms': nom_prenom,
                'Profil utilisateur': old_profil,
                'Direction': direction,
                'DATE DE DERNIERE CONNEXION': last_login,
                'DATE_EXTRACTION': extraction_date.strftime('%Y-%m-%d'),
                'ACTIF': 0
            })
        
        elif i < 7:  # Non RH + inactif
            profil = random.choice(list(profils_base.keys()))
            direction = random.choice(list(directions_base.keys()))
            last_login = (extraction_date - timedelta(days=random.randint(130, 250))).strftime('%Y-%m-%d')
            
            # Seulement dans extraction
            ext_data.append({
                'Identifiant': code,
                'Nom et Prénoms': nom_prenom,
                'Profil utilisateur': profil,
                'Direction': direction,
                'DATE DE DERNIERE CONNEXION': last_login,
                'DATE_EXTRACTION': extraction_date.strftime('%Y-%m-%d'),
                'ACTIF': 0
            })
        
        else:  # Multiple changements
            old_profil, new_profil = random.choice(profil_changes)
            old_dir, new_dir = random.choice(direction_changes)
            last_login = (extraction_date - timedelta(days=random.randint(10, 80))).strftime('%Y-%m-%d')
            
            rh_data.append({
                'CODE_UTILISATEUR': code,
                'NOM_UTILISATEUR': nom_prenom,
                'PROFIL': new_profil,
                'LIBELLE SERVICE': new_dir
            })
            
            ext_data.append({
                'Identifiant': code,
                'Nom et Prénoms': nom_prenom,
                'Profil utilisateur': old_profil,
                'Direction': old_dir,
                'DATE DE DERNIERE CONNEXION': last_login,
                'DATE_EXTRACTION': extraction_date.strftime('%Y-%m-%d'),
                'ACTIF': 0
            })
        
        user_counter += 1
    
    # Ajouter quelques comptes suspendus
    for row in random.sample(ext_data, 5):
        row['ACTIF'] = 1
    
    # Créer les DataFrames
    df_rh = pd.DataFrame(rh_data)
    df_ext = pd.DataFrame(ext_data)
    
    # Diviser RH en deux fichiers (60/40)
    split_index = int(len(df_rh) * 0.6)
    df_rh_in = df_rh.iloc[:split_index]
    df_rh_out = df_rh.iloc[split_index:]
    
    # Sauvegarder les fichiers
    df_rh_in.to_excel('test_rh_in.xlsx', index=False)
    df_rh_out.to_excel('test_rh_out.xlsx', index=False)
    df_ext.to_excel('test_extraction.xlsx', index=False)
    
    print(f"✅ Fichiers générés avec succès:")
    print(f"   - test_rh_in.xlsx: {len(df_rh_in)} lignes")
    print(f"   - test_rh_out.xlsx: {len(df_rh_out)} lignes")
    print(f"   - test_extraction.xlsx: {len(df_ext)} lignes")
    print(f"\n📊 Répartition des cas:")
    print(f"   - Sans anomalie: 20")
    print(f"   - Compte non RH: 15")
    print(f"   - Changements profil: 15")
    print(f"   - Variations profil: 10")
    print(f"   - Changements direction: 10")
    print(f"   - Variations direction: 10")
    print(f"   - Inactifs: 10")
    print(f"   - Cas combinés: 10")

if __name__ == "__main__":
    generate_test_files()