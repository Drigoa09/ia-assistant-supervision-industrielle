import matplotlib.pyplot as plt

from Init_zones import get_areas_sigscan

from matplotlib.text import Text

class interface_view:

    #Créer le tableau de base contenant l'ensemble des zones et la position initiale des objets
    def __init__(self, objets_carac):
        self.fig, self.ax = plt.subplots()

        self.x_max = 0
        self.y_max = 0

        self.Objet_Actors = {}
        self.objets_carac = objets_carac

        #Obtenir la liste de l'ensemble des zones et les ajouter à ax
        #Faire un appel à la fonction get_areas (déjà écrit) pour obtenir les zones
        zones_requetes = get_areas_sigscan()

        for zone in zones_requetes:
            zone_text = Text(zone['positionX'], zone['positionY'], zone['name'], color = 'b')
            self.ax.add_artist(zone_text)

            self.x_max = max(zone['positionX'], self.x_max)
            self.y_max = max(zone['positionY'], self.y_max)

        #Obtenir les positions initiales et les ajouter à ax
        for objet in objets_carac:
            #Créer un objet Text représentant l'objet avec ses coordonnées le plus tôt et le nom de l'objet en jaune
            if objets_carac[objet] != []:
                Position = objets_carac[objet][0]
                objet_text = Text(Position['positionx'], Position['positiony'], objet, color = 'y')

                self.ax.add_artist(objet_text)
                self.Objet_Actors[objet] = objet_text

    def set_caracs(self, startDate, endDate, nb_frames_total):
         self.startDate = startDate
         self.endDate = endDate
         self.nb_frames_total = nb_frames_total

    #Produire une image pour la frame correspondante
    def animate(self, frame):

        #Convertir le numéro de la frame en temps correspondant
        dureeDate = self.endDate - self.startDate

        date_time = self.startDate + dureeDate * frame / (self.nb_frames_total - 1)

        #Modifier la position des objets sur le tableau de base
        for objet in self.objets_carac:
            #Trouver les positions postérieurs à la date demandée
            positions = self.objets_carac[objet]

            positions_anterieurs = [position for position in positions if position['creation_date'] <= date_time]

            n = len(positions)
            m = len(positions_anterieurs)

            #Calculer la bonne possible position de l'objet
            if n - m >= 1 and m >= 1:
                #Calculer la position intermédiaire entre la position à la bonne date et la prochaine
                bonne_position = positions_anterieurs[m - 1]
                prochaine_position = positions[m]

                #Calculer le pourcentage de date faite entre la position à la bonne date et la prochaine
                difference = prochaine_position['creation_date'] - bonne_position['creation_date']
                ratio = (date_time - bonne_position['creation_date']) / difference
                #Calculer la position intermédiaire
                x_int = bonne_position['positionx'] + ratio * (prochaine_position['positionx'] - bonne_position['positionx'])
                y_int = bonne_position['positiony'] + ratio * (prochaine_position['positiony'] - bonne_position['positiony'])

                self.Objet_Actors[objet].set_x(x_int)
                self.Objet_Actors[objet].set_y(y_int)

                self.x_max = max(x_int, self.x_max)
                self.y_max = max(y_int, self.y_max)
            elif n - m == 0 and m >= 1:
                #Prendre la position de l'objet à la bonne date
                bonne_position = positions_anterieurs[m-1]

                x_int = bonne_position['positionx']
                y_int = bonne_position['positiony']

                self.Objet_Actors[objet].set_x(x_int)
                self.Objet_Actors[objet].set_y(y_int)

                self.x_max = max(x_int, self.x_max)
                self.y_max = max(y_int, self.y_max)

        self.ax.set_xlim(0, self.x_max * 1.5)
        self.ax.set_ylim(0, self.y_max * 1.5)

        return self.ax
