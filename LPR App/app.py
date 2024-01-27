from flask import Flask, render_template, redirect, url_for, flash, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from PIL import Image
import io
import os
from flask import jsonify
import cv2
from matplotlib import pyplot as plt
import numpy as np
import imutils
import easyocr
import base64
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    matriculation = db.Column(db.String(100), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to access that page.', 'error')
    return redirect(url_for('login'))

# Routes
@app.route('/')
@login_required
def home():
    return 'Welcome to the Flask app!'
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        matriculation = request.form['matriculation']

        user = User.query.filter_by(username=username).first()

        if user:
            flash('Username already exists.', 'error')
        else:
            new_user = User(username=username, password=password, matriculation=matriculation)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect("/app")
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/app')
@login_required
def protected():
    return render_template("index.html")


@app.route('/upload', methods=['POST'])
@login_required
def upload_image():
    # Récupérer l'image téléchargée depuis le formulaire
    cropped_image = request.form['image']
    cropped_image_data = cropped_image.replace('data:image/png;base64,', '')
    cropped_image_bytes = io.BytesIO(base64.b64decode(cropped_image_data))
    image = Image.open(cropped_image_bytes)
    
    # Convertir l'image en niveaux de gris
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    gray_image = Image.fromarray(gray)
    
    # Convertir l'image en base64
    buffered = io.BytesIO()
    gray_image.save(buffered, format="JPEG")
    gray_image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # Réduire le bruit
    bfilter = cv2.bilateralFilter(gray, 11, 17, 17)

    # Détection des contours
    edged = cv2.Canny(bfilter, 30, 200)

    # Conversion des couleurs pour l'affichage
    edged_rgb = cv2.cvtColor(edged, cv2.COLOR_BGR2RGB)

    # Encodage de l'image en base64
    _, edged_buffer = cv2.imencode('.png', edged_rgb)
    edged_base64 = base64.b64encode(edged_buffer).decode('utf-8')


    keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(keypoints)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    location = None
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 10, True)
        if len(approx) == 4:
            location = approx
            break
    # mask = np.zeros(gray.shape, np.uint8)
    image = np.array(image)
    mask = np.zeros(image.shape[:2], dtype=np.uint8)

    new_image = cv2.drawContours(mask, [location], 0, 255, -1)
    new_image = cv2.bitwise_and(image, image, mask=mask)
    retval, buffer = cv2.imencode('.png', new_image)
    new_image_base64 = base64.b64encode(buffer).decode('utf-8')
    (x,y) = np.where(mask==255)
    (x1, y1) = (np.min(x), np.min(y))
    (x2, y2) = (np.max(x), np.max(y))
    cropped_image = gray[x1:x2+1, y1:y2+1]
    retval, buffer = cv2.imencode('.png', cropped_image)
    cropped_image_base64 = base64.b64encode(buffer).decode('utf-8')
    reader = easyocr.Reader(['en'])
    result = reader.readtext(cropped_image)
    if len(result) > 0:
        text = result[0][-2]
        response = {
            'status': 'success',
            'text': text,
           
        }
    else:
    # Gérer le cas où la liste result est vide
        text = "Aucun élément trouvé dans la liste result" 
        response = {
            'status': 'error',
            'text': text,
            
        }

    font = cv2.FONT_HERSHEY_SIMPLEX
    res = cv2.putText(image, text=text, org=(approx[0][0][0], approx[1][0][1]+60), fontFace=font, fontScale=1, color=(0,255,0), thickness=2, lineType=cv2.LINE_AA)
    res = cv2.rectangle(image, tuple(approx[0][0]), tuple(approx[2][0]), (0,255,0),3)
    retval, buffer = cv2.imencode('.png', res)
    res_base64 = base64.b64encode(buffer).decode('utf-8')
    print(text)
    for detection in result:
        text = detection[1]
        confidence = "{:.3f}".format(detection[2])
        #print(f"Texte détecté : {text} (Confiance : {confidence})")
    #print(new_image.shape)
    #return render_template('index.html', gray_image=gray_image_base64)
    
    return jsonify({'gray_image': gray_image_base64,'edged_image': edged_base64,'new_image':cropped_image_base64,'res':res_base64,'text':text,'confidence':confidence})
    





if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("cheque")
        if not User.query.filter_by(username='admin').first():
            print("Default user not exist !\nCreating defaulte user ..")
            default_user = User(username='admin', password='password' ,matriculation="test")
            db.session.add(default_user)
            db.session.commit()
            print("Donne.")
    app.run(debug=True)
