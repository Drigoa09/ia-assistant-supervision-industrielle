from Tools_nodes.treatment_node.traitement_format import fonctions_existantes

from Tools_nodes.treatment_node.outils_fonctions.creer_graphique import creer_graphique
from Tools_nodes.treatment_node.outils_fonctions.exprimer_information_en_fonction_autre import exprimer_information_en_fonction_autre
from Tools_nodes.treatment_node.outils_fonctions.filtrer_comparaison import filtrer_comparaison
from Tools_nodes.treatment_node.outils_fonctions.filtrer_valeur import filtrer_valeur
from Tools_nodes.treatment_node.outils_fonctions.n_premiers import n_premiers
from Tools_nodes.treatment_node.outils_fonctions.plus_occurent import plus_occurent

D = {
    fonctions_existantes.PLUS_OCCURENT : plus_occurent,
    fonctions_existantes.INFORMATION_EN_FONCTION_AUTRE : exprimer_information_en_fonction_autre,
    fonctions_existantes.FILTRER_VALEUR : filtrer_valeur,
    fonctions_existantes.CREER_GRAPHIQUE : creer_graphique,
    fonctions_existantes.FILTRER_COMPARAISON : filtrer_comparaison,
    fonctions_existantes.N_PREMIERS : n_premiers
}
