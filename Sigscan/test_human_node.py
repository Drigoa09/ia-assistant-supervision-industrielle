import contextlib
import unittest
from dotenv import load_dotenv

from langchain_core.messages import AIMessage

#Chargement des variables d'environnement
load_dotenv()


from Sigscan.Human.welcome_msg import WELCOME_MSG
from State import State

from Human.human import Human

from unittest.mock import patch

from langgraph.graph import END

import io

INPUT = 'Quel temps fait-il aujourd''hui ?'

class TestingClass(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestingClass, self).__init__(*args, **kwargs)
        self.formalisateur_requete = Human("Antoine Drigo", WELCOME_MSG)

    @patch('builtins.input', return_value=INPUT)
    def tester_msg_vide(self, mock_input):
        buffer = io.StringIO()
        state = State(messages=[])

        with contextlib.redirect_stdout(buffer):
            new_state = self.formalisateur_requete.demander_question(state)

        print(f'''\nTest :
              {buffer.getvalue()} == "{WELCOME_MSG + "\n"}''')
        
        assert buffer.getvalue() == WELCOME_MSG + "\n"

    @patch('builtins.input', return_value=INPUT)
    def tester_msg_present(self, mock_input):
        buffer = io.StringIO()

        msg = "Actualité : Le PSG gagne la ligue des Champions"

        state = State(messages=[AIMessage(content = msg)])

        with contextlib.redirect_stdout(buffer):
            new_state = self.formalisateur_requete.demander_question(state)

        print(f'''\nTest :
              {buffer.getvalue()} == "Model : {msg + "\n"}''')
        
        assert buffer.getvalue() == "Model : " + msg + "\n"

    @patch('builtins.input', return_value=INPUT)
    def tester_msg_entre(self, mock_input):
        buffer = io.StringIO()

        msg = "Actualité : Le PSG gagne la ligue des Champions"

        state = State(messages=[AIMessage(content = msg)])

        with contextlib.redirect_stdout(buffer):
            new_state = self.formalisateur_requete.demander_question(state)

        print(f'''\nTest :
              "{new_state["messages"][-1].content}" == "{INPUT}"''')
        
        assert new_state["messages"][-1].content == INPUT

    def tester_exit_with_human_node(self):

        state_non_fini = State(finished=False)
        state_fini = State(finished=True)

        assert self.formalisateur_requete.maybe_exit_with_human_node(state_non_fini) == "Formalisateur de requête"
        assert self.formalisateur_requete.maybe_exit_with_human_node(state_fini) == END

if __name__ == "__main__":
    unittest.main()
