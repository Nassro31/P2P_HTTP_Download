# Serveur HTTP — basé sur l'exemple serveur du cours
import mimetypes
import os
import socket

DOSSIER = "test_files"
PORT = 9000


def reponse_http(conn, code, contenu, type_contenu="text/plain"):
    entetes = (
        f"HTTP/1.1 {code}\r\n"
        f"Content-Type: {type_contenu}\r\n"
        f"Content-Length: {len(contenu)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    conn.sendall(entetes.encode("ascii") + contenu)


def traiter_requete(conn, requete):
    # première ligne : "GET /gros.bin HTTP/1.1"
    premiere_ligne = requete.split(b"\r\n")[0].decode("ascii", errors="replace")
    morceaux = premiere_ligne.split()
    if len(morceaux) != 3:
        reponse_http(conn, "400 Bad Request", b"Requete invalide\n")
        return

    methode, chemin, version = morceaux
    if methode != "GET":
        reponse_http(conn, "405 Method Not Allowed", b"Methode non geree\n")
        return

    # sécurité : interdit de sortir du dossier partagé
    if ".." in chemin:
        reponse_http(conn, "403 Forbidden", b"Acces interdit\n")
        return

    fichier = os.path.join(DOSSIER, chemin.lstrip("/"))
    if not os.path.isfile(fichier):
        reponse_http(conn, "404 Not Found", b"Fichier introuvable\n")
        return

    with open(fichier, "rb") as f:
        contenu = f.read()
    type_contenu = mimetypes.guess_type(fichier)[0] or "application/octet-stream"
    reponse_http(conn, "200 OK", contenu, type_contenu)


if __name__ == '__main__':
    # Etape 1 : création de la socket d'écoute
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ecoute:
        ecoute.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Etape 1 suite : liaison de la socket d'écoute (choix du port)
        ecoute.bind(('', PORT))
        # Etape 2 : ouverture du service
        ecoute.listen()
        print(f"Serveur en écoute sur le port {PORT}")
        try:
            while True:
                # Etape 3 : attente et acceptation d'une nouvelle connexion
                service, addr = ecoute.accept()
                with service:
                    print('Connecté à ', addr)
                    # Etape 4 : lecture de la requête jusqu'à la fin des en-têtes
                    requete = b""
                    while b"\r\n\r\n" not in requete:
                        data = service.recv(1024)
                        if not data:
                            break
                        requete += data
                    print(requete.split(b"\r\n")[0].decode("ascii", errors="replace"))
                    # Etape 4 suite : réponse HTTP avec le fichier demandé
                    traiter_requete(service, requete)
        except KeyboardInterrupt:
            print("\nArrêt du serveur")