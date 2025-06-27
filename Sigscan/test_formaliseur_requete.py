from typing import Optional, TypedDict
import unittest
from dotenv import load_dotenv
from devtools import pprint
from pydantic import Field

#Chargement des variables d'environnement
load_dotenv()


from State import State

from Requetes.areas import Area
from Requetes.objects import Objet
from Agents.formaliseur_requete import Formalisateur_requete
from Agents.prompt import PROMPT

from Requetes.Agent_to_InteractionBdd import Temps

class TestingClass(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestingClass, self).__init__(*args, **kwargs)
        self.formalisateur_requete = Formalisateur_requete(PROMPT, Objet, Area)

    def correspondre_question(self, question : str, reponse_attendue):
        print()
        print("Evaluation des réponses de l'agent pour la question... \n")

        state = State(question=question)

        response_state = self.formalisateur_requete.formaliser_requete(state)

        print(f"""Test :
              {reponse_attendue.object} == {response_state['call_request'].object}
              {reponse_attendue.area} == {response_state['call_request'].area}
              {reponse_attendue.startDate} == {response_state['call_request'].startDate}
              {reponse_attendue.endDate} == {response_state['call_request'].endDate}""")

        assert reponse_attendue.object == response_state['call_request'].object
        assert reponse_attendue.area == response_state['call_request'].area
        assert reponse_attendue.startDate == response_state['call_request'].startDate
        assert reponse_attendue.endDate == response_state['call_request'].endDate

    def test_question_1(self):
        
        question = "Quelles sont les positions du 02/02/2024 au 10/05/2024 du Chariot ?"

        reponse_attendue = self.formalisateur_requete.dict_Structure(
            object = Objet.CHARIOT,
            area = None,
            startDate = Temps(annee = 2024, mois = 2, jour = 2),
            endDate = Temps(annee = 2024, mois = 5, jour = 10)
        )

        self.correspondre_question(question, reponse_attendue)

    def test_question_2(self):
        
        question = "Illustre les pièces présentes dans la zone Tournage du 01/03/2025 au 01/06/2025"

        reponse_attendue = self.formalisateur_requete.dict_Structure(
            object = None,
            area = Area.TOURNAGE,
            startDate = Temps(annee = 2025, mois = 3, jour = 1),
            endDate = Temps(annee = 2025, mois = 6, jour = 1)
        )

        self.correspondre_question(question, reponse_attendue)

    def test_question_3(self):
        
        question = "Liste les pièces et leur zone associée"

        reponse_attendue = self.formalisateur_requete.dict_Structure(
            object = None,
            area = None,
            startDate = None,
            endDate = None
        )

        self.correspondre_question(question, reponse_attendue)

    def test_question_4(self):
        
        question = "Liste les fois où le Chariot est passé dans la zone Jet d'eau du 12/08/2025 au 19/10/2025"

        reponse_attendue = self.formalisateur_requete.dict_Structure(
            object = Objet.CHARIOT,
            area = Area.JET_D_EAU,
            startDate = Temps(annee = 2025, mois = 8, jour = 12),
            endDate = Temps(annee = 2025, mois = 10, jour = 19)
        )

        self.correspondre_question(question, reponse_attendue)

if __name__ == "__main__":
    unittest.main()

