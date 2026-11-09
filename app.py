from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flasgger import Swagger
import os
import hashlib
import json
import time

app = Flask(__name__, instance_relative_config=True)

# ==========================================
# CONFIGURACIÓN DE CORS Y SWAGGER
# ==========================================
CORS(app)
swagger = Swagger(app, template={
    "info": {
        "title": "API de Productos y Estudiantes",
        "description": "API REST con integración a SQLite, sistema de caché y CORS.",
        "version": "1.0.0"
    }
})

# ==========================================
# CONFIGURACIÓN DE BASE DE DATOS
# ==========================================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'datos.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
os.makedirs(app.instance_path, exist_ok=True)

db = SQLAlchemy(app)

# ==========================================
# SESIÓN 8: SISTEMA DE CACHÉ (Cache-Aside)
# ==========================================
cache_store = {}
CACHE_TTL = 60

def obtener_de_cache(key):
    if key in cache_store:
        entrada = cache_store[key]
        if time.time() < entrada['expires']:
            return entrada['data'], entrada['etag']
        else:
            del cache_store[key]
    return None, None

def guardar_en_cache(key, data):
    etag = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
    cache_store[key] = {
        'data': data,
        'etag': etag,
        'expires': time.time() + CACHE_TTL
    }
    return etag

def invalidar_cache(key):
    if key in cache_store:
        del cache_store[key]

# ==========================================
# MODELOS
# ==========================================
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    precio = db.Column(db.Float, nullable=False)

class Estudiante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    edad = db.Column(db.Integer, nullable=False)

# ==========================================
# RUTAS DE PRODUCTOS (CRUD)
# ==========================================
@app.route("/api/productos", methods=["GET"])
def listar_productos():
    """
    Obtener lista de productos
    Retorna todos los productos directamente desde la base de datos (con soporte de caché).
    ---
    tags:
      - Productos
    responses:
      200:
        description: Lista obtenida exitosamente
    """
    cache_key = "productos_lista"
    if_none_match = request.headers.get('If-None-Match')
    datos_cache, etag = obtener_de_cache(cache_key)
    
    if if_none_match and if_none_match == etag:
        return '', 304
    
    if datos_cache:
        respuesta = jsonify(datos_cache)
        respuesta.headers['X-Cache-Status'] = 'HIT'
    else:
        productos = Producto.query.all()
        data = [{"id": p.id, "nombre": p.nombre, "precio": p.precio} for p in productos]
        etag = guardar_en_cache(cache_key, data)
        respuesta = jsonify(data)
        respuesta.headers['X-Cache-Status'] = 'MISS'
    
    respuesta.headers['Cache-Control'] = f'public, max-age={CACHE_TTL}'
    respuesta.headers['ETag'] = etag
    return respuesta

@app.route("/api/productos", methods=["POST"])
def crear_producto():
    """
    Crear un nuevo producto
    Guarda un nuevo producto en la base de datos SQLite.
    ---
    tags:
      - Productos
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            nombre:
              type: string
              example: "Disco Duro NVMe"
            precio:
              type: number
              example: 120.50
    responses:
      201:
        description: Producto creado
    """
    data = request.get_json()
    if not data or 'nombre' not in data or 'precio' not in data:
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    nuevo = Producto(nombre=data['nombre'], precio=data['precio'])
    db.session.add(nuevo)
    db.session.commit()
    
    invalidar_cache("productos_lista")
    return jsonify({"id": nuevo.id, "nombre": nuevo.nombre, "precio": nuevo.precio}), 201

# ==========================================
# RUTAS DE ESTUDIANTES
# ==========================================
@app.route("/api/estudiantes", methods=["GET"])
def listar_estudiantes():
    """
    Obtener lista de estudiantes
    Retorna todos los estudiantes desde la base de datos.
    ---
    tags:
      - Estudiantes
    responses:
      200:
        description: Lista de estudiantes obtenida
    """
    estudiantes = Estudiante.query.all()
    data = [{"id": e.id, "nombre": e.nombre, "apellido": e.apellido, "edad": e.edad} for e in estudiantes]
    return jsonify(data), 200

# ==========================================
# INICIALIZACIÓN
# ==========================================
with app.app_context():
    db.create_all()
    # Datos semilla si la tabla está vacía
    if Producto.query.count() == 0:
        db.session.add(Producto(nombre="Teclado Mecánico", precio=75.0))
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=True, port=5000)