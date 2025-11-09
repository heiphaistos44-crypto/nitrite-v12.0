# NiTrite v3.0 Portable

Installation automatique de 304 applications Windows via une interface graphique simple.

## 🚀 Démarrage Rapide

### Installation

```bash
git clone https://github.com/heiphaistos44-crypto/nitrite-v2-portable.git
cd nitrite-v2-portable
pip install -r requirements.txt
```

### Lancement

**Windows (recommandé):**
```bash
scripts\lanceurs\LANCER_NITRITE.bat
```

**Python:**
```bash
python nitrite_complet.py
```

### Compilation

Pour créer un exécutable standalone :
```bash
python build_nitrite_v3.0_portable.py
```

L'exécutable sera dans : `NiTrite_Autonome/NiTrite_OrdiPlus_v2.exe`

---

## 📦 Contenu

- **304 applications** réparties en 25 catégories
- **Auto-élévation admin** - 1 seul popup UAC au lieu de 10+
- **Interface graphique** intuitive
- **Base de données SQLite** portable

---

## 📁 Structure du Projet

```
nitrite-v2-portable/
├── nitrite_complet.py              # Application principale
├── build_nitrite_v3.0_portable.py  # Script de compilation
├── requirements.txt                # Dépendances Python
│
├── src/                            # Code source
│   ├── config_manager.py           # Gestion de la configuration
│   ├── gui_manager.py              # Interface graphique
│   ├── installer_manager.py        # Gestion des installations
│   ├── elevation_helper.py         # Élévation privilèges admin
│   └── ...
│
├── data/                           # Données
│   ├── programs.json               # Base de 304 applications
│   └── config.json                 # Configuration
│
├── scripts/                        # Scripts utilitaires
│   ├── lanceurs/                   # Scripts de lancement
│   └── tests/                      # Scripts de test/validation
│
└── docs/                           # Documentation
    ├── GUIDE_UTILISATION.md        # Guide complet
    ├── QUICK_START.md              # Démarrage rapide
    └── MISE_A_JOUR.md              # Guide de mise à jour
```

---

## ✨ Fonctionnalités Principales

### 1. Auto-Élévation Admin
- Demande les privilèges administrateur **1 seule fois** au démarrage
- Plus de popups UAC multiples pendant l'installation

### 2. 304 Applications
- 25 catégories (toutes avec 10+ programmes)
- Navigateurs, Pack Office, Antivirus, Multimédia, Développement, etc.
- Installation depuis sources officielles

### 3. Interface Graphique
- Sélection multiple par catégorie
- Barre de progression en temps réel
- Recherche et filtrage

### 4. Mode Portable
- Base de données SQLite locale
- Aucune dépendance externe nécessaire après compilation
- Configuration sauvegardée

---

## 🛠️ Utilisation

### Première Utilisation

1. Lancez avec `scripts\lanceurs\LANCER_NITRITE.bat`
2. Acceptez l'UAC (1 seule fois)
3. Sélectionnez vos applications
4. Cliquez sur "Installer les programmes sélectionnés"

### Utilisations Suivantes

Mode rapide sans vérification des dépendances :
```bash
scripts\lanceurs\LANCER_PORTABLE.bat
```

---

## 🧪 Tests

### Vérifier le nombre d'applications
```bash
python scripts/tests/verifier_nombre_apps.py
```

### Tests unitaires complets
```bash
python scripts/tests/run_tests.py
```

### Vérification d'installation
```bash
python scripts/tests/verifier_installation.py
```

---

## 📋 Configuration Requise

- **OS:** Windows 10/11
- **Python:** 3.8+ (pour développement/compilation uniquement)
- **RAM:** 4 Go minimum
- **Disque:** 500 Mo pour l'application + espace pour les programmes installés

---

## 📚 Documentation

- **[Guide d'Utilisation](docs/GUIDE_UTILISATION.md)** - Documentation complète
- **[Quick Start](docs/QUICK_START.md)** - Démarrage en 3 étapes
- **[Mise à Jour](docs/MISE_A_JOUR.md)** - Comment mettre à jour

---

## 🔧 Développement

### Modifier les Applications

Éditez `data/programs.json` et ajoutez/modifiez les applications :

```json
{
  "Navigateurs": {
    "Google Chrome": {
      "name": "Google Chrome",
      "category": "Navigateurs",
      "url": "https://...",
      "winget_id": "Google.Chrome"
    }
  }
}
```

### Recompiler après Modifications

```bash
python build_nitrite_v3.0_portable.py
```

---

## 📊 Statistiques

- **304 programmes** au total
- **25 catégories**
- **17 tests unitaires**
- **1 popup UAC** seulement
- **~90% de réduction** des interruptions UAC

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créez une branche (`git checkout -b feature/amelioration`)
3. Committez vos changements (`git commit -m 'Ajout fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/amelioration`)
5. Ouvrez une Pull Request

---

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 👤 Auteur

**NiTrite v3.0**
- Version: 3.0.0
- Date: 2025-11-09
- Développé avec l'assistance de Claude AI

---

## 🔗 Liens Utiles

- [Repository GitHub](https://github.com/heiphaistos44-crypto/nitrite-v2-portable)
- [Issues](https://github.com/heiphaistos44-crypto/nitrite-v2-portable/issues)
- [Releases](https://github.com/heiphaistos44-crypto/nitrite-v2-portable/releases)

---

**Note:** Ce projet utilise WinGet et télécharge les applications depuis leurs sources officielles. Aucune modification n'est apportée aux installateurs.
