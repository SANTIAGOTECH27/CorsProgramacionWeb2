from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__, instance_relative_config=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'datos.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
os.makedirs(app.instance_path, exist_ok=True)

db = SQLAlchemy(app)

# Tabla Producto
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    precio = db.Column(db.Float, nullable=False)

# Tabla Estudiante (¡ASEGÚRATE QUE ESTÉ AQUÍ!)
class Estudiante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    edad = db.Column(db.Integer, nullable=False)

# Rutas...
@app.route("/api/productos", methods=["GET"])
def listar_productos2():
    productos = Producto.query.all()
    return jsonify([{"id": p.id, "nombre": p.nombre, "precio": p.precio} for p in productos])

@app.route("/api/estudiantes", methods=["GET"])
def listar_estudiantes():
    estudiantes = Estudiante.query.all()
    return jsonify([{"id": e.id, "nombre": e.nombre, "apellido": e.apellido, "edad": e.edad} for e in estudiantes])

# Crear tablas
with app.app_context():
    db.create_all()
    
    if Producto.query.count() == 0:
        db.session.add(Producto(nombre="Teclado", precio=39.99))
        db.session.commit()
    
    if Estudiante.query.count() == 0:
        db.session.add(Estudiante(nombre="Juan", apellido="Pérez", edad=20))
        db.session.commit()
        print("✅ Tabla Estudiante creada")

if __name__ == "__main__":
    app.run(debug=True, port=5000)