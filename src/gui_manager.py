"""
Gestionnaire d'interface graphique pour NiTrite v.2
VERSION COMPLÈTE - Affiche TOUS les programmes disponibles (80+)
MODE SOMBRE Ordi Plus
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
from pathlib import Path
from datetime import datetime
import logging
import webbrowser
import subprocess
import win32com.client
import winshell
from PIL import Image, ImageTk

class NiTriteGUIComplet:
    """Interface graphique complète affichant TOUS les programmes"""
    
    # Couleurs du thème Ordi Plus (plus foncé que le site)
    DARK_BG = '#1a1a1a'          # Fond principal - Gris très foncé
    DARK_BG2 = '#2a2a2a'         # Fond secondaire - Gris foncé
    DARK_BG3 = '#333333'         # Fond tertiaire - Gris moyen foncé
    DARK_FG = '#ffffff'          # Texte principal - Blanc pur
    DARK_FG2 = '#cccccc'         # Texte secondaire - Gris clair
    ACCENT_ORANGE = '#FF6B00'    # Orange Ordi Plus (couleur principale)
    ACCENT_BLUE = '#003366'      # Bleu foncé Ordi Plus
    ACCENT_GREEN = '#00CC66'     # Vert succès
    ACCENT_RED = '#ff3333'       # Rouge erreur
    ACCENT_YELLOW = '#FFB800'    # Jaune warning (variante orange)
    BORDER = '#444444'           # Bordures
    
    def __init__(self, root, installer_manager=None, config_manager=None):
        self.root = root
        self.installer_manager = installer_manager
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Variables pour les programmes
        self.program_vars = {}
        self.programs = {}
        self.category_frames = {}
        self.category_widgets = {}
        self.collapsed_categories = set()
        self.is_installing = False
        
        # Charger le logo Ordi Plus pour l'arrière-plan
        self.load_background_logo()
        
        # Charger TOUS les programmes
        self.load_all_programs()
        
        # Interface
        self.setup_window()
        self.setup_styles()
        self.create_main_interface()
        
        # Protocole de fermeture propre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_background_logo(self):
        """Charge le logo Ordi Plus pour l'arrière-plan"""
        try:
            import sys
            # Chemins compatibles PyInstaller
            if getattr(sys, 'frozen', False):
                # Mode exécutable
                base_path = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else Path(sys.executable).parent
            else:
                # Mode développement
                base_path = Path(__file__).parent.parent
            
            logo_path = base_path / 'assets' / 'logo_ordiplus_bg.png'
            if logo_path.exists():
                img = Image.open(logo_path)
                self.bg_logo = ImageTk.PhotoImage(img)
            else:
                self.bg_logo = None
                self.logger.warning(f"Logo Ordi Plus non trouvé : {logo_path}")
        except Exception as e:
            self.bg_logo = None
            self.logger.error(f"Erreur chargement logo : {e}")
    
    def setup_window(self):
        """Configure la fenêtre principale en plein écran"""
        self.root.title("🚀 NiTrite v.2 - Installateur Automatique de Programmes (80+ applications)")
        
        # MAXIMISER complètement la fenêtre
        self.root.state('zoomed')
        
        # Configuration responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Couleur de fond SOMBRE
        self.root.configure(bg=self.DARK_BG)
        
        # Icône (si disponible)
        try:
            import sys
            # Chemins compatibles PyInstaller
            if getattr(sys, 'frozen', False):
                base_path = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else Path(sys.executable).parent
            else:
                base_path = Path(__file__).parent.parent
            
            icon_path = base_path / 'assets' / 'icon.ico'
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception as e:
            self.logger.warning(f"Impossible de charger l'icône: {e}")
    
    def setup_styles(self):
        """Configure les styles pour mode sombre"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configuration globale MODE SOMBRE
        style.configure('.',
                       background=self.DARK_BG,
                       foreground=self.DARK_FG,
                       fieldbackground=self.DARK_BG2,
                       bordercolor=self.BORDER,
                       darkcolor=self.DARK_BG,
                       lightcolor=self.DARK_BG3)
        
        # Labels
        style.configure('TLabel',
                       background=self.DARK_BG,
                       foreground=self.DARK_FG)
        
        # Frames
        style.configure('TFrame',
                       background=self.DARK_BG)
        
        # LabelFrames
        style.configure('TLabelframe',
                       background=self.DARK_BG,
                       foreground=self.ACCENT_BLUE,
                       bordercolor=self.BORDER)
        style.configure('TLabelframe.Label',
                       background=self.DARK_BG,
                       foreground=self.ACCENT_BLUE,
                       font=('Segoe UI', 10, 'bold'))
        
        # Boutons
        style.configure('TButton',
                       background=self.DARK_BG2,
                       foreground=self.DARK_FG,
                       bordercolor=self.BORDER,
                       font=('Segoe UI', 8))
        style.map('TButton',
                 background=[('active', self.DARK_BG3), ('pressed', self.ACCENT_ORANGE)],  # Orange au clic
                 foreground=[('active', self.DARK_FG)])
        
        # Checkbuttons
        style.configure('TCheckbutton',
                       background=self.DARK_BG,
                       foreground=self.DARK_FG,
                       font=('Segoe UI', 9))
        style.map('TCheckbutton',
                 background=[('active', self.DARK_BG)])
        
        # Styles spécialisés
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 16, 'bold'),
                       foreground=self.ACCENT_ORANGE,  # Orange Ordi Plus pour le titre
                       background=self.DARK_BG)
        
        style.configure('Category.TLabel', 
                       font=('Segoe UI', 11, 'bold'),
                       foreground=self.ACCENT_ORANGE,  # Orange Ordi Plus pour les catégories
                       background=self.DARK_BG)
        
        style.configure('Action.TButton', 
                       font=('Segoe UI', 11, 'bold'),
                       padding=8,
                       background=self.ACCENT_ORANGE,  # Orange Ordi Plus pour les boutons d'action
                       foreground='#ffffff')
        style.map('Action.TButton',
                 background=[('active', '#ff8533'), ('pressed', '#cc5500')])  # Variations d'orange
        
        style.configure('Select.TButton', 
                       font=('Segoe UI', 9, 'bold'),
                       padding=4)
    
    def load_all_programs(self):
        """Charge TOUS les programmes depuis programs.json"""
        try:
            import sys
            # Chemins compatibles PyInstaller
            if getattr(sys, 'frozen', False):
                base_path = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else Path(sys.executable).parent
            else:
                base_path = Path(__file__).parent.parent
            
            programs_file = base_path / 'data' / 'programs.json'
            
            if programs_file.exists():
                with open(programs_file, 'r', encoding='utf-8') as f:
                    self.programs = json.load(f)
                
                # Compter le total
                total = sum(len(progs) if isinstance(progs, dict) else 0 
                          for progs in self.programs.values())
                
                self.logger.info(f"✅ {total} programmes chargés depuis {len(self.programs)} catégories")
                
            else:
                self.logger.warning("⚠️ Fichier programs.json non trouvé")
                self.programs = {}
                
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du chargement des programmes: {e}")
            self.programs = {}
    
    def create_main_interface(self):
        """Crée l'interface principale avec PanedWindow redimensionnable et logo en arrière-plan"""
        # Frame principal MODE SOMBRE
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Logo en arrière-plan (si disponible) - placé en premier pour être derrière
        if self.bg_logo:
            bg_label = tk.Label(main_frame, image=self.bg_logo, bg=self.DARK_BG)
            bg_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # En-tête
        self.create_header(main_frame)
        
        # Barre d'actions (AVANT pour initialiser selection_label)
        self.create_action_bar(main_frame)
        
        # PanedWindow pour séparer programmes et outils avec diviseur draggable
        self.paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        self.paned_window.grid(row=2, column=0, sticky="nsew")
        
        # Frame gauche pour les programmes
        programs_container = ttk.Frame(self.paned_window)
        self.paned_window.add(programs_container, weight=4)

        # Frame droit pour les outils (ratio 4:3 pour élargir le panneau d'outils)
        tools_container = ttk.Frame(self.paned_window)
        self.paned_window.add(tools_container, weight=3)
        
        # Zone principale des programmes (dans le container gauche)
        self.create_programs_area_in_container(programs_container)
        
        # Panel d'outils à droite (dans le container droit)
        self.create_tools_panel_in_container(tools_container)
    
    def create_header(self, parent):
        """Crée l'en-tête"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        # Calcul du nombre total de programmes
        total_programs = sum(len(progs) if isinstance(progs, dict) else 0 
                           for progs in self.programs.values())
        
        # Titre MODE SOMBRE
        title_label = ttk.Label(
            header_frame,
            text=f"🎯 NITRITE v.2 - {total_programs} APPLICATIONS",
            style='Title.TLabel'
        )
        title_label.pack()
        
        # Sous-titre MODE SOMBRE
        subtitle_label = ttk.Label(
            header_frame,
            text="Installation silencieuse • Sources officielles",
            font=('Segoe UI', 9),
            foreground=self.DARK_FG2,
            background=self.DARK_BG
        )
        subtitle_label.pack(pady=(2, 0))
    
    def create_programs_area_in_container(self, parent):
        """Crée la zone des programmes avec TOUS les programmes affichés"""
        programs_frame = ttk.LabelFrame(parent, text="📋 PROGRAMMES", padding=3)
        programs_frame.pack(fill="both", expand=True)
        programs_frame.grid_rowconfigure(0, weight=1)
        programs_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas principal avec scrollbar MODE SOMBRE
        self.main_canvas = tk.Canvas(
            programs_frame, 
            bg=self.DARK_BG,
            highlightthickness=0
        )
        
        main_scrollbar = ttk.Scrollbar(programs_frame, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)
        
        # Configuration du scroll
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=1800)
        self.main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        # Placement
        self.main_canvas.grid(row=0, column=0, sticky="nsew")
        main_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind scroll avec molette
        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Créer les checkboxes pour TOUS les programmes
        self.create_all_program_checkboxes()
        
        # Mettre à jour le compteur initial
        if hasattr(self, 'selection_label'):
            self.update_selection_count()
    
    def safe_update_selection_count(self):
        """Version sûre de update_selection_count"""
        if hasattr(self, 'selection_label'):
            self.update_selection_count()
    
    def create_all_program_checkboxes(self):
        """Crée les checkboxes pour TOUS les programmes par catégorie"""
        row = 0
        
        # Icônes pour les catégories
        category_icons = {
            'Navigateurs': '🌐',
            'Développement': '💻',
            'Bureautique': '📝',
            'Multimédia': '🎨',
            'Utilitaires': '🔧',
            'Communication': '💬',
            'Jeux': '🎮',
            'Sécurité': '🛡️',
            'Internet': '🌍',
            'Outils OrdiPlus': '🛠️',
            'Pack Office': '📦'
        }
        
        # Ordre d'affichage des catégories (OrdiPlus en premier)
        category_order = [
            'Outils OrdiPlus',
            'Pack Office',
            'Navigateurs',
            'Bureautique',
            'Multimédia',
            'Développement',
            'Utilitaires',
            'Sécurité',
            'Communication',
            'Jeux',
            'Internet'
        ]
        
        # Afficher dans l'ordre défini
        sorted_categories = []
        for cat in category_order:
            if cat in self.programs and isinstance(self.programs[cat], dict) and len(self.programs[cat]) > 0:
                sorted_categories.append((cat, self.programs[cat]))
        
        # Ajouter les catégories manquantes
        for category, programs in sorted(self.programs.items()):
            if category not in category_order and isinstance(programs, dict) and len(programs) > 0:
                sorted_categories.append((category, programs))
        
        for category, programs in sorted_categories:
            icon = category_icons.get(category, '📦')
            
            # Titre de catégorie avec bouton plier/déplier MODE SOMBRE
            category_header = ttk.Frame(self.scrollable_frame)
            category_header.grid(row=row, column=0, sticky="ew", pady=(8, 3), padx=5)
            category_header.grid_columnconfigure(1, weight=1)
            
            # Bouton plier/déplier
            collapse_btn = ttk.Button(
                category_header,
                text="▼",
                width=3,
                command=lambda cat=category: self.toggle_category(cat)
            )
            collapse_btn.grid(row=0, column=0, padx=(0, 5))
            
            # Label de catégorie MODE SOMBRE
            category_label = ttk.Label(
                category_header,
                text=f"{icon} {category.upper()} - {len(programs)} programmes",
                style='Category.TLabel',
                font=('Segoe UI', 11, 'bold')
            )
            category_label.grid(row=0, column=1, sticky="w")
            
            # Bouton sélectionner tout dans cette catégorie
            select_cat_btn = ttk.Button(
                category_header,
                text="✓ Tout",
                width=8,
                command=lambda c=category: self.select_category(c)
            )
            select_cat_btn.grid(row=0, column=2, padx=(5, 0))
            
            row += 1
            
            # Ligne de séparation MODE SOMBRE
            separator = ttk.Separator(self.scrollable_frame, orient='horizontal')
            separator.grid(row=row, column=0, sticky="ew", pady=(0, 3))
            row += 1
            
            # Frame pour les programmes de cette catégorie MODE SOMBRE
            programs_container = ttk.Frame(self.scrollable_frame)
            programs_container.grid(row=row, column=0, sticky="ew", padx=15)
            
            # 5 COLONNES pour gagner de la place
            for i in range(5):
                programs_container.grid_columnconfigure(i, weight=1)
            
            # Stocker les widgets pour le plier/déplier
            self.category_widgets[category] = {
                'collapse_btn': collapse_btn,
                'programs_container': programs_container
            }
            
            # Programmes en 5 colonnes pour maximiser l'affichage
            prog_row = 0
            col = 0
            
            checkbox_count = 0
            button_count = 0
            
            for program_name, program_info in sorted(programs.items()):
                # Frame pour ce programme (COMPACT)
                prog_frame = ttk.Frame(programs_container)
                prog_frame.grid(row=prog_row, column=col, sticky="w", padx=3, pady=2)
                
                # Vérifier si c'est un désinstallateur (catégorie spéciale)
                is_uninstaller = category == "Désinstallateurs Antivirus"
                
                # Tous les programmes ont maintenant une checkbox
                checkbox_count += 1
                var = tk.BooleanVar()
                self.program_vars[program_name] = var
                
                # Checkbox avec nom du programme (POLICE PLUS PETITE)
                checkbox = ttk.Checkbutton(
                    prog_frame,
                    text=program_name,
                    variable=var,
                    style='Program.TCheckbutton'
                )
                checkbox.pack(anchor='w')
                
                # Configurer la police plus petite
                checkbox.configure(style='Program.TCheckbutton')
                
                # Lier manuellement le changement
                var.trace_add('write', lambda *args: self.safe_update_selection_count())
                
                # Pour les désinstallateurs, ajouter un bouton de téléchargement en plus
                if is_uninstaller:
                    download_url = program_info.get('download_url', '')
                    if download_url:
                        download_btn = ttk.Button(
                            prog_frame,
                            text="📥 Télécharger",
                            command=lambda url=download_url: self.open_download_link(url),
                            width=15
                        )
                        download_btn.pack(anchor='w', padx=(20, 0), pady=(2, 0))
                
                # Description (SI DISPONIBLE et COURTE)
                desc = program_info.get('description', '')
                if desc and len(desc) < 60:
                    desc_label = ttk.Label(
                        prog_frame,
                        text=desc[:40] + "..." if len(desc) > 40 else desc,
                        font=('Segoe UI', 7),
                        foreground='#7f8c8d'
                    )
                    desc_label.pack(anchor='w', padx=(20, 0))
                
                # Passer à la colonne suivante
                col += 1
                if col >= 5:  # 5 colonnes
                    col = 0
                    prog_row += 1
            
            # Logger le nombre de checkboxes créées pour cette catégorie
            if checkbox_count > 0 or button_count > 0:
                self.logger.info(f"📊 {category}: {checkbox_count} checkboxes, {button_count} boutons")
            
            row += 1
    
    def toggle_category(self, category):
        """Plie ou déplie une catégorie"""
        if category in self.category_widgets:
            widgets = self.category_widgets[category]
            
            if category in self.collapsed_categories:
                # Déplier
                widgets['programs_container'].grid()
                widgets['collapse_btn'].config(text="▼")
                self.collapsed_categories.remove(category)
            else:
                # Plier
                widgets['programs_container'].grid_remove()
                widgets['collapse_btn'].config(text="▶")
                self.collapsed_categories.add(category)
            
            # Mettre à jour la région de défilement
            self.scrollable_frame.update_idletasks()
            self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
    
    def create_action_bar(self, parent):
        """Crée la barre d'actions"""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        action_frame.grid_columnconfigure(1, weight=1)
        
        # Label de sélection (PLUS COMPACT)
        self.selection_label = ttk.Label(
            action_frame,
            text="0 programme(s) sélectionné(s)",
            font=('Segoe UI', 11, 'bold'),
            foreground='#2c3e50'
        )
        self.selection_label.grid(row=0, column=0, sticky="w", padx=5)
        
        # Barre de progression (PLUS PETITE)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            action_frame,
            variable=self.progress_var,
            maximum=100,
            length=200
        )
        self.progress_bar.grid(row=0, column=1, sticky="ew", padx=15)
        
        # Bouton d'organisation des programmes
        self.organize_button = ttk.Button(
            action_frame,
            text="🔄 ORGANISER",
            command=self.open_organize_dialog,
            style='Action.TButton'
        )
        self.organize_button.grid(row=0, column=2, sticky="e", padx=5)
        
        # Bouton d'ajout de programme
        self.add_program_button = ttk.Button(
            action_frame,
            text="➕ AJOUTER",
            command=self.add_custom_program,
            style='Action.TButton'
        )
        self.add_program_button.grid(row=0, column=3, sticky="e", padx=5)
        
        # Bouton d'installation (PLUS COMPACT)
        self.install_button = ttk.Button(
            action_frame,
            text="🚀 INSTALLER",
            command=self.start_installation,
            style='Action.TButton',
            state='disabled'  # Initialement désactivé
        )
        self.install_button.grid(row=0, column=4, sticky="e", padx=5)
    
    def _on_mousewheel(self, event):
        """Gestion du scroll avec la molette"""
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def select_all_programs(self):
        """Sélectionne TOUS les programmes"""
        for var in self.program_vars.values():
            var.set(True)
        self.update_selection_count()
    
    def deselect_all_programs(self):
        """Désélectionne tous les programmes"""
        for var in self.program_vars.values():
            var.set(False)
        self.update_selection_count()
    
    def select_category(self, category):
        """Sélectionne tous les programmes d'une catégorie"""
        if category in self.programs:
            for program_name in self.programs[category]:
                if program_name in self.program_vars:
                    self.program_vars[program_name].set(True)
        self.update_selection_count()
    
    def update_selection_count(self):
        """Met à jour le compteur de sélection"""
        selected_count = sum(1 for var in self.program_vars.values() if var.get())
        total_count = len(self.program_vars)
        
        self.selection_label.config(
            text=f"{selected_count} programme(s) sélectionné(s) sur {total_count}"
        )
        
        # Activer/désactiver le bouton
        if selected_count > 0:
            self.install_button.config(state='normal')
        else:
            self.install_button.config(state='disabled')
    
    def start_installation(self):
        """Démarre l'installation ou l'exécution de commandes"""
        self.logger.info("🔔 Bouton INSTALLER cliqué !")
        
        selected_programs = [
            name for name, var in self.program_vars.items() if var.get()
        ]
        
        self.logger.info(f"📊 Programmes sélectionnés: {len(selected_programs)}")
        self.logger.info(f"📋 Liste: {selected_programs}")
        
        if not selected_programs:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner au moins un programme ou commande.")
            return
        
        # Séparer les commandes des programmes
        commands_to_run = []
        programs_to_install = []
        
        self.logger.info(f"🔍 Recherche dans programs_db...")
        
        for prog_name in selected_programs:
            # Chercher le programme dans la base de données
            prog_info = None
            for category_progs in self.programs.values():
                if prog_name in category_progs:
                    prog_info = category_progs[prog_name]
                    break
            
            self.logger.info(f"🔍 {prog_name} -> prog_info={prog_info is not None}, is_command={prog_info.get('is_command', False) if prog_info else 'N/A'}")
            
            if prog_info and prog_info.get('is_command'):
                commands_to_run.append((prog_name, prog_info))
                self.logger.info(f"➡️ {prog_name} ajouté aux commandes")
            else:
                programs_to_install.append(prog_name)
                self.logger.info(f"➡️ {prog_name} ajouté aux programmes à installer")
        
        # Exécuter les commandes immédiatement
        if commands_to_run:
            self.logger.info(f"⚡ Exécution de {len(commands_to_run)} commande(s)")
            self.execute_commands(commands_to_run)
        
        # Installer les programmes si nécessaire
        if programs_to_install:
            self.logger.info(f"📦 {len(programs_to_install)} programme(s) à installer")
            # Confirmation
            if messagebox.askyesno(
                "Confirmation d'installation",
                f"Installer {len(programs_to_install)} programme(s) ?\n\n"
                "L'installation sera automatique et silencieuse."
            ):
                self.logger.info(f"✅ Installation confirmée pour {len(programs_to_install)} programmes")
                
                # Désactiver le bouton d'installation
                self.is_installing = True
                self.install_button.config(state='disabled', text="⏳ Installation...")
                
                # Lancer l'installation dans un thread séparé
                if self.installer_manager:
                    self.logger.info(f"🚀 Démarrage du thread d'installation...")
                    install_thread = threading.Thread(
                        target=self.installer_manager.install_programs,
                        args=(
                            programs_to_install,
                            self.update_progress,
                            self.on_installation_finished
                        ),
                        daemon=True
                    )
                    install_thread.start()
                else:
                    self.logger.error("❌ InstallerManager n'est pas disponible!")
                    messagebox.showerror(
                        "Erreur",
                        "Le gestionnaire d'installation n'est pas disponible!"
                    )
                    self.is_installing = False
                    self.install_button.config(state='normal', text="🚀 INSTALLER")
            else:
                self.logger.info("❌ Installation annulée par l'utilisateur")
        elif not commands_to_run:
            self.logger.warning("⚠️ Aucune action à effectuer")
            messagebox.showwarning("Aucune sélection", "Aucune action à effectuer.")
    
    def execute_commands(self, commands_list):
        """Exécute les commandes Windows sélectionnées"""
        import subprocess
        
        executed_count = 0
        failed_count = 0
        
        for prog_name, prog_info in commands_list:
            command = prog_info.get('command', '')
            admin_required = prog_info.get('admin_required', False)
            
            try:
                if admin_required:
                    # Exécuter en mode administrateur avec PowerShell
                    ps_command = f'Start-Process cmd.exe -ArgumentList "/c {command}" -Verb RunAs'
                    subprocess.Popen(
                        ["powershell.exe", "-Command", ps_command],
                        shell=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                else:
                    # Exécuter normalement
                    subprocess.Popen(
                        command,
                        shell=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                
                self.logger.info(f"✅ Commande exécutée: {prog_name}")
                executed_count += 1
                
            except Exception as e:
                self.logger.error(f"❌ Erreur lors de l'exécution de {prog_name}: {e}")
                failed_count += 1
        
        # Désélectionner les commandes exécutées
        for prog_name, _ in commands_list:
            if prog_name in self.program_vars:
                self.program_vars[prog_name].set(False)
        
        self.update_selection_count()
        
        # Message de résultat
        if executed_count > 0:
            message = f"✅ {executed_count} commande(s) exécutée(s)"
            if failed_count > 0:
                message += f"\n⚠️ {failed_count} échec(s)"
            
            messagebox.showinfo("Commandes exécutées", message)

    
    def update_progress(self, value, message=""):
        """Met à jour la barre de progression"""
        self.progress_var.set(value)
        if message:
            self.selection_label.config(text=f"⏳ {message}")
        self.root.update_idletasks()
    
    def log_installation_message(self, message, level="info"):
        """Affiche un message de log"""
        print(f"[{level.upper()}] {message}")
        self.logger.info(message)
    
    def on_installation_finished(self, success):
        """Appelé quand l'installation est terminée"""
        self.is_installing = False
        self.install_button.config(state='normal', text="🚀 INSTALLER")
        
        if success:
            messagebox.showinfo(
                "Installation terminée",
                "✅ L'installation de tous les programmes sélectionnés est terminée !\n\n"
                "Vérifiez vos applications installées."
            )
            # Créer le dossier "Outils de nettoyage" si nécessaire
            self.create_cleanup_folder()
            # Désélectionner tous les programmes
            self.deselect_all_programs()
        else:
            messagebox.showwarning(
                "Installation interrompue",
                "⚠️ L'installation a été interrompue.\n\n"
                "Certains programmes peuvent avoir été installés."
            )
        
        self.update_progress(0, "")
        self.update_selection_count()
    
    def create_cleanup_folder(self):
        """Crée le dossier 'Outils de nettoyage' sur le bureau avec les raccourcis"""
        try:
            import os
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            cleanup_folder = Path(desktop) / "Outils de nettoyage"
            cleanup_folder.mkdir(exist_ok=True)
            
            # Programmes à inclure dans le dossier
            cleanup_programs = {
                "Malwarebytes": r"C:\Program Files\Malwarebytes\Anti-Malware\mbam.exe",
                "AdwCleaner": r"C:\Program Files\Malwarebytes\AdwCleaner\adwcleaner.exe",
                "Wise Disk Cleaner": r"C:\Program Files (x86)\Wise\Wise Disk Cleaner\WiseDiskCleaner.exe",
                "Spybot": r"C:\Program Files (x86)\Spybot - Search & Destroy 2\SDWelcome.exe"
            }
            
            # Télécharger les portables
            portable_downloads = Path(__file__).parent.parent / "downloads"
            anydesk_exe = portable_downloads / "AnyDesk.exe"
            rustdesk_exe = portable_downloads / "rustdesk.exe"
            
            # Copier les exécutables portables
            if anydesk_exe.exists():
                import shutil
                shutil.copy(anydesk_exe, cleanup_folder / "AnyDesk.exe")
            
            if rustdesk_exe.exists():
                import shutil
                shutil.copy(rustdesk_exe, cleanup_folder / "RustDesk.exe")
            
            # Créer les raccourcis
            shell = Dispatch('WScript.Shell')
            
            for prog_name, exe_path in cleanup_programs.items():
                if Path(exe_path).exists():
                    shortcut_path = cleanup_folder / f"{prog_name}.lnk"
                    shortcut = shell.CreateShortCut(str(shortcut_path))
                    shortcut.Targetpath = exe_path
                    shortcut.WorkingDirectory = str(Path(exe_path).parent)
                    shortcut.IconLocation = exe_path
                    shortcut.save()
            
            self.logger.info(f"✅ Dossier 'Outils de nettoyage' créé sur le bureau")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Impossible de créer le dossier Outils de nettoyage: {e}")
    
    def open_massgrave(self):
        """Ouvre le site MAS dans le navigateur"""
        import webbrowser
        webbrowser.open("https://massgrave.dev/")
        self.logger.info("🔐 Ouverture du site MAS (Microsoft Activation Scripts)")
    
    def activate_windows(self):
        """Lance la commande d'activation Windows en admin"""
        if messagebox.askyesno(
            "Activation Windows",
            "⚡ Cette commande va lancer le script d'activation Windows.\n\n"
            "Voulez-vous continuer ?\n\n"
            "Note: Un terminal PowerShell s'ouvrira avec les privilèges administrateur."
        ):
            try:
                import subprocess
                
                # Commande PowerShell à exécuter en admin
                command = 'irm https://get.activated.win | iex'
                
                # Lancer PowerShell en admin avec fenêtre visible - MÉTHODE CORRIGÉE
                ps_command = f'Start-Process powershell.exe -Verb RunAs -ArgumentList "-NoExit","-Command","irm https://get.activated.win | iex"'
                
                subprocess.Popen(
                    ['powershell.exe', '-Command', ps_command],
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
                
                self.logger.info("⚡ Commande d'activation Windows lancée")
                messagebox.showinfo(
                    "Activation lancée",
                    "✅ Le script d'activation a été lancé !\n\n"
                    "Suivez les instructions dans la fenêtre PowerShell."
                )
                
            except Exception as e:
                self.logger.error(f"❌ Erreur lors de l'activation: {e}")
                messagebox.showerror(
                    "Erreur",
                    f"❌ Impossible de lancer l'activation:\n{e}"
                )
    
    def create_tools_panel_in_container(self, parent):
        """Crée le panel d'outils à droite avec sections REDIMENSIONNABLES et RÉORGANISABLES"""
        tools_frame = ttk.LabelFrame(parent, text="🛠️ OUTILS WINDOWS - Glissez les titres pour réorganiser", padding=5)
        tools_frame.pack(fill="both", expand=True)
        
        # PanedWindow VERTICAL pour les sections redimensionnables
        self.tools_paned = ttk.PanedWindow(tools_frame, orient=tk.VERTICAL)
        self.tools_paned.pack(fill="both", expand=True)
        
        # Initialiser l'ordre des sections (peut être modifié par drag & drop)
        self.sections_order = ['reparation', 'activation', 'maintenance', 'diagnostics', 'reseau', 'winget', 'parametres', 'support']
        self.section_widgets = {}

        # Créer toutes les sections
        self.create_reparation_section()
        self.create_activation_section()
        self.create_maintenance_section()
        self.create_diagnostics_section()
        self.create_reseau_section()
        self.create_winget_section()
        self.create_parametres_section()
        self.create_support_section()
        
        # Ajouter les sections dans l'ordre initial
        for section_name in self.sections_order:
            if section_name in self.section_widgets:
                self.tools_paned.add(self.section_widgets[section_name])
    
    def create_reparation_section(self):
        """Crée la section Réparation Système - OPTIMISÉE"""
        section_frame = ttk.Frame(self.tools_paned)
        
        # En-tête avec drag handle
        header = self.create_draggable_header(section_frame, "🔧 RÉPARATION SYSTÈME", 'reparation')
        header.pack(fill="x", padx=2, pady=2)
        
        # Contenu avec hauteur fixe optimale (28 boutons en 4 colonnes = 7 lignes)
        content_frame = ttk.Frame(section_frame, height=180)
        content_frame.pack(fill="both", expand=True, padx=2)
        content_frame.pack_propagate(False)  # Empêche l'expansion automatique
        
        canvas = tk.Canvas(content_frame, bg=self.DARK_BG2, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)
        
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Boutons de réparation - EN 2 COLONNES
        dism_buttons = [
            ("🔍 DISM Vérifier", "DISM /Online /Cleanup-Image /CheckHealth"),
            ("🔎 DISM Scanner", "DISM /Online /Cleanup-Image /ScanHealth"),
            ("🔧 DISM Réparer", "DISM /Online /Cleanup-Image /RestoreHealth"),
            ("🧹 DISM Nettoyer", "DISM /Online /Cleanup-Image /StartComponentCleanup"),
            ("🧹+ DISM Nettoyer++", "DISM /Online /Cleanup-Image /StartComponentCleanup /ResetBase"),
            ("🛡️ SFC Scan", "sfc /scannow"),
            ("💿 ChkDsk C:", "chkdsk C: /F /R"),
            ("💾 ChkDsk Scan", "chkdsk C: /scan"),
            ("🔄 Réparer Boot", "bootrec /fixmbr & bootrec /fixboot & bootrec /rebuildbcd"),
            ("🧼 Nettoyer Store", "wsreset.exe"),
            ("🔥 Vider DNS", "ipconfig /flushdns"),
            ("🌐 Reset Winsock", "netsh winsock reset"),
            ("📡 Reset IP", "netsh int ip reset"),
            ("🔨 DISM+SFC Complet", "DISM /Online /Cleanup-Image /RestoreHealth & sfc /scannow"),
            ("⚙️ MSConfig", "msconfig"),
            ("ℹ️ WinVer", "winver"),
            ("🖥️ Propriétés Système", "sysdm.cpl"),
            ("📁 AppData", "explorer %appdata%"),
            ("🗑️ Temp", "explorer %temp%"),
            ("🌐 Programmes", "explorer shell:Programs"),
            ("🚀 Démarrage", "explorer shell:Startup"),
            ("💻 Système32", "explorer C:\\Windows\\System32"),
            ("🎛️ Gestionnaire périph.", "devmgmt.msc"),
            ("💾 Gestion disques", "diskmgmt.msc"),
            ("🔌 Services", "services.msc"),
            ("📋 Registre", "regedit"),
            ("🖨️ Imprimantes", "control printers")
        ]
        
        # Configuration 6 colonnes pour maximiser l'espace horizontal
        for i in range(6):
            scrollable.grid_columnconfigure(i, weight=1)

        for idx, (label, cmd) in enumerate(dism_buttons):
            row = idx // 6  # Division par 6 pour 6 colonnes
            col = idx % 6   # Modulo 6 pour alterner entre colonnes 0-5
            ttk.Button(
                scrollable,
                text=label,
                command=lambda c=cmd: self.execute_quick_command(c, True)
            ).grid(row=row, column=col, pady=1, padx=1, sticky="ew")
        
        self.section_widgets['reparation'] = section_frame
    
    def create_activation_section(self):
        """Crée la section Activation - TOUS LES BOUTONS SUR UNE LIGNE"""
        section_frame = ttk.Frame(self.tools_paned)

        # En-tête avec drag handle
        header = self.create_draggable_header(section_frame, "🔑 ACTIVATION & TÉLÉCHARGEMENTS", 'activation')
        header.pack(fill="x", padx=2, pady=2)

        # Contenu - UNE SEULE LIGNE
        content_frame = ttk.Frame(section_frame)
        content_frame.pack(fill="x", padx=2, pady=3)

        # Grid 1 ligne x 5 colonnes - tous les boutons sur une ligne
        button_container = ttk.Frame(content_frame)
        button_container.pack(fill="x")

        # Configuration de 5 colonnes avec weight égal
        for i in range(5):
            button_container.grid_columnconfigure(i, weight=1)

        ttk.Button(button_container, text="🔐 MAS", command=self.open_massgrave).grid(row=0, column=0, padx=1, pady=2, sticky="ew")
        ttk.Button(button_container, text="⚡ Win", command=self.activate_windows).grid(row=0, column=1, padx=1, pady=2, sticky="ew")
        ttk.Button(button_container, text="📦 Office FR", command=lambda: self.open_manufacturer_support("https://gravesoft.dev/office_c2r_links#french-fr-fr")).grid(row=0, column=2, padx=1, pady=2, sticky="ew")
        ttk.Button(button_container, text="🌊 YGG", command=lambda: self.open_manufacturer_support("https://www.yggtorrent.top/auth/login")).grid(row=0, column=3, padx=1, pady=2, sticky="ew")
        ttk.Button(button_container, text="💾 BDD Portables", command=self.show_portable_database_stats).grid(row=0, column=4, padx=1, pady=2, sticky="ew")

        self.section_widgets['activation'] = section_frame

    def create_maintenance_section(self):
        """Crée la section Maintenance & Nettoyage"""
        section_frame = ttk.Frame(self.tools_paned)

        # En-tête avec drag handle
        header = self.create_draggable_header(section_frame, "🧹 MAINTENANCE & NETTOYAGE", 'maintenance')
        header.pack(fill="x", padx=2, pady=2)

        # Contenu avec hauteur fixe optimale (16 boutons en 4 colonnes = 4 lignes)
        content_frame = ttk.Frame(section_frame, height=120)
        content_frame.pack(fill="both", expand=True, padx=2)
        content_frame.pack_propagate(False)

        canvas = tk.Canvas(content_frame, bg=self.DARK_BG2, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)

        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        maintenance_buttons = [
            ("🗑️ Vider Corbeille", "PowerShell -Command \"Clear-RecycleBin -Force\""),
            ("🧹 Nettoyer Temp", "cleanmgr /sageset:1 & cleanmgr /sagerun:1"),
            ("📦 Disk Cleanup", "cleanmgr"),
            ("🗂️ Nettoyer WinSxS", "DISM /Online /Cleanup-Image /StartComponentCleanup"),
            ("🔄 Défragmenter C:", "defrag C: /O"),
            ("📊 Analyser Défrag", "dfrgui"),
            ("⚡ Gestionnaire Tâches", "taskmgr"),
            ("📈 Moniteur Ressources", "resmon"),
            ("💾 Nettoyage Disque", "cleanmgr /sagerun:1"),
            ("🗃️ Analyse Espace", "explorer C:\\"),
            ("🧹 Nettoyer Préfetch", "del /q /f C:\\Windows\\Prefetch\\*"),
            ("🗑️ Vider %TEMP%", "del /q /f %temp%\\* & rd /s /q %temp%"),
            ("📥 Nettoyer Downloads", "explorer %USERPROFILE%\\Downloads"),
            ("🗂️ Gestionnaire Stockage", "start ms-settings:storagesense"),
            ("🧼 Optimiser Disques", "dfrgui"),
            ("🔌 Désinstaller Apps", "appwiz.cpl")
        ]

        # Configuration 6 colonnes
        for i in range(6):
            scrollable.grid_columnconfigure(i, weight=1)

        for idx, (label, cmd) in enumerate(maintenance_buttons):
            row = idx // 6
            col = idx % 6
            ttk.Button(
                scrollable,
                text=label,
                command=lambda c=cmd: self.execute_quick_command(c, True)
            ).grid(row=row, column=col, pady=1, padx=1, sticky="ew")

        self.section_widgets['maintenance'] = section_frame

    def create_diagnostics_section(self):
        """Crée la section Diagnostics & Infos Système"""
        section_frame = ttk.Frame(self.tools_paned)

        # En-tête avec drag handle
        header = self.create_draggable_header(section_frame, "🔍 DIAGNOSTICS & INFOS", 'diagnostics')
        header.pack(fill="x", padx=2, pady=2)

        # Contenu avec hauteur fixe optimale (16 boutons en 4 colonnes = 4 lignes)
        content_frame = ttk.Frame(section_frame, height=120)
        content_frame.pack(fill="both", expand=True, padx=2)
        content_frame.pack_propagate(False)

        canvas = tk.Canvas(content_frame, bg=self.DARK_BG2, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)

        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        diagnostics_buttons = [
            ("💻 Infos Système", "msinfo32"),
            ("🎮 DirectX Diagnostic", "dxdiag"),
            ("📊 Observateur Événements", "eventvwr.msc"),
            ("📈 Moniteur Performances", "perfmon"),
            ("💾 Gestion Disques", "diskmgmt.msc"),
            ("🔧 Analyseur Fiabilité", "perfmon /rel"),
            ("🖥️ Propriétés Système", "sysdm.cpl"),
            ("ℹ️ Version Windows", "winver"),
            ("🔌 Gestionnaire Périph.", "devmgmt.msc"),
            ("🔋 Rapport Batterie", "powercfg /batteryreport"),
            ("⚡ Rapport Énergie", "powercfg /energy"),
            ("📡 Config Réseau", "ncpa.cpl"),
            ("🌡️ Temp Processeur", "wmic cpu get temperature"),
            ("💻 Config Matérielle", "msinfo32 /categories +ComponentsSummary"),
            ("🔍 Rapport Intégrité", "DISM /Online /Cleanup-Image /CheckHealth"),
            ("🧪 Test Mémoire", "MdSched.exe")
        ]

        # Configuration 6 colonnes
        for i in range(6):
            scrollable.grid_columnconfigure(i, weight=1)

        for idx, (label, cmd) in enumerate(diagnostics_buttons):
            row = idx // 6
            col = idx % 6
            ttk.Button(
                scrollable,
                text=label,
                command=lambda c=cmd: self.execute_quick_command(c, True)
            ).grid(row=row, column=col, pady=1, padx=1, sticky="ew")

        self.section_widgets['diagnostics'] = section_frame

    def create_reseau_section(self):
        """Crée la section Réseau & Internet"""
        section_frame = ttk.Frame(self.tools_paned)

        # En-tête avec drag handle
        header = self.create_draggable_header(section_frame, "🌐 RÉSEAU & INTERNET", 'reseau')
        header.pack(fill="x", padx=2, pady=2)

        # Contenu avec hauteur fixe optimale (16 boutons en 4 colonnes = 4 lignes)
        content_frame = ttk.Frame(section_frame, height=120)
        content_frame.pack(fill="both", expand=True, padx=2)
        content_frame.pack_propagate(False)

        canvas = tk.Canvas(content_frame, bg=self.DARK_BG2, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)

        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        reseau_buttons = [
            ("🌐 Ping Google", "ping 8.8.8.8 -n 10"),
            ("🔍 Test DNS", "nslookup google.com"),
            ("📡 Afficher IP", "ipconfig /all"),
            ("🗺️ Traceroute", "tracert google.com"),
            ("📊 Netstat", "netstat -ano"),
            ("🔥 Vider DNS", "ipconfig /flushdns"),
            ("🌐 Reset Winsock", "netsh winsock reset"),
            ("📡 Reset IP", "netsh int ip reset"),
            ("🔌 Renouveler IP", "ipconfig /release & ipconfig /renew"),
            ("🛡️ Pare-feu", "firewall.cpl"),
            ("🌐 Config Réseau", "ncpa.cpl"),
            ("📈 Moniteur Réseau", "resmon"),
            ("🔍 Test Latence", "ping 8.8.8.8 -t"),
            ("🌍 Test Speed", "start https://fast.com"),
            ("📡 WiFi Info", "netsh wlan show interfaces"),
            ("🔐 Proxy Settings", "start ms-settings:network-proxy")
        ]

        # Configuration 6 colonnes
        for i in range(6):
            scrollable.grid_columnconfigure(i, weight=1)

        for idx, (label, cmd) in enumerate(reseau_buttons):
            row = idx // 6
            col = idx % 6
            ttk.Button(
                scrollable,
                text=label,
                command=lambda c=cmd: self.execute_quick_command(c, True)
            ).grid(row=row, column=col, pady=1, padx=1, sticky="ew")

        self.section_widgets['reseau'] = section_frame

    def create_winget_section(self):
        """Crée la section Winget - Mises à jour"""
        section_frame = ttk.Frame(self.tools_paned)

        # En-tête avec drag handle
        header = self.create_draggable_header(section_frame, "🔄 WINGET - MISES À JOUR", 'winget')
        header.pack(fill="x", padx=2, pady=2)

        # Contenu avec hauteur fixe optimale (12 boutons en 4 colonnes = 3 lignes)
        content_frame = ttk.Frame(section_frame, height=100)
        content_frame.pack(fill="both", expand=True, padx=2)
        content_frame.pack_propagate(False)
        
        canvas = tk.Canvas(content_frame, bg=self.DARK_BG2, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)
        
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Boutons Winget - EN 4 COLONNES
        winget_buttons = [
            ("🔄 MAJ Tout", "winget upgrade --all"),
            ("📋 Liste MAJ", "winget upgrade"),
            ("🔍 Recherche", "winget search"),
            ("📦 Liste installés", "winget list"),
            ("⚙️ Winget Info", "winget --info"),
            ("🧹 Nettoyer cache", "winget source reset --force"),
            ("📥 MAJ Chrome", "winget upgrade Google.Chrome"),
            ("🦊 MAJ Firefox", "winget upgrade Mozilla.Firefox"),
            ("📝 MAJ VSCode", "winget upgrade Microsoft.VisualStudioCode"),
            ("💬 MAJ Discord", "winget upgrade Discord.Discord"),
            ("🎮 MAJ Steam", "winget upgrade Valve.Steam"),
            ("🎵 MAJ Spotify", "winget upgrade Spotify.Spotify")
        ]
        
        # Configuration 6 colonnes
        for i in range(6):
            scrollable.grid_columnconfigure(i, weight=1)

        for idx, (label, cmd) in enumerate(winget_buttons):
            row = idx // 6
            col = idx % 6
            ttk.Button(
                scrollable,
                text=label,
                command=lambda c=cmd: self.execute_quick_command(c, True)
            ).grid(row=row, column=col, pady=1, padx=1, sticky="ew")
        
        self.section_widgets['winget'] = section_frame
    
    def create_parametres_section(self):
        """Crée la section Paramètres - OPTIMISÉE"""
        section_frame = ttk.Frame(self.tools_paned)

        # En-tête avec drag handle
        header = self.create_draggable_header(section_frame, "⚙️ PARAMÈTRES WINDOWS", 'parametres')
        header.pack(fill="x", padx=2, pady=2)

        # Contenu avec hauteur fixe optimale (13 boutons en 4 colonnes = 4 lignes)
        content_frame = ttk.Frame(section_frame, height=120)
        content_frame.pack(fill="both", expand=True, padx=2)
        content_frame.pack_propagate(False)
        
        canvas = tk.Canvas(content_frame, bg=self.DARK_BG2, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)
        
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        params_buttons = [
            ("⚙️ Paramètres", "start ms-settings:"),
            ("🌐 Réseau", "start ms-settings:network"),
            ("📡 Bluetooth", "start ms-settings:bluetooth"),
            ("🖨️ Imprimantes", "start ms-settings:printers"),
            ("🔊 Son", "start ms-settings:sound"),
            ("⌨️ Clavier", "start ms-settings:keyboard"),
            ("🔑 Activation", "start ms-settings:activation"),
            ("🔄 Update", "start ms-settings:windowsupdate"),
            ("📱 Périphériques", "start ms-settings:connecteddevices"),
            ("🎛️ Panneau", "control"),
            ("📦 Programmes", "appwiz.cpl"),
            ("⚙️ Services", "services.msc"),
            ("📝 Registre", "regedit")
        ]
        
        # Configuration 6 colonnes
        for i in range(6):
            scrollable.grid_columnconfigure(i, weight=1)

        for idx, (label, cmd) in enumerate(params_buttons):
            row = idx // 6
            col = idx % 6
            ttk.Button(
                scrollable,
                text=label,
                command=lambda c=cmd: self.execute_quick_command(c, False)
            ).grid(row=row, column=col, pady=1, padx=1, sticky="ew")
        
        self.section_widgets['parametres'] = section_frame
    
    def create_support_section(self):
        """Crée la section Support Fabricants - OPTIMISÉE"""
        section_frame = ttk.Frame(self.tools_paned)

        # En-tête avec drag handle
        header = self.create_draggable_header(section_frame, "🏢 SUPPORT & DRIVERS", 'support')
        header.pack(fill="x", padx=2, pady=2)

        # Contenu avec hauteur fixe optimale (12 boutons en 4 colonnes = 3 lignes)
        content_frame = ttk.Frame(section_frame, height=100)
        content_frame.pack(fill="both", expand=True, padx=2)
        content_frame.pack_propagate(False)
        
        canvas = tk.Canvas(content_frame, bg=self.DARK_BG2, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)
        
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        support_buttons = [
            ("💻 Lenovo Vantage", "https://support.lenovo.com/fr/fr/solutions/ht505081"),
            ("🖨️ HP Support", "https://support.hp.com/fr-fr/help/hp-support-assistant"),
            ("💻 Dell SupportAssist", "https://www.dell.com/support/home/fr-fr/product-support/product/supportassist-for-home-pcs/download"),
            ("🎮 MSI Center", "https://fr.msi.com/Landing/MSI-Center"),
            ("⚡ ASUS Support", "https://www.asus.com/fr/support/download-center/"),
            ("🖥️ Acer Support", "https://www.acer.com/fr-fr/support"),
            ("💾 Intel DSA", "https://www.intel.fr/content/www/fr/fr/support/detect.html"),
            ("🎮 AMD Software", "https://www.amd.com/fr/support"),
            ("🖥️ NVIDIA GeForce", "https://www.nvidia.com/fr-fr/geforce/geforce-experience/"),
            ("📱 Samsung Magician", "https://www.samsung.com/fr/support/computing/samsung-magician/"),
            ("🔌 Logitech G HUB", "https://www.logitechg.com/fr-fr/innovation/g-hub.html"),
            ("🖱️ Razer Synapse", "https://www.razer.com/fr-fr/synapse-3")
        ]
        
        # Configuration 6 colonnes
        for i in range(6):
            scrollable.grid_columnconfigure(i, weight=1)

        for idx, (label, url) in enumerate(support_buttons):
            row = idx // 6
            col = idx % 6
            ttk.Button(
                scrollable,
                text=label,
                command=lambda u=url: self.open_manufacturer_support(u)
            ).grid(row=row, column=col, pady=1, padx=1, sticky="ew")
        
        self.section_widgets['support'] = section_frame
    
    def create_draggable_header(self, parent, title, section_name):
        """Crée un en-tête draggable pour réorganiser les sections"""
        header = tk.Frame(parent, bg=self.ACCENT_BLUE, cursor="hand2", height=30)  # Bleu foncé Ordi Plus
        
        label = tk.Label(
            header, 
            text=f"⋮⋮ {title}",
            bg=self.ACCENT_BLUE,  # Bleu foncé Ordi Plus
            fg="white",
            font=('Segoe UI', 9, 'bold'),
            pady=5
        )
        label.pack(fill="both", expand=True)
        
        # Bind drag events
        header.bind("<Button-1>", lambda e: self.start_drag(e, section_name))
        header.bind("<B1-Motion>", lambda e: self.on_drag(e, section_name))
        header.bind("<ButtonRelease-1>", lambda e: self.end_drag(e, section_name))
        
        label.bind("<Button-1>", lambda e: self.start_drag(e, section_name))
        label.bind("<B1-Motion>", lambda e: self.on_drag(e, section_name))
        label.bind("<ButtonRelease-1>", lambda e: self.end_drag(e, section_name))
        
        return header
    
    def start_drag(self, event, section_name):
        """Début du drag d'une section"""
        self.drag_data = {
            'section': section_name,
            'start_y': event.y_root,
            'original_index': self.sections_order.index(section_name)
        }
    
    def on_drag(self, event, section_name):
        """Pendant le drag"""
        if hasattr(self, 'drag_data'):
            delta_y = event.y_root - self.drag_data['start_y']
            # Visuel du drag (optionnel)
            pass
    
    def end_drag(self, event, section_name):
        """Fin du drag - réorganise les sections"""
        if not hasattr(self, 'drag_data'):
            return
        
        delta_y = event.y_root - self.drag_data['start_y']
        original_index = self.drag_data['original_index']
        
        # Calculer le nouvel index basé sur le déplacement
        # Chaque section fait environ 200px
        sections_moved = round(delta_y / 200)
        new_index = max(0, min(len(self.sections_order) - 1, original_index + sections_moved))
        
        if new_index != original_index:
            # Réorganiser l'ordre
            self.sections_order.pop(original_index)
            self.sections_order.insert(new_index, section_name)
            
            # Reconstruire le PanedWindow
            self.rebuild_tools_panel()
        
        del self.drag_data
    
    def rebuild_tools_panel(self):
        """Reconstruit le panneau d'outils avec le nouvel ordre"""
        # Retirer toutes les sections
        for child in self.tools_paned.panes():
            self.tools_paned.forget(child)
        
        # Réajouter dans le nouvel ordre
        for section_name in self.sections_order:
            if section_name in self.section_widgets:
                self.tools_paned.add(self.section_widgets[section_name])
    
    def open_manufacturer_support(self, url):
        """Ouvre le lien de support du fabricant dans le navigateur"""
        import webbrowser
        try:
            webbrowser.open(url)
            self.logger.info(f"✅ Ouverture du support fabricant: {url}")
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'ouverture du lien: {e}")
            messagebox.showerror(
                "Erreur",
                f"❌ Impossible d'ouvrir le lien:\n{e}"
            )
    
    def open_download_link(self, url):
        """Ouvre le lien de téléchargement dans le navigateur"""
        import webbrowser
        try:
            if url:
                webbrowser.open(url)
                self.logger.info(f"✅ Ouverture du lien de téléchargement: {url}")
                messagebox.showinfo(
                    "Téléchargement",
                    "Le lien de téléchargement a été ouvert dans votre navigateur.\n\n"
                    "Téléchargez l'outil et exécutez-le pour désinstaller proprement l'antivirus."
                )
            else:
                messagebox.showerror(
                    "Erreur",
                    "Aucun lien de téléchargement disponible pour cet outil."
                )
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'ouverture du lien: {e}")
            messagebox.showerror(
                "Erreur",
                f"❌ Impossible d'ouvrir le lien:\n{e}"
            )
    
    def execute_quick_command(self, command, admin_required=False):
        """Exécute une commande Windows rapidement (boutons d'accès rapide)"""
        import subprocess
        
        try:
            if admin_required:
                # Confirmation pour les commandes admin
                if not messagebox.askyesno(
                    "Droits administrateur requis",
                    f"Cette commande nécessite les droits administrateur:\n\n{command}\n\n"
                    "Voulez-vous continuer ?"
                ):
                    return
                
                # Exécuter en mode administrateur avec PowerShell - FENÊTRE VISIBLE
                ps_command = f'Start-Process cmd.exe -ArgumentList "/k {command}" -Verb RunAs'
                subprocess.Popen(
                    ["powershell.exe", "-Command", ps_command],
                    shell=True
                )
                self.logger.info(f"✅ Commande admin exécutée: {command}")
                
            else:
                # Exécuter normalement - FENÊTRE VISIBLE
                subprocess.Popen(
                    ["cmd.exe", "/k", command],
                    shell=True
                )
                self.logger.info(f"✅ Commande exécutée: {command}")
                
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'exécution de la commande: {e}")
            messagebox.showerror(
                "Erreur",
                f"❌ Impossible d'exécuter la commande:\n{e}"
            )
    
    def open_organize_dialog(self):
        """Ouvre le dialogue d'organisation des programmes avec drag & drop"""
        dialog = tk.Toplevel(self.root)
        dialog.title("🔄 Organiser les programmes")
        dialog.geometry("900x700")
        dialog.configure(bg=self.DARK_BG)
        
        # Centrer la fenêtre
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Titre
        title_label = ttk.Label(
            main_frame,
            text="🔄 Organiser les programmes - Glissez-déposez entre les catégories",
            style='Title.TLabel'
        )
        title_label.pack(pady=(0, 10))
        
        # Frame pour les deux listes côte à côte
        lists_frame = ttk.Frame(main_frame)
        lists_frame.pack(fill="both", expand=True)
        lists_frame.grid_columnconfigure(0, weight=1)
        lists_frame.grid_columnconfigure(1, weight=1)
        
        # Variables pour le drag & drop
        self.drag_data = {"source_cat": None, "program_name": None}
        
        # Frame gauche - Catégories et programmes
        left_frame = ttk.LabelFrame(lists_frame, text="📁 Catégories et Programmes", padding=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Sélecteur de catégorie
        cat_select_frame = ttk.Frame(left_frame)
        cat_select_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(cat_select_frame, text="Catégorie:").pack(side="left", padx=(0, 10))
        
        category_var = tk.StringVar()
        categories = sorted(self.programs.keys())
        category_combo = ttk.Combobox(cat_select_frame, textvariable=category_var, values=categories, state='readonly', width=30)
        category_combo.pack(side="left", fill="x", expand=True)
        
        # Liste des programmes de la catégorie sélectionnée
        programs_list = tk.Listbox(left_frame, bg=self.DARK_BG2, fg=self.DARK_FG, height=25, selectmode=tk.SINGLE)
        programs_list.pack(fill="both", expand=True)
        
        # Scrollbar pour la liste
        scrollbar_left = ttk.Scrollbar(left_frame, orient="vertical", command=programs_list.yview)
        scrollbar_left.pack(side="right", fill="y")
        programs_list.config(yscrollcommand=scrollbar_left.set)
        
        # Frame droit - Destination
        right_frame = ttk.LabelFrame(lists_frame, text="🎯 Déplacer vers la catégorie", padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Sélecteur de catégorie destination
        dest_cat_frame = ttk.Frame(right_frame)
        dest_cat_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(dest_cat_frame, text="Catégorie destination:").pack(side="left", padx=(0, 10))
        
        dest_category_var = tk.StringVar()
        dest_category_combo = ttk.Combobox(dest_cat_frame, textvariable=dest_category_var, values=categories, state='readonly', width=30)
        dest_category_combo.pack(side="left", fill="x", expand=True)
        
        # Zone d'information
        info_text = scrolledtext.ScrolledText(right_frame, bg=self.DARK_BG2, fg=self.DARK_FG, height=25, wrap=tk.WORD)
        info_text.pack(fill="both", expand=True)
        info_text.insert("1.0", "👆 Sélectionnez un programme à gauche\n📂 Choisissez une catégorie de destination\n✅ Cliquez sur 'Déplacer' pour transférer")
        info_text.config(state='disabled')
        
        # Fonction pour charger les programmes d'une catégorie
        def load_programs(event=None):
            programs_list.delete(0, tk.END)
            cat = category_var.get()
            if cat and cat in self.programs:
                for prog_name in sorted(self.programs[cat].keys()):
                    programs_list.insert(tk.END, prog_name)
        
        category_combo.bind("<<ComboboxSelected>>", load_programs)
        
        # Charger la première catégorie par défaut
        if categories:
            category_combo.current(0)
            load_programs()
        
        # Fonction de déplacement
        def move_program():
            selection = programs_list.curselection()
            if not selection:
                messagebox.showwarning("Sélection requise", "Veuillez sélectionner un programme à déplacer.")
                return
            
            source_cat = category_var.get()
            dest_cat = dest_category_var.get()
            program_name = programs_list.get(selection[0])
            
            if not dest_cat:
                messagebox.showwarning("Destination requise", "Veuillez sélectionner une catégorie de destination.")
                return
            
            if source_cat == dest_cat:
                messagebox.showinfo("Même catégorie", "Le programme est déjà dans cette catégorie.")
                return
            
            # Confirmation
            if not messagebox.askyesno("Confirmer", f"Déplacer '{program_name}'\nDe: {source_cat}\nVers: {dest_cat}\n\nContinuer?"):
                return
            
            try:
                # Charger programs.json
                import sys
                if getattr(sys, 'frozen', False):
                    base_path = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else Path(sys.executable).parent
                else:
                    base_path = Path(__file__).parent.parent
                
                programs_file = base_path / 'data' / 'programs.json'
                with open(programs_file, 'r', encoding='utf-8') as f:
                    all_programs = json.load(f)
                
                # Déplacer le programme
                program_data = all_programs[source_cat].pop(program_name)
                
                if dest_cat not in all_programs:
                    all_programs[dest_cat] = {}
                
                all_programs[dest_cat][program_name] = program_data
                
                # Sauvegarder
                with open(programs_file, 'w', encoding='utf-8') as f:
                    json.dump(all_programs, f, indent=4, ensure_ascii=False)
                
                # Mettre à jour l'affichage
                self.programs = all_programs
                load_programs()
                
                messagebox.showinfo("Succès", f"✅ '{program_name}' déplacé vers '{dest_cat}'!\n\nRedémarrez l'application pour voir les changements.")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"❌ Erreur lors du déplacement:\n{e}")
        
        # Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text="➡️ Déplacer", command=move_program, style='Action.TButton').pack(side="left", padx=5)
        ttk.Button(button_frame, text="🔄 Rafraîchir", command=load_programs).pack(side="left", padx=5)
        ttk.Button(button_frame, text="❌ Fermer", command=dialog.destroy).pack(side="right", padx=5)
    
    def add_custom_program(self):
        """Permet d'ajouter un programme personnalisé via URL de téléchargement"""
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Ajouter un programme personnalisé")
        dialog.geometry("600x400")
        dialog.configure(bg=self.DARK_BG)
        dialog.resizable(False, False)
        
        # Centrer la fenêtre
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Titre
        title_label = ttk.Label(
            main_frame,
            text="➕ Ajouter un nouveau programme",
            style='Title.TLabel'
        )
        title_label.pack(pady=(0, 20))
        
        # Nom du programme
        ttk.Label(main_frame, text="📝 Nom du programme:").pack(anchor="w", pady=(0, 5))
        name_entry = ttk.Entry(main_frame, width=60)
        name_entry.pack(fill="x", pady=(0, 15))
        
        # URL de téléchargement
        ttk.Label(main_frame, text="🔗 URL de téléchargement (.exe, .msi):").pack(anchor="w", pady=(0, 5))
        url_entry = ttk.Entry(main_frame, width=60)
        url_entry.pack(fill="x", pady=(0, 15))
        
        # Catégorie
        ttk.Label(main_frame, text="📁 Catégorie:").pack(anchor="w", pady=(0, 5))
        category_var = tk.StringVar(value="Utilitaires")
        categories = sorted(self.programs.keys())
        category_combo = ttk.Combobox(main_frame, textvariable=category_var, values=categories, width=57, state='readonly')
        category_combo.pack(fill="x", pady=(0, 15))
        
        # Description
        ttk.Label(main_frame, text="📄 Description (optionnelle):").pack(anchor="w", pady=(0, 5))
        desc_entry = ttk.Entry(main_frame, width=60)
        desc_entry.pack(fill="x", pady=(0, 20))
        
        # Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        def save_program():
            name = name_entry.get().strip()
            url = url_entry.get().strip()
            category = category_var.get()
            description = desc_entry.get().strip() or name
            
            if not name or not url:
                messagebox.showwarning("Champs manquants", "Veuillez remplir le nom et l'URL du programme.")
                return
            
            if not url.startswith(('http://', 'https://')):
                messagebox.showwarning("URL invalide", "L'URL doit commencer par http:// ou https://")
                return
            
            # Ajouter le programme à programs.json
            try:
                import sys
                if getattr(sys, 'frozen', False):
                    base_path = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else Path(sys.executable).parent
                else:
                    base_path = Path(__file__).parent.parent
                
                programs_file = base_path / 'data' / 'programs.json'
                with open(programs_file, 'r', encoding='utf-8') as f:
                    all_programs = json.load(f)
                
                # Créer l'entrée du programme
                program_entry = {
                    "name": name,
                    "description": description,
                    "url": url,
                    "installer_type": "direct",
                    "silent_args": "/S",
                    "essential": False
                }
                
                # Ajouter à la catégorie
                if category not in all_programs:
                    all_programs[category] = {}
                
                all_programs[category][name] = program_entry
                
                # Sauvegarder
                with open(programs_file, 'w', encoding='utf-8') as f:
                    json.dump(all_programs, f, indent=4, ensure_ascii=False)
                
                messagebox.showinfo("Succès", f"✅ Programme '{name}' ajouté avec succès!\n\nRedémarrez l'application pour voir les changements.")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Erreur", f"❌ Erreur lors de l'ajout:\n{e}")
        
        ttk.Button(button_frame, text="✅ Ajouter", command=save_program, style='Action.TButton').pack(side="left", padx=5)
        ttk.Button(button_frame, text="❌ Annuler", command=dialog.destroy).pack(side="left", padx=5)
    
    def on_closing(self):
        """Fermeture propre de l'application"""
        import sys
        import gc
        
        try:
            # Arrêter toute installation en cours
            if self.is_installing:
                if not messagebox.askyesno(
                    "Installation en cours",
                    "Une installation est en cours. Voulez-vous vraiment quitter ?"
                ):
                    return
            
            # Fermer tous les logs
            logging.shutdown()
            
            # Nettoyer les références
            self.program_vars.clear()
            self.programs.clear()
            self.category_frames.clear()
            self.category_widgets.clear()
            
            # Forcer le garbage collector
            gc.collect()
            
            # Détruire la fenêtre
            self.root.quit()
            self.root.destroy()
            
            # Forcer la sortie
            sys.exit(0)
            
        except Exception as e:
            print(f"Erreur lors de la fermeture: {e}")
            sys.exit(0)

    # ===============================================
    # MÉTHODES BASE DE DONNÉES PORTABLE
    # ===============================================
    
    def show_portable_database_stats(self):
        """Affiche les statistiques de la base de données portable"""
        from tkinter import messagebox, scrolledtext
        import tkinter as tk
        from tkinter import ttk
        
        if not self.installer_manager or not hasattr(self.installer_manager, 'portable_db') or not self.installer_manager.portable_db:
            messagebox.showinfo(
                "Base de données portable",
                "💾 La base de données portable n'est pas disponible.\n\n"
                "Elle sera créée automatiquement lors de l'installation d'applications portables."
            )
            return
        
        try:
            db = self.installer_manager.portable_db
            stats = db.get_statistics()
            categories = db.get_categories()
            
            # Créer une fenêtre de dialogue
            dialog = tk.Toplevel(self.root)
            dialog.title("💾 Base de Données Portable - Statistiques")
            dialog.geometry("700x600")
            dialog.configure(bg=self.DARK_BG)
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Frame principal
            main_frame = ttk.Frame(dialog)
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Titre
            title_label = tk.Label(
                main_frame,
                text="📊 STATISTIQUES BASE DE DONNÉES PORTABLE",
                font=('Segoe UI', 16, 'bold'),
                bg=self.DARK_BG,
                fg=self.ACCENT_ORANGE
            )
            title_label.pack(pady=(0, 20))
            
            # Frame pour les statistiques
            stats_frame = ttk.LabelFrame(main_frame, text=" 📈 Statistiques globales ", padding=15)
            stats_frame.pack(fill="x", pady=10)
            
            # Statistiques générales
            stats_text = f"""
📦 Applications totales : {stats.get('total_apps', 0)}
✅ Applications portables : {stats.get('portable_apps', 0)}
💿 Applications installées : {stats.get('installed_apps', 0)}
📁 Catégories : {len(categories)}

💾 ESPACE UTILISÉ :
   • Total : {stats.get('total_size_gb', 0):.2f} GB
   • Détails : {stats.get('total_size_mb', 0):.2f} MB
   • Octets : {stats.get('total_size_bytes', 0):,}
"""
            
            stats_label = tk.Label(
                stats_frame,
                text=stats_text,
                font=('Consolas', 10),
                bg=self.DARK_BG2,
                fg=self.DARK_FG,
                justify="left",
                anchor="w"
            )
            stats_label.pack(fill="x")
            
            # Frame pour les catégories
            cat_frame = ttk.LabelFrame(main_frame, text=" 📁 Applications par catégorie ", padding=15)
            cat_frame.pack(fill="both", expand=True, pady=10)
            
            # Créer un canvas avec scrollbar pour les catégories
            cat_canvas = tk.Canvas(cat_frame, bg=self.DARK_BG2, height=200)
            cat_scrollbar = ttk.Scrollbar(cat_frame, orient="vertical", command=cat_canvas.yview)
            cat_scrollable = ttk.Frame(cat_canvas)
            
            cat_scrollable.bind(
                "<Configure>",
                lambda e: cat_canvas.configure(scrollregion=cat_canvas.bbox("all"))
            )
            
            cat_canvas.create_window((0, 0), window=cat_scrollable, anchor="nw")
            cat_canvas.configure(yscrollcommand=cat_scrollbar.set)
            
            cat_canvas.pack(side="left", fill="both", expand=True)
            cat_scrollbar.pack(side="right", fill="y")
            
            # Afficher les catégories
            apps_by_cat = stats.get('apps_by_category', {})
            if apps_by_cat:
                for idx, (category, count) in enumerate(sorted(apps_by_cat.items(), key=lambda x: x[1], reverse=True)):
                    cat_label = tk.Label(
                        cat_scrollable,
                        text=f"  • {category}: {count} app(s)",
                        font=('Consolas', 9),
                        bg=self.DARK_BG2,
                        fg=self.DARK_FG2,
                        anchor="w"
                    )
                    cat_label.pack(fill="x", pady=2)
            else:
                no_cat_label = tk.Label(
                    cat_scrollable,
                    text="Aucune catégorie pour le moment",
                    font=('Consolas', 9),
                    bg=self.DARK_BG2,
                    fg=self.ACCENT_YELLOW,
                    anchor="w"
                )
                no_cat_label.pack(fill="x", pady=2)
            
            # Boutons d'action
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill="x", pady=(20, 0))
            
            ttk.Button(
                button_frame,
                text="🔍 Voir toutes les apps",
                command=lambda: self.show_all_portable_apps(dialog),
                style='Action.TButton'
            ).pack(side="left", padx=5)
            
            ttk.Button(
                button_frame,
                text="🔐 Vérifier intégrité",
                command=lambda: self.verify_database_integrity(dialog)
            ).pack(side="left", padx=5)
            
            ttk.Button(
                button_frame,
                text="📤 Exporter JSON",
                command=lambda: self.export_database_json(dialog)
            ).pack(side="left", padx=5)
            
            ttk.Button(
                button_frame,
                text="❌ Fermer",
                command=dialog.destroy
            ).pack(side="right", padx=5)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'affichage des statistiques: {e}")
            messagebox.showerror(
                "Erreur",
                f"❌ Impossible d'afficher les statistiques:\n\n{e}"
            )

    def show_all_portable_apps(self, parent_dialog=None):
        """Affiche toutes les applications portables de la base de données"""
        from tkinter import scrolledtext
        import tkinter as tk
        from tkinter import ttk
        
        if not self.installer_manager or not self.installer_manager.portable_db:
            return
        
        try:
            db = self.installer_manager.portable_db
            apps = db.list_applications(portable_only=True)
            
            # Créer une fenêtre
            dialog = tk.Toplevel(parent_dialog or self.root)
            dialog.title(f"📦 Applications Portables ({len(apps)})")
            dialog.geometry("900x600")
            dialog.configure(bg=self.DARK_BG)
            
            # Frame principal
            main_frame = ttk.Frame(dialog)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Titre
            title_label = tk.Label(
                main_frame,
                text=f"📦 {len(apps)} APPLICATIONS PORTABLES",
                font=('Segoe UI', 14, 'bold'),
                bg=self.DARK_BG,
                fg=self.ACCENT_GREEN
            )
            title_label.pack(pady=(0, 10))
            
            # Zone de texte avec scrollbar
            text_frame = ttk.Frame(main_frame)
            text_frame.pack(fill="both", expand=True)
            
            text_widget = scrolledtext.ScrolledText(
                text_frame,
                font=('Consolas', 9),
                bg=self.DARK_BG2,
                fg=self.DARK_FG,
                wrap="word"
            )
            text_widget.pack(fill="both", expand=True)
            
            # Afficher les applications
            for app in apps:
                text_widget.insert("end", f"📦 {app['name']}\n", "app_name")
                text_widget.insert("end", f"   Catégorie: {app.get('category', 'N/A')}\n")
                text_widget.insert("end", f"   Description: {app.get('description', 'N/A')}\n")
                text_widget.insert("end", f"   Version: {app.get('version', 'N/A')}\n")
                text_widget.insert("end", f"   Chemin: {app.get('executable_path', 'N/A')}\n")
                size_mb = app.get('file_size', 0) / 1024 / 1024 if app.get('file_size') else 0
                text_widget.insert("end", f"   Taille: {size_mb:.2f} MB\n")
                text_widget.insert("end", "\n" + "-"*80 + "\n\n")
            
            text_widget.configure(state="disabled")
            
            # Bouton fermer
            ttk.Button(
                main_frame,
                text="❌ Fermer",
                command=dialog.destroy
            ).pack(pady=(10, 0))
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'affichage des apps: {e}")
            messagebox.showerror("Erreur", f"❌ Erreur:\n{e}")

    def verify_database_integrity(self, parent_dialog=None):
        """Vérifie l'intégrité de la base de données"""
        from tkinter import messagebox, scrolledtext
        import tkinter as tk
        from tkinter import ttk
        
        if not self.installer_manager or not self.installer_manager.portable_db:
            return
        
        try:
            db = self.installer_manager.portable_db
            issues = db.verify_integrity()
            
            if not issues:
                messagebox.showinfo(
                    "Vérification d'intégrité",
                    "✅ AUCUN PROBLÈME DÉTECTÉ\n\n"
                    "La base de données est intègre.\n"
                    "Tous les fichiers sont présents et non modifiés."
                )
            else:
                # Créer une fenêtre pour afficher les problèmes
                dialog = tk.Toplevel(parent_dialog or self.root)
                dialog.title(f"⚠️ Problèmes détectés ({len(issues)})")
                dialog.geometry("700x400")
                dialog.configure(bg=self.DARK_BG)
                
                main_frame = ttk.Frame(dialog)
                main_frame.pack(fill="both", expand=True, padx=10, pady=10)
                
                title_label = tk.Label(
                    main_frame,
                    text=f"⚠️ {len(issues)} PROBLÈME(S) DÉTECTÉ(S)",
                    font=('Segoe UI', 12, 'bold'),
                    bg=self.DARK_BG,
                    fg=self.ACCENT_RED
                )
                title_label.pack(pady=(0, 10))
                
                text_widget = scrolledtext.ScrolledText(
                    main_frame,
                    font=('Consolas', 9),
                    bg=self.DARK_BG2,
                    fg=self.DARK_FG
                )
                text_widget.pack(fill="both", expand=True)
                
                for issue in issues:
                    text_widget.insert("end", f"⚠️ {issue['app']}\n", "app_name")
                    text_widget.insert("end", f"   Problème: {issue['issue']}\n")
                    text_widget.insert("end", f"   Chemin: {issue['path']}\n\n")
                
                text_widget.configure(state="disabled")
                
                ttk.Button(main_frame, text="❌ Fermer", command=dialog.destroy).pack(pady=(10, 0))
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification: {e}")
            messagebox.showerror("Erreur", f"❌ Erreur:\n{e}")

    def export_database_json(self, parent_dialog=None):
        """Exporte la base de données vers un fichier JSON"""
        from tkinter import messagebox, filedialog
        from datetime import datetime
        
        if not self.installer_manager or not self.installer_manager.portable_db:
            return
        
        try:
            # Demander où sauvegarder
            default_name = f"portable_apps_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filename = filedialog.asksaveasfilename(
                parent=parent_dialog or self.root,
                title="Exporter la base de données",
                defaultextension=".json",
                initialfile=default_name,
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                db = self.installer_manager.portable_db
                success = db.export_to_json(filename)
                
                if success:
                    messagebox.showinfo(
                        "Export réussi",
                        f"✅ Base de données exportée avec succès!\n\n"
                        f"Fichier: {filename}"
                    )
                else:
                    messagebox.showerror(
                        "Erreur d'export",
                        "❌ Impossible d'exporter la base de données."
                    )
        except Exception as e:
            self.logger.error(f"Erreur lors de l'export: {e}")
            messagebox.showerror("Erreur", f"❌ Erreur:\n{e}")


def create_gui_manager(root, installer_manager=None, config_manager=None):
    """Crée et retourne le GUI Manager complet"""
    return NiTriteGUIComplet(root, installer_manager, config_manager)
