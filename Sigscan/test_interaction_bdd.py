import unittest
from datetime import datetime
from State import State
from InteractionBdd.interactionBdd import InteractionBdd
from Requetes.areas import Area
from Requetes.objects import Objet
from Requetes.Agent_to_InteractionBdd import Temps

class TestInteractionBddDataContent(unittest.TestCase):

    def setUp(self):
        self.interaction = InteractionBdd()

    def build_state(self, obj=None, area=None, start=None, end=None):
        request = type("Request", (), {})()
        request.object = obj
        request.area = area
        request.startDate = start
        request.endDate = end
        return State(call_request=request)

    def test_fetch_all_positions_last_90_days(self):
        test_state = self.build_state()
        result_state = self.interaction.interactionBdd(test_state)

        df_list = result_state["dataFrames"]
        positions_df = next(d["dataFrame"] for d in df_list if d["role"] == "Positions objets")

        self.assertFalse(positions_df.empty, "DataFrame 'Positions objets' devrait contenir des données")
        self.assertIn("last_update_date", positions_df.columns)

    def test_positions_for_chariot_only(self):
        test_state = self.build_state(
            obj=Objet.CHARIOT,
            start=Temps(annee=2025, mois=2, jour=2),
            end=Temps(annee=2025, mois=6, jour=10)
        )
        result_state = self.interaction.interactionBdd(test_state)
        df = next(d["dataFrame"] for d in result_state["dataFrames"] if d["role"] == "Positions objets")

        self.assertFalse(df.empty, "Aucune position trouvée pour le Chariot")
        self.assertTrue((df["sigscan_object_name"].str.contains("Chariot")).all())

    def test_positions_for_area_tournage_only(self):
        test_state = self.build_state(
            area=Area.TOURNAGE,
            start=Temps(annee=2025, mois=2, jour=2),
            end=Temps(annee=2025, mois=6, jour=10)
        )
        result_state = self.interaction.interactionBdd(test_state)
        df = next(d["dataFrame"] for d in result_state["dataFrames"] if d["role"] == "Positions objets")

        self.assertFalse(df.empty, "Aucune position trouvée pour la zone Tournage")
        self.assertIn("Tournage", df["area_name"].unique())

    def test_positions_combined_filter(self):
        test_state = self.build_state(
            obj=Objet.CHARIOT,
            area=Area.JET_D_EAU,
            start=Temps(annee=2025, mois=2, jour=2),
            end=Temps(annee=2025, mois=6, jour=10)
        )
        result_state = self.interaction.interactionBdd(test_state)
        df = next(d["dataFrame"] for d in result_state["dataFrames"] if d["role"] == "Positions objets")

        self.assertFalse(df.empty, "Aucune position trouvée pour le Chariot dans Jet d'eau")
        self.assertTrue((df["sigscan_object_name"].str.contains("Chariot")).all())
        self.assertIn("Jet d'eau", df["area_name"].unique())


if __name__ == '__main__':
    unittest.main()
