import os
import requests
from tqdm import tqdm
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from colorama import Fore, Back, Style
from datetime import datetime

# URL du fichier CRL
crl_url = "https://igc-sante.esante.gouv.fr/CRL/ACI-FO-PP.crl"
# Chemin pour enregistrer le fichier CRL localement
crl_file_path = "ACI-FO-PP.crl"

# Télécharger le fichier CRL avec une barre de progression
print("Telechargement de la liste de révocation ...")
response = requests.get(crl_url, stream=True)
total_size_in_bytes = int(response.headers.get('content-length', 0))
block_size = 1024  # 1 Ko
progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
with open(crl_file_path, "wb") as crl_file:
    for data in response.iter_content(block_size):
        progress_bar.update(len(data))
        crl_file.write(data)
progress_bar.close()

# Lire le fichier CRL
with open(crl_file_path, "rb") as crl_file:
    crl_data = crl_file.read()

# Charger le fichier CRL (en format DER)
crl = x509.load_der_x509_crl(crl_data, default_backend())

# Demander le numéro de série de la carte à l'utilisateur
while True:
    target_serial = input("Veuillez saisir le numero de serie de la carte (en hexadecimal) : ")
    if len(target_serial) != 32:
        print(Fore.RED + "Erreur: Le numéro de série doit avoir une longueur de 32 caractères." + Style.RESET_ALL)
    else:
        break

# Convertir le numéro de série en un entier
target_serial_int = int(target_serial, 16)

# Vérifier si le numéro de série est dans la CRL
found = False
for revoked_cert in crl:
    if revoked_cert.serial_number == target_serial_int:
        found = True
        revocation_date = revoked_cert.revocation_date_utc.strftime("%d/%m/%Y")
        print(Fore.YELLOW + f"Certificat révoqué trouvé : {target_serial}" + Style.RESET_ALL)
        print(Fore.YELLOW + f"Date de révocation : {Fore.GREEN}{revocation_date}" + Style.RESET_ALL)
        break

if not found:
    print(f"Certificat avec le numero de serie {target_serial} n'est pas révoqué.")

# Supprimer le fichier CRL
os.remove(crl_file_path)

# Attendre une action de l'utilisateur avant de terminer
input("Appuyez sur Entrée pour quitter...")
