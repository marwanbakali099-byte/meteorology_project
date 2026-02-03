from django.shortcuts import render, redirect # Conservez uniquement render et redirect pour la clarté
from django.http import HttpResponse # Inutile pour les vues actuelles, mais peut rester
from .models import Region ,Ville,StationMeteorologique,AgentMeteorologique,MesureMeteorologique,Consulter,Previsionniste,Alert
from .forms import RegionForm,VilleForm,StationMeteorologiqueForm,AgentMeteorologiqueForm,MesureMeteorologiqueForm,ConsulterForm,PrevisionnisteForm,AlertForm
from django.shortcuts import render, redirect, get_object_or_404
import csv
from django.db import IntegrityError
from django.db.models import Avg, Max, Min, Count
from .models import (
    StationMeteorologique, 
    AgentMeteorologique, 
    Ville, 
    MesureMeteorologique, 
    Alert
)


def home(request):
    # 1. Statistiques Globales
    total_stations = StationMeteorologique.objects.count()
    total_agents = AgentMeteorologique.objects.count()
    total_villes = Ville.objects.count()

    # Température max globale
    temp_max_agg = MesureMeteorologique.objects.aggregate(
        max_temp=Max('temperature_maximale')
    )
    temp_max_globale = temp_max_agg['max_temp']

    # 2. Alertes
    alertes_recentes = Alert.objects.all().order_by('-date_heure')[:3]
    total_alertes_actives = Alert.objects.count()

    # 3. Stations pour la carte (IMPORTANT)
    stations = StationMeteorologique.objects.select_related('ville')

    # 4. Contexte
    context = {
        'total_stations': total_stations,
        'total_agents': total_agents,
        'total_villes': total_villes,
        'temp_max_globale': temp_max_globale,
        'alertes_recentes': alertes_recentes,
        'total_alertes_actives': total_alertes_actives,

        # AJOUT POUR LA CARTE
        'stations': StationMeteorologique.objects.all()

    }

    return render(request, 'home/home.html', context)

# =========================================================
# 1. GESTION DES RÉGIONS
# =========================================================

# Renommée de 'region_create' en 'regions_form' (pour correspondre à votre URL)
def regions_form(request):
    """
    Gère la création d'une nouvelle région.
    """
    if request.method == 'POST':
        form = RegionForm(request.POST)
        
        if form.is_valid():
            form.save() 
            # La redirection doit utiliser le nom d'URL correct
            return redirect('regions_list') 
    else:
        form = RegionForm()

    context = {
        'form': form,
        'page_title': "Ajouter une nouvelle Région"
    }
    return render(request, 'home/regions_form.html', context)


# Partie de gestion des regions liste 
def region_list(request):
    """
    Récupère toutes les régions et les passe au template.
    """
    regions = Region.objects.all() 
    
    context = {
        'regions': regions,
        'page_title': "Liste des Régions"
    }
    return render(request,'home/regions_list.html',context)

# =========================================================
# 3. Modification (Update)
# =========================================================
def regions_update(request, pk):
    # Récupère l'instance existante via la clé primaire (id_region)
    region_instance = get_object_or_404(Region, pk=pk)

    if request.method == 'POST':
        # Crée le formulaire avec les données POST et l'instance existante
        form = RegionForm(request.POST, instance=region_instance)
        
        if form.is_valid():
            form.save() 
            return redirect('regions_list') 
    else:
        # Affiche le formulaire pré-rempli (GET)
        form = RegionForm(instance=region_instance)

    context = {
        'form': form,
        'page_title': "Modifier la Région",
        'is_update': True
    }
    return render(request, 'home/regions_form.html', context)


# =========================================================
# 4. Suppression (Delete)
# =========================================================
def regions_delete(request, pk):
    # Récupère l'instance existante (id_region)
    region_instance = get_object_or_404(Region, pk=pk)
    
    # La suppression se fait sans confirmation POST directe dans cette vue simplifiée
    region_instance.delete()
    
    # Rediriger vers la liste
    return redirect('regions_list')

# =========================================================
# 2. GESTION DES VILLES
# =========================================================

def villes_form(request):
    """Gère la création d'une nouvelle ville."""
    if request.method == 'POST':
        form = VilleForm(request.POST)
        
        if form.is_valid():
            form.save() 
            # La redirection doit utiliser le nom d'URL correct
            return redirect('villes_list') 
    else:
        form = VilleForm() # Formulaire vide pour la méthode GET

    context = {
        'form': form,
        'page_title': "Ajouter une nouvelle Ville"
    }
    return render(request, 'home/villes_form.html', context)


# FONCTIONS POUR VILLE (Liste)
def ville_list(request):
    """Affiche la liste de toutes les villes."""
    # Sélectionne toutes les villes et pré-charge les données de la région associée
    villes = Ville.objects.select_related('region').all()
    
    context = {
        'villes': villes,
        'page_title': "Liste des Villes"
    }
    return render(request, 'home/villes_list.html', context)

# =========================================================
# 3. Modification (Update)
# =========================================================
def villes_update(request, pk):
    # Récupère l'instance existante via la clé primaire (id_ville)
    ville_instance = get_object_or_404(Ville, pk=pk)

    if request.method == 'POST':
        # Charge l'instance existante pour la modification
        form = VilleForm(request.POST, instance=ville_instance)
        
        if form.is_valid():
            form.save() 
            return redirect('villes_list') 
    else:
        # Affiche le formulaire pré-rempli (GET)
        form = VilleForm(instance=ville_instance)

    context = {
        'form': form,
        'page_title': "Modifier la Ville",
        'is_update': True
    }
    # Utilise le même template que l'ajout
    return render(request, 'home/villes_form.html', context)


# =========================================================
# 4. Suppression (Delete)
# =========================================================
def villes_delete(request, pk):
    # Récupère l'instance existante (id_ville)
    ville_instance = get_object_or_404(Ville, pk=pk)
    
    # Suppression de l'instance
    ville_instance.delete()
    
    # Rediriger vers la liste
    return redirect('villes_list')

# =========================================================
# 3. GESTION DES STATIONS MÉTÉOROLOGIQUES
# =========================================================

## FONCTIONS POUR STATION (Liste)
def station_list(request):
    """Affiche la liste de toutes les stations météorologiques."""
    # Utilise select_related pour récupérer les données de la Ville et de la Région associées
    stations = StationMeteorologique.objects.select_related('ville__region').all()
    
    context = {
        'stations': stations,
        'page_title': "Liste des Stations Météorologiques"
    }
    return render(request, 'home/stations_list.html', context)


## FONCTIONS POUR STATION (Création/Formulaire)
def station_form(request):
    """Gère la création d'une nouvelle station."""
    if request.method == 'POST':
        form = StationMeteorologiqueForm(request.POST)
        
        if form.is_valid():
            form.save() 
            # Redirige l'utilisateur vers la liste des stations
            return redirect('stations_list') 
    else:
        form = StationMeteorologiqueForm()

    context = {
        'form': form,
        'page_title': "Ajouter une nouvelle Station Météorologique"
    }
    return render(request, 'home/stations_form.html', context)

# =========================================================
# 3. Modification (Update)
# =========================================================
def stations_update(request, pk):
    # Récupère l'instance existante via la clé primaire (code)
    station_instance = get_object_or_404(StationMeteorologique, pk=pk)

    if request.method == 'POST':
        form = StationMeteorologiqueForm(request.POST, instance=station_instance)
        
        if form.is_valid():
            form.save() 
            return redirect('stations_list') 
    else:
        form = StationMeteorologiqueForm(instance=station_instance)

    context = {
        'form': form,
        'page_title': "Modifier la Station",
        'is_update': True
    }
    return render(request, 'home/stations_form.html', context)


# =========================================================
# 4. Suppression (Delete)
# =========================================================
def stations_delete(request, pk):
    # Récupère l'instance existante (code)
    station_instance = get_object_or_404(StationMeteorologique, pk=pk)
    
    station_instance.delete()
    
    return redirect('stations_list')


# =========================================================
# 1. Liste et Lecture (Read)
# =========================================================
def alerts_list(request):
    alerts = Alert.objects.all()
    
    context = {
        'alerts': alerts,
        'page_title': "Liste des Alertes"
    }
    return render(request, 'home/alerts_list.html', context)


# =========================================================
# 2. Ajout et Création (Create)
# =========================================================
# Dans MonApp/views.py

def alerts_form(request):
    if request.method == 'POST':
        form = AlertForm(request.POST) # <-- Maintenant AlertForm est le bon formulaire
        
        if form.is_valid():
            form.save()
            return redirect('alerts_list')
    else:
        form = AlertForm()

    context = {
        'form': form,
        'page_title': "Ajouter une Alerte",
        'is_update': False
    }
    return render(request, 'home/alerts_form.html', context)

# =========================================================
# 3. Modification (Update)
# =========================================================
def alerts_update(request, pk):
    alert_instance = get_object_or_404(Alert, pk=pk)

    if request.method == 'POST':
        form = AlertForm(request.POST, instance=alert_instance)
        
        if form.is_valid():
            form.save() 
            return redirect('alerts_list') 
    else:
        form = AlertForm(instance=alert_instance)

    context = {
        'form': form,
        'page_title': "Modifier l'Alerte",
        'is_update': True
    }
    return render(request, 'home/alerts_form.html', context)


# =========================================================
# 4. Suppression (Delete)
# =========================================================
def alerts_delete(request, pk):
    alert_instance = get_object_or_404(Alert, pk=pk)
    
    alert_instance.delete()
    
    return redirect('alerts_list')


# =========================================================
# 4. GESTION DES AGENTS MÉTÉOROLOGIQUES
# =========================================================

## FONCTIONS POUR AGENT (Liste)
def agents_list(request):
    """Affiche la liste de tous les agents météorologiques."""
    # Utilise select_related pour récupérer les données de la Station et de la Ville
    agents = AgentMeteorologique.objects.select_related('station__ville').all()
    
    context = {
        'agents': agents,
        'page_title': "Liste des Agents Météorologiques"
    }
    return render(request, 'home/agents_list.html', context)

## FONCTIONS POUR AGENT (Création/Formulaire)
def agents_form(request):
    """Gère la création d'un nouvel agent."""
    if request.method == 'POST':
        form = AgentMeteorologiqueForm(request.POST)
        
        if form.is_valid():
            form.save() 
            # Redirige l'utilisateur vers la liste des agents
            return redirect('agents_list') 
    else:
        form = AgentMeteorologiqueForm()

    context = {
        'form': form,
        'page_title': "Ajouter un nouvel Agent Météorologique"
    }
    return render(request, 'home/agents_form.html', context)

# =========================================================
# 3. Modification (Update)
# =========================================================
def agents_update(request, pk):
    # Récupère l'instance existante via la clé primaire (CIN)
    # Notez que pk est ici la chaîne de caractères (CIN)
    agent_instance = get_object_or_404(AgentMeteorologique, pk=pk)

    if request.method == 'POST':
        # Le formulaire est lié à l'instance existante
        form = AgentMeteorologiqueForm(request.POST, instance=agent_instance)
        
        if form.is_valid():
            form.save() 
            return redirect('agents_list') 
    else:
        # Affiche le formulaire pré-rempli (GET)
        form = AgentMeteorologiqueForm(instance=agent_instance)
        
        # Désactiver le champ CIN pour la modification (le CIN ne doit pas changer)
        # Note: 'cin' est le nom du champ dans le ModelForm
        form.fields['cin'].widget.attrs['readonly'] = 'readonly'

    context = {
        'form': form,
        'page_title': "Modifier l'Agent",
        'is_update': True
    }
    # Utiliser un template d'agent_form (à créer/adapter)
    return render(request, 'home/agents_form.html', context)


# =========================================================
# 4. Suppression (Delete)
# =========================================================
def agents_delete(request, pk):
    # Récupère l'instance existante (CIN)
    agent_instance = get_object_or_404(AgentMeteorologique, pk=pk)
    
    # Suppression de l'instance
    agent_instance.delete()
    
    # Rediriger vers la liste
    return redirect('agents_list')

# =========================================================
# 5. Gestion des Mesures Météorologiques (MESURES)
# =========================================================

## Dictionnaire de la vue Liste (List)
def mesures_list(request):
    """Affiche la liste de toutes les mesures météorologiques."""
    # Utiliser select_related pour joindre Station, Ville, et Agent en une seule requête.
    mesures = MesureMeteorologique.objects.select_related('station__ville', 'agent').all().order_by('-date_heure')
    
    context = {
        'mesures': mesures,
        'page_title': "Liste des Mesures Météorologiques"
    }
    return render(request, 'home/mesures_list.html', context)

## Dictionnaire de la vue Formulaire (Form)
def mesures_form(request):
    """Gère l'ajout d'une nouvelle mesure."""
    if request.method == 'POST':
        form = MesureMeteorologiqueForm(request.POST)
        
        if form.is_valid():
            form.save() 
            # Redirection vers la liste après l'enregistrement
            return redirect('mesures_list') 
    else:
        form = MesureMeteorologiqueForm()

    context = {
        'form': form,
        'page_title': "Ajouter une Mesure Météorologique"
    }
    # NOTE: Le template doit s'appeler 'mesures_form.html'
    return render(request, 'home/mesures_form.html', context)

# =========================================================
# 3. Modification (Update)
# =========================================================
def mesures_update(request, pk):
    # Récupère l'instance existante via la clé primaire (id_mesure)
    mesure_instance = get_object_or_404(MesureMeteorologique, pk=pk)

    if request.method == 'POST':
        form = MesureMeteorologiqueForm(request.POST, instance=mesure_instance)
        
        if form.is_valid():
            form.save() 
            return redirect('mesures_list') 
    else:
        form = MesureMeteorologiqueForm(instance=mesure_instance)
        
        # Désactiver le champ ID pour la modification
        form.fields['id_mesure'].widget.attrs['readonly'] = 'readonly'


    context = {
        'form': form,
        'page_title': "Modifier la Mesure",
        'is_update': True
    }
    return render(request, 'home/mesures_form.html', context)


# =========================================================
# 4. Suppression (Delete)
# =========================================================
def mesures_delete(request, pk):
    # Récupère l'instance existante (id_mesure)
    mesure_instance = get_object_or_404(MesureMeteorologique, pk=pk)
    
    mesure_instance.delete()
    
    return redirect('mesures_list')

# =========================================================
# 6. Gestion des Agents Météorologiques (PREVISIONNISTES)
# =========================================================

## Dictionnaire de la vue Liste (List)
def previsionnistes_list(request):
    """Affiche la liste de tous les agents (ou prévisionnistes)."""
    # 🚨 Assurez-vous d'avoir 'select_related('station')' ici et non 'region'
    agents = AgentMeteorologique.objects.select_related('station').all().order_by('nom') 
    
    context = {
        'agents': agents,
        'page_title': "Liste des Prévisionnistes"
    }
    # 🚨 Utilise le template dédié
    return render(request, 'home/previsionnistes_list.html', context) 

## Dictionnaire de la vue Formulaire (Form)
def previsionnistes_form(request):
    """Gère l'ajout d'un nouvel agent/prévisionniste."""
    if request.method == 'POST':
        form = AgentMeteorologiqueForm(request.POST)
        
        if form.is_valid():
            form.save()
            # Redirection vers la liste des prévisionnistes
            return redirect('previsionnistes_list') 
    else:
        form = AgentMeteorologiqueForm()

    context = {
        'form': form,
        'page_title': "Ajouter un Prévisionniste"
    }
    # 🚨 Utilise le template dédié
    return render(request, 'home/previsionnistes_form.html', context)

# =========================================================
# 3. Modification (Update)
# =========================================================
def previsionnistes_update(request, pk):
    # Récupère l'instance existante via la clé primaire (CIN)
    previsionniste_instance = get_object_or_404(Previsionniste, pk=pk)

    if request.method == 'POST':
        # Le formulaire est lié à l'instance existante
        form = PrevisionnisteForm(request.POST, instance=previsionniste_instance)
        
        if form.is_valid():
            form.save() 
            return redirect('previsionnistes_list') 
    else:
        # Affiche le formulaire pré-rempli (GET)
        form = PrevisionnisteForm(instance=previsionniste_instance)
        
        # Le CIN est la clé primaire, il est généralement préférable de ne pas le changer
        form.fields['cin'].widget.attrs['readonly'] = 'readonly'

    context = {
        'form': form,
        'page_title': "Modifier le Prévisionniste",
        'is_update': True
    }
    return render(request, 'home/previsionnistes_form.html', context)

# =========================================================
# 3. Modification (Update)
# =========================================================
def consulter_update(request, station_pk, previsionniste_pk):
    
    # 1. Trouver l'instance Consulter existante
    # Nous utilisons les PK des modèles Station et Previsionniste
    try:
        instance = Consulter.objects.get(
            station__code=station_pk,          
            previsionniste__cin=previsionniste_pk 
        )
    except Consulter.DoesNotExist:
        return redirect('consulter_list')
        
    if request.method == 'POST':
        # 2. Lier le formulaire à l'instance existante
        # IMPORTANT : Lier le formulaire à l'instance existante permet de la remplacer.
        form = ConsulterForm(request.POST, instance=instance)
        
        if form.is_valid():
            try:
                form.save() 
                return redirect('consulter_list')
            except IntegrityError:
                # Gérer l'erreur si l'utilisateur essaie de créer une association existante (même station, même prévisionniste)
                form.add_error(None, "Cette association Station / Prévisionniste existe déjà.")
            except Exception as e:
                form.add_error(None, f"Erreur de sauvegarde: {e}")
    else:
        # 3. Afficher le formulaire pré-rempli (GET)
        form = ConsulterForm(instance=instance)

    context = {
        'form': form,
        'page_title': "Modifier la Consultation",
        'is_update': True
    }
    return render(request, 'home/consulter_form.html', context)

# =========================================================
# 4. Suppression (Delete)
# =========================================================
def previsionnistes_delete(request, pk):
    # Récupère l'instance existante (CIN)
    previsionniste_instance = get_object_or_404(Previsionniste, pk=pk)
    
    # Suppression de l'instance
    previsionniste_instance.delete()
    
    # Rediriger vers la liste
    return redirect('previsionnistes_list')


# =========================================================
# 1. Liste et Lecture (Read)
# =========================================================
def consulter_list(request):
    # Utilisation de select_related pour éviter les requêtes N+1
    consultations = Consulter.objects.all().select_related('station', 'previsionniste')
    
    context = {
        'consultations': consultations,
        'page_title': "Liste des Enregistrements de Consultation"
    }
    return render(request, 'home/consulter_list.html', context)


# =========================================================
# 2. Ajout et Création (Create)
# =========================================================
def consulter_form(request):
    if request.method == 'POST':
        form = ConsulterForm(request.POST)
        
        if form.is_valid():
            try:
                # La validation du formulaire vérifie déjà l'unicité (unique_together dans Meta)
                form.save()
                return redirect('consulter_list')
            except Exception as e:
                # Gérer les erreurs de base de données (ex: violation unique_together)
                form.add_error(None, "Erreur : Cette consultation existe déjà ou les clés sont invalides.")
                print(f"Erreur lors de la sauvegarde: {e}")
    else:
        form = ConsulterForm()

    context = {
        'form': form,
        'page_title': "Ajouter une Consultation",
        'is_update': False
    }
    # Nous allons utiliser ce template pour le formulaire
    return render(request, 'home/consulter_form.html', context)


# =========================================================
# 4. Suppression (Delete)
# Note : Nous utilisons les PK des deux objets liés
# =========================================================
def consulter_delete(request, station_pk, previsionniste_pk):
    # station_pk est le 'code' de la station (un int, ici traité comme str dans l'URL)
    # previsionniste_pk est le 'cin' du prévisionniste (un str)

    # Note : Le filtre DOIT utiliser le nom du champ de relation (station et previsionniste)
    # et non le nom de la colonne DB (code et cin).
    
    # Trouver l'instance Consulter qui correspond à la clé composite
    try:
        consultation_instance = Consulter.objects.get(
            station__code=station_pk,          # Utilise la PK de l'objet Station
            previsionniste__cin=previsionniste_pk # Utilise la PK de l'objet Previsionniste
        )
    except Consulter.DoesNotExist:
        # Gérer le cas où l'association n'existe pas
        return redirect('consulter_list') # ou afficher un message d'erreur

    # Suppression de l'instance
    consultation_instance.delete()
    
    return redirect('consulter_list')


def previsionnistes_list(request):
    """
    Affiche la liste de tous les prévisionnistes.
    """
    # Récupère tous les enregistrements du modèle Previsionniste
    previsionnistes = Previsionniste.objects.all()
    
    context = {
        # Passe la liste au template
        'previsionnistes': previsionnistes,
        'page_title': "Liste des Prévisionnistes"
    }
    # Rend le template previsionnistes_list.html
    return render(request, 'home/previsionnistes_list.html', context)

# =========================================================
# 2. Ajout et Création (Create)
# =========================================================
def previsionnistes_form(request):
    """
    Gère l'affichage du formulaire (GET) et la création d'un nouvel enregistrement (POST).
    """
    if request.method == 'POST':
        # Crée une instance de formulaire remplie avec les données envoyées (POST)
        form = PrevisionnisteForm(request.POST)
        
        if form.is_valid():
            # Si les données sont valides, sauvegarde le nouvel enregistrement dans la DB
            form.save()
            # Redirige l'utilisateur vers la liste des prévisionnistes après l'ajout
            return redirect('previsionnistes_list')
    else:
        # Si c'est une requête GET, affiche un formulaire vide
        form = PrevisionnisteForm()

    context = {
        'form': form,
        'page_title': "Ajouter un Prévisionniste",
        # Utilisé par le template pour afficher le bon titre/bouton
        'is_update': False 
    }
    # Rend le template previsionnistes_form.html
    return render(request, 'home/previsionnistes_form.html', context)


def statistiques(request):

    # ===============================
    # STATISTIQUES GLOBALES
    # ===============================
    global_stats = MesureMeteorologique.objects.aggregate(
        temp_max=Max("temperature_maximale"),
        temp_min=Min("temperature_minimale"),
        temp_moy=Avg("temperature_moyenne"),
        total_mesures=Count("id_mesure")
    )

    # ===============================
    # STATISTIQUES PAR VILLE
    # ===============================
    stats_villes = (
        MesureMeteorologique.objects
        .values("station__ville__nom")
        .annotate(
            temp_moy=Avg("temperature_moyenne"),
            humidite_moy=Avg("taux_d_humidité"),
            vent_moy=Avg("vitesse_du_vent"),
            total_mesures=Count("id_mesure")
        )
        .order_by("station__ville__nom")
    )

    # ===============================
    # DONNÉES POUR CHART.JS
    # ===============================
    labels = []
    temp_values = []
    humidite_values = []

    for s in stats_villes:
        labels.append(s["station__ville__nom"])
        temp_values.append(round(s["temp_moy"], 2))
        humidite_values.append(round(s["humidite_moy"], 2))

    context = {
        # global
        "temp_max": global_stats["temp_max"],
        "temp_min": global_stats["temp_min"],
        "temp_moy": round(global_stats["temp_moy"], 2),
        "total_mesures": global_stats["total_mesures"],

        # par ville
        "stats_villes": stats_villes,

        # chart
        "labels": labels,
        "temp_values": temp_values,
        "humidite_values": humidite_values,
    }

    return render(request, "home/stats.html", context)

def telecharger_rapport(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="rapport_statistiques.csv"'

    writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    # En-têtes
    writer.writerow([
        "ID Mesure", "Date & Heure", "Station", "Ville", 
        "Température Moyenne", "Température Max", "Température Min",
        "Humidité", "Vent (km/h)", "Précipitation", "Pression", "Direction du Vent", "Agent"
    ])

    # Données
    mesures = MesureMeteorologique.objects.all()
    for m in mesures:
        writer.writerow([
            m.id_mesure,
            m.date_heure.strftime("%Y-%m-%d %H:%M:%S"),
            m.station.nom if m.station else "",
            m.station.ville.nom if m.station else "",
            m.temperature_moyenne,
            m.temperature_maximale,
            m.temperature_minimale,
            m.taux_d_humidité,
            m.vitesse_du_vent,
            m.quantite_de_precipation,
            m.pression_atmospherique,
            m.direction_du_vent,
            f"{m.agent.nom} {m.agent.prenom}" if m.agent else ""
        ])

    return response