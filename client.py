import os
import socket

HOTE = "localhost"
PORT = 9000
CHEMIN = "/gros.bin"          # fichier à télécharger (un seul pour l'instant)
DOSSIER = "downloads"          # dossier où enregistrer le fichier


def envoyer_requete(hote, port, chemin):
    requete = (
        f"GET {chemin} HTTP/1.1\r\n"
        f"Host: {hote}:{port}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((hote, port))
        s.sendall(requete.encode("ascii"))

        reponse = bytearray()
        while True:
            bloc = s.recv(4096)
            if not bloc:
                break
            reponse.extend(bloc)

    return bytes(reponse)


def separer_reponse(reponse):
    entetes, separateur, corps = reponse.partition(b"\r\n\r\n")
    if not separateur:
        raise ValueError("Réponse HTTP invalide")

    ligne = entetes.split(b"\r\n", 1)[0].decode("ascii")
    return ligne, entetes, corps


if __name__ == "__main__":
    reponse = envoyer_requete(HOTE, PORT, CHEMIN)
    statut, entetes, contenu = separer_reponse(reponse)

    # "HTTP/1.1 200 OK" -> ["HTTP/1.1", "200", "OK"]
    if statut.split()[1] != "200":
        print("Erreur :", statut)
        raise SystemExit(1)

    os.makedirs(DOSSIER, exist_ok=True)
    nom = os.path.join(DOSSIER, os.path.basename(CHEMIN))
    with open(nom, "wb") as fichier:
        fichier.write(contenu)

    print("Fichier téléchargé :", nom, f"({len(contenu)} octets)")