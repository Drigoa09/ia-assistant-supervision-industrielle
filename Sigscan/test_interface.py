
from dotenv import load_dotenv

#Chargement des variables d'environnement
load_dotenv()

object_carac = {"Chocolat" : [{
                    "lieu" : "Salle de bain", 
                    "x" : 0.1, 
                    "y" : 0.9, 
                    "date" : 0}, 
                    {
                    "lieu" : "Cuisine", 
                    "x" : 0.9, 
                    "y" : 0.1, 
                    "date" : 10}
                    ]}

from interface import interface_view

import matplotlib.pyplot as plt
import matplotlib.animation as animation

'''
interface_vue = interface_view(object_carac, 5, 5)

import matplotlib.pyplot as plt

interface_vue.set_caracs(0, 10, 10)

ani = animation.FuncAnimation(fig=interface_vue.fig, func=interface_vue.animate, frames=10, interval=1000)
plt.show()
'''

import unittest

class TestingClass(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestingClass, self).__init__(*args, **kwargs)
        

    def tester_trajectoire(self):
        object_carac = {"Chocolat" : [{
                    "lieu" : "Salle de bain", 
                    "x" : 1, 
                    "y" : 1000, 
                    "date" : 0}, 
                    {
                    "lieu" : "Cuisine", 
                    "x" : 1000, 
                    "y" : 1, 
                    "date" : 10}
                    ]}
        
        self.interface_view = interface_view(object_carac)
        
        self.interface_view.objets_carac = object_carac

        self.interface_view.set_caracs(0, 10, 10)
        ani = animation.FuncAnimation(fig=self.interface_view.fig, func=self.interface_view.animate, frames=10, interval=1000)
        
        plt.show()

if __name__ == "__main__":
    unittest.main()
