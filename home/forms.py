from django import forms
from .models import Region,Ville,StationMeteorologique,AgentMeteorologique,MesureMeteorologique,Consulter,Previsionniste,Alert

class RegionForm(forms.ModelForm):
    class Meta:
        # Spécifie le modèle à utiliser
        model = Region 
        
        # Liste des champs du modèle Region que vous voulez inclure dans le formulaire
        # Note: 'id_region' est AutoField et est géré automatiquement.
        fields = [
            'nom', 
            'nombre_des_villes', 
            'densite_de_population', 
            'taille'
        ]
        
        # Vous pouvez également définir des labels personnalisés si nécessaire
        labels = {
            'nom': 'Nom de la Région',
            'nombre_des_villes': 'Nombre de Villes',
            'densite_de_population': 'Densité de Population',
            'taille': 'Taille (Surface en km²)',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Appliquer 'form-control' à tous les champs
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class VilleForm(forms.ModelForm):
    class Meta:
        model = Ville 
        # Liste des champs à inclure. 
        # Remarquez que 'region' est inclus car c'est la clé étrangère.
        fields = [
            'nom', 
            'suface', 
            'densite_population', 
            'region' 
        ]
        
        labels = {
            'nom': 'Nom de la Ville',
            'suface': 'Surface (km²)',
            'densite_population': 'Densité de Population',
            'region': 'Région Appartenante', # Ceci affichera un menu déroulant des régions
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Appliquer 'form-control' à tous les champs (Nom, Surface, Densité, Région)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class StationMeteorologiqueForm(forms.ModelForm):
    class Meta:
        model = StationMeteorologique 
        fields = '__all__'
        
        labels = {
            'nom': 'Nom de la Station',
            'altitude': 'Altitude (m)',
            'ville': 'Ville d\'implantation', 
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Application de la classe Bootstrap 'form-control' à tous les champs
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        
class AgentMeteorologiqueForm(forms.ModelForm):
    class Meta:
        model = AgentMeteorologique 
        
        fields = [
            'cin', # Ajout du CIN si vous voulez l'entrer via le formulaire
            'nom', 
            'prenom', 
            'age',
            'salaire',
            'date_embauche', # Maintenant, ce champ existe dans le modèle!
            'station' 
        ]
        
        labels = {
            'cin': 'CIN',
            'nom': 'Nom',
            'prenom': 'Prénom',
            'age': 'Âge',
            'salaire': 'Salaire',
            'date_embauche': 'Date d\'embauche (AAAA-MM-JJ)', 
            'station': 'Station d\'affectation', 
        }
        widgets = {
            # Utiliser un widget de type Date pour un meilleur affichage/saisie
            'date_embauche': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # CETTE BOUCLE APPLIQUE LE STYLE BOOTSTRAP
        for field_name, field in self.fields.items():
            
            # Appliquer la classe 'form-control' à presque tous les champs
            if not isinstance(field.widget, forms.CheckboxInput) and \
               not isinstance(field.widget, forms.RadioSelect) and \
               not isinstance(field.widget, forms.FileInput):
                
                # Surcharge des attributs du widget pour ajouter la classe 'form-control'
                field.widget.attrs['class'] = 'form-control'


class MesureMeteorologiqueForm(forms.ModelForm):
    class Meta:
        model = MesureMeteorologique
        fields = [
            'id_mesure', 
            'date_heure', 
            'temperature_moyenne', 
            'temperature_maximale', 
            'temperature_minimale',
            'taux_d_humidité', 
            'vitesse_du_vent', 
            'quantite_de_precipation', 
            'pression_atmospherique', 
            'direction_du_vent',
            'station',
            'agent'    
        ] 
        
        labels = {
            'id_mesure': "ID Mesure (Texte)",
            'date_heure': "Date et Heure (YYYY-MM-DD HH:MM:SS)",
            'temperature_moyenne': "T° Moyenne",
            'temperature_maximale': "T° Maximale",
            'temperature_minimale': "T° Minimale",
            'taux_d_humidité': "Taux d'Humidité (%)",
            'vitesse_du_vent': "Vitesse du Vent (km/h)",
            'quantite_de_precipation': "Précipitations (mm)",
            'pression_atmospherique': "Pression (hPa)",
            'direction_du_vent': "Direction du Vent",
            'station': "Station de Mesure",
            'agent': "Agent Météo",
        }
        widgets = {
            'date_heure': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class ConsulterForm(forms.ModelForm):
    class Meta:
        model = Consulter
        fields = ['station', 'previsionniste'] 
        
        labels = {
            'station': "Station à consulter",
            'previsionniste': "Prévisionniste consultant",
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Appliquer 'form-control' aux champs (Station et Prévisionniste sont probablement des Selects)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class PrevisionnisteForm(forms.ModelForm):
    class Meta:
        model = Previsionniste
        # Liste des champs à inclure dans le formulaire
        fields = ['cin', 'nom', 'prenom'] 
        
        # Si vous ne voulez pas que le champ CIN soit modifiable 
        # lors de la modification (update), vous pouvez le désactiver :
        widgets = {
            'cin': forms.TextInput(attrs={'placeholder': 'Entrez le CIN'}),
            'nom': forms.TextInput(attrs={'placeholder': 'Entrez le Nom'}),
            'prenom': forms.TextInput(attrs={'placeholder': 'Entrez le Prénom'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Appliquer 'form-control' aux champs (CIN, Nom, Prénom)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class AlertForm(forms.ModelForm):
    
    class Meta:
        # 🚨 CORRECTION MAJEURE : Utiliser le modèle Alert, pas AgentMeteorologique
        model = Alert 
        
        # Champs du modèle Alert
        fields = [
            'date_heure', 
            'type', 
            'zone_cocernee', 
            'niveau_de_gravite', 
            'station' 
        ] 
        
        # Labels personnalisés pour les champs (basés sur votre modèle Alert)
        labels = {
            # Le label 'date_heure' est utile si vous voulez un format précis
            'date_heure': "Date et Heure (YYYY-MM-DD HH:MM:SS)", 
            'type': "Type d'Alerte (Ex: Inondation, Tempête, Canicule)",
            'zone_cocernee': "Zone/Ville Concernée",
            'niveau_de_gravite': "Niveau de Gravité (Ex: Rouge, Orange)",
            'station': "Station Émettrice de l'Alerte",
        }
        
        # Widgets optionnels pour améliorer les champs
        widgets = {
            # Affiche un sélecteur de date/heure plus convivial
            'date_heure': forms.DateTimeInput(attrs={'type': 'datetime-local'}), 
            # Les champs 'type' et 'niveau_de_gravite' pourraient être des Select
            # si vous définissez des CHOICES dans votre modèle Alert.
            'type': forms.TextInput(attrs={'placeholder': 'Ex: Tempête de Vent'}),
            'niveau_de_gravite': forms.TextInput(attrs={'placeholder': 'Ex: Rouge (Risque Élevé)'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Utilisation de la classe Bootstrap 'form-control'
        for field_name, field in self.fields.items():
            # Assurez-vous que tous les champs reçoivent la classe form-control
            # sauf pour la clé étrangère (Select) si elle a besoin d'un style spécifique.
            if field_name != 'station':
                 field.widget.attrs['class'] = 'form-control'
            else:
                 # La clé étrangère est aussi form-control, mais c'est un Select
                 field.widget.attrs['class'] = 'form-select' # Utiliser form-select pour les <select> de Bootstrap
                 # Optionnel : personnaliser le label du premier choix vide
                 field.empty_label = "--- Sélectionner une station ---"