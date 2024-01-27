import os
import glob


directory_path ='D:/M1 S2/ML/LPR Project Nadia/Numb_plate_imgs'

# liste de tous les fichiers à l'intérieure de 'Numb_plate_imgs'
all_files = glob.glob(os.path.join(directory_path, '*'))

# la suppressionles fichiers qui ont l'extension différente de .png ou .jpg
for file in all_files:
    if not file.endswith(('.png', '.jpg')):
        os.remove(file)

files = os.listdir(directory_path)
num_files = len(files)
print("le nombre de fichier dans le dossier est :",num_files)