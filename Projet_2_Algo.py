# Définition des classes nécessaires pour le système de facturation

class Client:
    def __init__(self, nom, date_naissance, numero_telephone, facture=0.0):
        self.nom = nom
        self.date_naissance = date_naissance
        self.numero_telephone = numero_telephone
        self.facture = facture

    def get_facture(self):
        return self.facture

    def set_facture(self, facture):
        self.facture = facture


class GestionClients:
    def __init__(self):
        self.clients = {}
        self.facturation = Facturation()
        self.statistique = Statistique()

    def ajouter_client(self, client):
        if client.numero_telephone in self.clients :
            print("Ce Client existe déjà sur la liste.")
        else:
            self.clients[client.numero_telephone] = client
            print(f"le client {client.nom} ajouté avec succès")

    def obtenir_client(self, numero_telephone):
        # Vérifier si le numéro de téléphone est dans le dictionnaire des clients
        if numero_telephone in self.clients:
            return self.clients[numero_telephone]
        else:
            print("Aucun client trouvé avec ce numéro de téléphone.")
            return None

    def traiter_cdr_client(self, pile_cdr, numero_client):
        montant_total = 0
        for cdr in pile_cdr:
            if cdr['appelant'] == numero_client:
                self.statistique.ajouter_cdr(cdr)
                montant_facture = self.facturation.calculer_facture(cdr)
                # Vérifier le type de service avant d'imprimer le message
                if cdr['type_call'] == 0:  # Appel
                    service = "l'appel"
                elif cdr['type_call'] == 1:  # SMS
                    service = "le SMS"
                elif cdr['type_call'] == 2:  # Internet
                    service = "l'utilisation d'Internet"
                print(f"Montant de la facture pour {service} {cdr['identifiant_appel']}: {montant_facture} $")
                montant_total += montant_facture
                # Mise à jour de la facture dans l'objet Client
                client = self.obtenir_client(numero_client)
                if client:
                    client.set_facture(client.get_facture() + montant_facture)
        print(f"Le montant total de la facture : {montant_total} $")
        stats_client = self.statistique.obtenir_statistiques(numero_client)
        return f"Statistiques pour le client {numero_client}: {stats_client}"

class ImportCDR:
    def __init__(self, chemin_fichier):
        self.chemin_fichier = chemin_fichier
        self.pile_cdr = []

    def importer_cdr(self):
        with open(self.chemin_fichier, 'r') as fichier:
            for ligne in fichier:
                elements = ligne.strip().split('|')
                cdr_dict = {
                    'identifiant_appel': int(elements[0]),
                    'type_call': int(elements[1]),
                    'date_heure': elements[2],
                    'appelant': elements[3],
                    'appele': elements[4],
                    # Gérer les chaînes vides pour la durée
                    'duree': int(elements[5]) if elements[5] else 0,
                    'taxe': int(elements[6]),
                    'total_volume': float(elements[7]) if elements[7] else 0.0
                }
                self.pile_cdr.append(cdr_dict)

    def obtenir_pile_cdr(self):
        return self.pile_cdr


class Facturation:
    TARIF_SMS_MEME_RESEAU = 0.001
    TARIF_SMS_AUTRE_RESEAU = 0.002
    TARIF_APPEL_MEME_RESEAU = 0.025 / 60
    TARIF_APPEL_AUTRE_RESEAU = 0.05 / 60
    TARIF_INTERNET = 0.03

    def est_meme_reseau(self, numero_appele):
        if not numero_appele:
            return False
        prefixes_vodacom = ['24381', '24382', '24383']
        return any(numero_appele.startswith(prefix) for prefix in prefixes_vodacom)

    def calculer_facture(self, cdr):
        total = 0
        numero_appele = cdr.get('appele', '')
        meme_reseau = self.est_meme_reseau(numero_appele)

        if cdr['type_call'] == 0:
            total += self.calculer_cout_appel(cdr['duree'], meme_reseau)
        elif cdr['type_call'] == 1:
            total += self.calculer_cout_sms(meme_reseau)
        elif cdr['type_call'] == 2:
            total += self.calculer_cout_internet(cdr['total_volume'])

        if cdr['taxe'] == 1:
            total *= 1.05
        elif cdr['taxe'] == 2:
            total *= 1.16

        return total

    def calculer_cout_sms(self, meme_reseau):
        return self.TARIF_SMS_MEME_RESEAU if meme_reseau else self.TARIF_SMS_AUTRE_RESEAU

    def calculer_cout_appel(self, duree, meme_reseau):
        tarif = self.TARIF_APPEL_MEME_RESEAU if meme_reseau else self.TARIF_APPEL_AUTRE_RESEAU
        return duree * tarif

    def calculer_cout_internet(self, total_volume):
        return total_volume * self.TARIF_INTERNET


class Statistique:
    def __init__(self):
        self.statistiques = {}

    def ajouter_cdr(self, cdr):
        numero_client = cdr['appelant']
        if numero_client not in self.statistiques:
            self.statistiques[numero_client] = {'appels': 0, 'duree_appels': 0,
                                                'sms': 0, 'internet_gb': 0}

        if cdr['type_call'] == 0:
            self.statistiques[numero_client]['appels'] += 1
            self.statistiques[numero_client]['duree_appels'] += cdr['duree']
        elif cdr['type_call'] == 1:
            self.statistiques[numero_client]['sms'] += 1
        elif cdr['type_call'] == 2:
            self.statistiques[numero_client]['internet_gb'] += cdr['total_volume'] / 1024

    def obtenir_statistiques(self, numero_client):
        return self.statistiques.get(numero_client, {})


# Création d'une instance de la classe GestionClients
gestion_clients = GestionClients()

# Ajout du client POLYTECHNIQUE avec ses deux numéros
client_polytechnique = Client("POLYTECHNIQUE", "01/01/2000", "243818140560")
gestion_clients.ajouter_client(client_polytechnique)
client_polytechnique_2 = Client("POLYTECHNIQUE", "01/01/2000", "243818140120")
gestion_clients.ajouter_client(client_polytechnique_2)

# Importation des CDR
import_cdr1 = ImportCDR('cdr.txt')
import_cdr2 = ImportCDR('tp_algo.txt')

import_cdr1.importer_cdr()
import_cdr2.importer_cdr()

# Calcul des statistiques et de la facture pour le premier numéro
gestion_clients.traiter_cdr_client(import_cdr1.obtenir_pile_cdr(), "243818140560")
print(gestion_clients.traiter_cdr_client(import_cdr2.obtenir_pile_cdr(), "243818140560"))

# Calcul des statistiques et de la facture pour le second numéro
gestion_clients.traiter_cdr_client(import_cdr1.obtenir_pile_cdr(), "243818140120")
print(gestion_clients.traiter_cdr_client(import_cdr2.obtenir_pile_cdr(), "243818140120"))

# Récupérer les informations du client POLYTECHNIQUE avec ses deux numéros
Client_1 = gestion_clients.obtenir_client("243818140560")
Client_2 = gestion_clients.obtenir_client("243818140120")

print(f"Le client {Client_1.nom} avec le numéro {Client_1.numero_telephone} a une facture totale de {Client_1.get_facture()} $")
print(f"Le client {Client_2.nom} avec le numéro {Client_2.numero_telephone} a une facture totale de {Client_2.get_facture()} $")

