from flask import Flask, request, render_template, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
import string
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont



application = Flask(__name__, static_url_path="/static")
#data base

application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lista.sqlite3"
db = SQLAlchemy(application)

class FormData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    nik = db.Column(db.String(100), nullable=False, default=None)
    client_id = db.Column(db.String(100), nullable=False)


    

with application.app_context():
    db.create_all()

#index.html
@application.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        client_id = request.form.get("id")

        img = Image.open("static/imagem/certificado.png")
        draw = ImageDraw.Draw(img)

        font = ImageFont.truetype("arial.ttf", 32)

        draw.text((100, 100), "Name: " + name, (0,0,0), font=font)
        draw.text((100, 200), "ID: " + client_id, (0,0,0), font=font)

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        return send_file(buffer, attachment_filename='static/imagem/certificado.png', mimetype='image/png')

    return render_template("index.html")


@application.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        nik = request.form.get("nik")
        client_id = request.form.get("id")
        data = FormData(name=name, phone=phone, email=email, nik=nik, client_id=client_id)
        db.session.add(data)
        db.session.commit()

        # Cria o certificado
        file_path = f"certificados/certificado_{client_id}.png"
        if not os.path.exists(file_path):
            with Image.open("static/imagem/certificado.png") as image:
                draw = ImageDraw.Draw(image)
                font = ImageFont.truetype("arial.ttf", size=50)
                font1 = ImageFont.truetype("arial.ttf", size=80)
                draw.text((550, 800), f"{nik}", fill=(255, 255, 255), font=font)
                draw.text((550, 675), f" {client_id} ", fill=(255, 215, 0), font=font1)
                image.save(file_path)


        # Download do certificado
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            abort(404)

    return render_template("form.html")


@application.route("/lista")
def list():
    data = FormData.query.with_entities(FormData.id, FormData.name, FormData.phone, FormData.email, FormData.nik, FormData.client_id).all()
    return render_template("lista.html", data=data)




@application.route("/download/<client_id>")
def download(client_id):
    file_path = f"certificados/certificado_{client_id}.png"
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        abort(404)


if __name__ == "__main__":
    application.run(debug=True)