from django.db import models

# ==============================================================================
# 1. TABLE Region
# ==============================================================================
class Region(models.Model):
    # id_region SERIAL PRIMARY KEY
    id_region = models.AutoField(primary_key=True, verbose_name="ID Région") 
    nom = models.CharField(max_length=50, unique=True, verbose_name="Nom de la Région")
    nombre_des_villes = models.IntegerField(verbose_name="Nombre de Villes", default=0) 
    densite_de_population = models.IntegerField(verbose_name="Densité de Population") 
    taille = models.FloatField(verbose_name="Taille (Surface)") # DOUBLE PRECISION

    def __str__(self):
        return self.nom
        
    class Meta:
        verbose_name = "Région"
        verbose_name_plural = "Régions"
        db_table = 'region' # <-- Force l'utilisation du nom de table SQL
        ordering = ['nom']


# ==============================================================================
# 2. TABLE Ville (FK vers Region)
# ==============================================================================
class Ville(models.Model):
    # id_ville SERIAL PRIMARY KEY
    id_ville = models.AutoField(primary_key=True, verbose_name="ID Ville")
    nom = models.CharField(max_length=50, verbose_name="Nom de la Ville")
    suface = models.FloatField(verbose_name="Surface") 
    densite_population = models.IntegerField(verbose_name="Densité de Population")
    
    # id_region INT NOT NULL
    region = models.ForeignKey(
        Region, 
        on_delete=models.CASCADE, 
        related_name='villes',
        verbose_name="Région associée",
        db_column='id_region'
    )

    def __str__(self):
        # Utiliser un try/except au cas où la région associée n'existerait plus
        try:
            region_nom = self.region.nom
        except:
            region_nom = "Non définie"
            
        return f"{self.nom} ({region_nom})"
        
    class Meta:
        verbose_name = "Ville"
        verbose_name_plural = "Villes"
        db_table = 'ville'


# ==============================================================================
# 3. TABLE Previsionnistes
# ==============================================================================
class Previsionniste(models.Model):
    # cin VARCHAR(50) PRIMARY KEY
    cin = models.CharField(max_length=50, primary_key=True, verbose_name="CIN")
    nom = models.CharField(max_length=50, verbose_name="Nom")
    prenom = models.CharField(max_length=50, verbose_name="Prénom")
    
    # La relation Many-to-Many 'stations_consultées' sera définie ci-dessous

    def __str__(self):
        return f"{self.nom} {self.prenom}"
        
    class Meta:
        verbose_name = "Prévisionniste"
        verbose_name_plural = "Prévisionnistes"
        db_table = 'previsionnistes'


# ==============================================================================
# 4. TABLE Station_meteorologique (FK vers Ville)
# ==============================================================================
class StationMeteorologique(models.Model):
    TYPE_CHOICES = [
        ('URBAINE', 'Urbaine'),
        ('RURALE', 'Rurale'),
        ('MARITIME', 'Maritime'),
        ('DESERTIQUE', 'Désertique'),
        ('MONTAGNE', 'Montagne'),
        ('FORESTIERE', 'Forestière'),
        ('AEROPORTUAIRE', 'Aéroportuaire'),
        ('FLUVIALE', 'Fluviale'),
        ('INSULAIRE', 'Insulaire'),
    ]
    # code SERIAL PRIMARY KEY
    code = models.AutoField(primary_key=True, verbose_name="Code de la Station") 
    nom = models.CharField(max_length=50, verbose_name="Nom de la Station")
    latitude = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Latitude")
    longtitude = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Longitude")
    altitude = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Altitude")
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='URBAINE',
        verbose_name="Type de Station" # Label affiché dans le formulaire
    )
        
    # id_ville INT NOT NULL
    ville = models.ForeignKey(
        Ville, 
        on_delete=models.CASCADE, 
        related_name='stations',
        verbose_name="Ville associée",
        db_column='id_ville'
    )

    def __str__(self):
        return self.nom
        
    class Meta:
        verbose_name = "Station Météorologique"
        verbose_name_plural = "Stations Météorologiques"
        db_table = 'station_meteorologique'


# ==============================================================================
# 5. TABLE Agent_meteorologique (FK vers Station)
# ==============================================================================
class AgentMeteorologique(models.Model):
    # cin VARCHAR(50) PRIMARY KEY
    cin = models.CharField(max_length=50, primary_key=True, verbose_name="CIN")
    nom = models.CharField(max_length=50, verbose_name="Nom")
    prenom = models.CharField(max_length=50, verbose_name="Prénom")
    age = models.SmallIntegerField(verbose_name="Âge") 
    salaire = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Salaire")
    
    date_embauche = models.DateField(verbose_name="Date d'embauche")
    
    # code INT NOT NULL
    station = models.ForeignKey(
        'StationMeteorologique', # Utilisation d'une chaîne si la classe n'est pas définie avant
        on_delete=models.CASCADE, 
        related_name='agents',
        verbose_name="Station d'affectation",
        db_column='code'
    )

    def __str__(self):
        return f"{self.nom} {self.prenom}"
        
    class Meta:
        verbose_name = "Agent Météorologique"
        verbose_name_plural = "Agents Météorologiques"
        db_table = 'agent_meteorologique'

# ==============================================================================
# 6. TABLE mesure_meteorologique (FK vers Station et Agent)
# ==============================================================================
class MesureMeteorologique(models.Model):
    # id_mesure VARCHAR(50) PRIMARY KEY
    id_mesure = models.CharField(max_length=50, primary_key=True, verbose_name="ID de la Mesure")
    date_heure = models.DateTimeField(verbose_name="Date et Heure") # TIMESTAMP
    temperature_moyenne = models.IntegerField(verbose_name="Température Moyenne")
    temperature_maximale = models.IntegerField(verbose_name="Température Maximale")
    temperature_minimale = models.IntegerField(verbose_name="Température Minimale")
    taux_d_humidité = models.FloatField(verbose_name="Taux d'Humidité") 
    vitesse_du_vent = models.FloatField(verbose_name="Vitesse du Vent") 
    quantite_de_precipation = models.IntegerField(verbose_name="Quantité de Précipitation")
    pression_atmospherique = models.FloatField(verbose_name="Pression Atmosphérique") 
    direction_du_vent = models.CharField(max_length=50, verbose_name="Direction du Vent")
    
    # Clé étrangère vers Station (celle-ci est déjà corrigée si elle utilisait 'code')
    station = models.ForeignKey(
        'StationMeteorologique', 
        on_delete=models.SET_NULL, 
        related_name='mesures',
        null=True, blank=True,
        verbose_name="Station de mesure",
        db_column='code' # <-- Assurez-vous que cette ligne est correcte pour la station
    )
    
    # 🚨 CLÉ ÉTRANGÈRE AGENT : AJOUT DE db_column 🚨
    # cin VARCHAR(50) (peut être NULL)
    agent = models.ForeignKey(
        'AgentMeteorologique', 
        on_delete=models.SET_NULL, 
        related_name='mesures_prises',
        null=True, blank=True,
        verbose_name="Agent Météo",
        db_column='cin' # <-- CORRECTION : C'est probablement 'cin' ou 'cin_agent'
    )

    def __str__(self):
        return f"Mesure n°{self.id_mesure} du {self.date_heure}"
        
    class Meta:
        verbose_name = "Mesure Météorologique"
        verbose_name_plural = "Mesures Météorologiques"
        db_table = 'mesure_meteorologique'


# ==============================================================================
# 7. TABLE Alert (FK vers Station)
# ==============================================================================
class Alert(models.Model):
    # id_alerte SERIAL PRIMARY KEY
    id_alerte = models.AutoField(primary_key=True, verbose_name="ID Alerte")
    date_heure = models.DateTimeField(verbose_name="Date et Heure de l'Alerte")
    type = models.CharField(max_length=50, verbose_name="Type d'Alerte")
    
    # Rappel : vous avez déjà corrigé ceci dans la réponse précédente :
    zone_cocernee = models.CharField(
        max_length=50, 
        verbose_name="Zone Concernée",
        db_column='zone_cocernée' # <-- Le nom réel de la colonne SQL (Faute de frappe corrigée)
    ) 
    
    niveau_de_gravite = models.CharField(max_length=50, verbose_name="Niveau de Gravité")
    
    # 🚨 CORRECTION DU NOM DE COLONNE DE LA CLÉ ÉTRANGÈRE 🚨
    station = models.ForeignKey(
        StationMeteorologique, 
        on_delete=models.CASCADE, 
        related_name='alerts',
        verbose_name="Station émettrice",
        # Remplacer 'code_id' par 'code' selon l'indice PostgreSQL :
        db_column='code' # <--- NOUVELLE CORRECTION : C'est le nom que la BD attend.
    )

    def __str__(self):
        return f"Alerte {self.type} ({self.niveau_de_gravite})"
        
    class Meta:
        verbose_name = "Alerte"
        verbose_name_plural = "Alertes"
        db_table = 'alert'

# ==============================================================================
# 1. Définition des Modèles de Base (Previsionniste et StationMeteorologique)
#    (Assurez-vous que StationMeteorologique est définie ici ou avant)
# ==============================================================================

class Previsionniste(models.Model):
    # Correspond à la colonne CIN VARCHAR(50) PRIMARY KEY dans la DB
    cin = models.CharField(max_length=50, primary_key=True) 
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.cin})"
    
    class Meta:
        db_table = 'previsionnistes'

# Si StationMeteorologique est définie dans un autre fichier, assurez-vous de l'importer.
# Si elle est dans ce fichier, elle doit apparaître avant Consulter.

# ==============================================================================
# 2. TABLE Consulter (Association Many-to-Many explicite 'through')
# ==============================================================================

class Consulter(models.Model):
    # Clé étrangère vers StationMeteorologique. Utilise 'code' dans la DB.
    # Conserve primary_key=True pour que Django ne cherche pas de colonne 'id'
    station = models.ForeignKey(
        'StationMeteorologique', 
        on_delete=models.CASCADE, 
        verbose_name="Station",
        db_column='code',
        primary_key=True, 
    )
    # Clé étrangère vers Previsionniste. Utilise 'cin' dans la DB.
    # N'ajoutez PAS primary_key=True ici (pour éviter l'erreur E026)
    previsionniste = models.ForeignKey(
        'Previsionniste', 
        on_delete=models.CASCADE, 
        verbose_name="Prévisionniste",
        db_column='cin',
    )

    def __str__(self):
        return f"Consultation : Station {self.station.code} / Agent {self.previsionniste.cin}"

    class Meta:
        # Assure l'unicité de la clé composée (station + previsionniste)
        unique_together = (('station', 'previsionniste'),) 
        verbose_name = "Consultation de Station"
        verbose_name_plural = "Consultations de Stations"
        db_table = 'consulter'
        
        # Ligne CLÉ : Indique à Django d'utiliser la table existante sans la modifier 
        # (et donc, d'ignorer la colonne 'id' inexistante)
        managed = False 

# ==============================================================================
# 3. Ajout du Many-to-Many au modèle Previsionniste via la table 'Consulter'
# ==============================================================================

# Cette section DOIT venir APRÈS que Consulter et Previsionniste soient définies.
Previsionniste.add_to_class(
    'stations_consultées', 
    models.ManyToManyField(
        'StationMeteorologique', 
        through='Consulter', # La table intermédiaire
        related_name='previsionnistes_consultants',
        verbose_name="Stations consultées"
    )
)