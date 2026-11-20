import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flasgger import Swagger, swag_from

app = Flask(__name__)

# Configuración de Base de Datos (usando instance/datos.db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 1. CONFIGURACIÓN DE CORS (Lista Blanca + Preflight)
origenes_permitidos = os.getenv(
    "CORS_ORIGINS", 
    "http://localhost:5000,http://127.0.0.1:5500"
).split(",")

CORS(
    app,
    resources={r"/api/*": {"origins": origenes_permitidos}},
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=600
)

# 2. CONFIGURACIÓN DE SWAGGER / OPENAPI 3.0.3
swagger_config = {
    "headers": [],
    "openapi": "3.0.3",
    "specs": [
        {
            "endpoint": 'openapi',
            "route": '/openapi.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
}

swagger_template = {
    "openapi": "3.0.3",
    "info": {
        "title": "API de Tareas - Proyecto Web",
        "version": "1.0.0",
        "description": "API REST documentada con OpenAPI 3.0.3 y protegida con CORS"
    },
    "servers": [
        {"url": "http://localhost:3000", "description": "Servidor de Desarrollo"}
    ],
    "components": {
        "schemas": {
            "Tarea": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "example": 1},
                    "titulo": {"type": "string", "example": "Implementar CORS en Flask"},
                    "hecha": {"type": "boolean", "example": False}
                }
            },
            "NuevaTarea": {
                "type": "object",
                "required": ["titulo"],
                "properties": {
                    "titulo": {"type": "string", "example": "Probar Swagger UI"}
                }
            }
        }
    }
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# --- MODELO DE BASE DE DATOS ---
class Tarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    hecha = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {"id": self.id, "titulo": self.titulo, "hecha": self.hecha}

with app.app_context():
    db.create_all()
    if Tarea.query.count() <= 1:
        tareas_iniciales = [
            Tarea(titulo="Configurar lista blanca de orígenes en Flask-CORS", hecha=True),
            Tarea(titulo="Documentar contratos y esquemas con OpenAPI 3.0.3", hecha=True),
            Tarea(titulo="Inspeccionar petición preflight OPTIONS en DevTools (F12)", hecha=False),
            Tarea(titulo="Validar bloqueo de origen no autorizado en puerto 5001", hecha=False),
            Tarea(titulo="Ejecutar pruebas de contrato automatizadas en Cypress", hecha=False),
        ]
        db.session.bulk_save_objects(tareas_iniciales)
        db.session.commit()

# --- ESPECIFICACIONES SWAGGER EN PYTHON PURO ---
spec_listar = {
    "tags": ["Tareas"],
    "summary": "Listar todas las tareas",
    "responses": {
        "200": {
            "description": "Lista de tareas obtenida con éxito",
            "content": {
                "application/json": {
                    "schema": {"type": "array", "items": {"$ref": "#/components/schemas/Tarea"}}
                }
            }
        }
    }
}

spec_crear = {
    "tags": ["Tareas"],
    "summary": "Crear una nueva tarea (Dispara Preflight OPTIONS)",
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/NuevaTarea"}
            }
        }
    },
    "responses": {
        "201": {
            "description": "Tarea creada exitosamente",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/Tarea"}
                }
            }
        },
        "400": {"description": "Error de validación (título vacío o faltante)"}
    }
}

spec_eliminar = {
    "tags": ["Tareas"],
    "summary": "Eliminar una tarea por ID",
    "parameters": [
        {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}
    ],
    "responses": {
        "200": {"description": "Tarea eliminada"},
        "404": {"description": "Tarea no encontrada"}
    }
}

spec_db = {
    "tags": ["Base de Datos"],
    "summary": "Inspeccionar todas las tablas, columnas y registros de SQLite",
    "responses": {
        "200": {"description": "Información completa de todas las tablas y registros en SQLite"}
    }
}

# --- ENDPOINTS DE LA API ---

@app.route('/api/tareas', methods=['GET'])
@swag_from(spec_listar)
def listar_tareas():
    tareas = Tarea.query.all()
    return jsonify([t.to_dict() for t in tareas]), 200


@app.route('/api/tareas', methods=['POST'])
@swag_from(spec_crear)
def crear_tarea():
    datos = request.get_json(silent=True) or {}
    titulo = datos.get('titulo', '').strip()
    
    if not titulo:
        return jsonify({"error": "El campo 'titulo' es obligatorio"}), 400
        
    nueva = Tarea(titulo=titulo)
    db.session.add(nueva)
    db.session.commit()
    return jsonify(nueva.to_dict()), 201


@app.route('/api/tareas/<int:id>', methods=['DELETE'])
@swag_from(spec_eliminar)
def eliminar_tarea(id):
    tarea = db.session.get(Tarea, id)
    if not tarea:
        return jsonify({"error": "Tarea no encontrada"}), 404
        
    db.session.delete(tarea)
    db.session.commit()
    return jsonify({"mensaje": "Tarea eliminada correctamente"}), 200


@app.route('/api/db-info', methods=['GET'])
@swag_from(spec_db)
def info_base_datos():
    inspector = db.inspect(db.engine)
    tablas_nombres = inspector.get_table_names()
    tablas_completas = {}

    for tabla in tablas_nombres:
        columnas = [
            {"nombre": c["name"], "tipo": str(c["type"]), "pk": bool(c.get("primary_key"))}
            for c in inspector.get_columns(tabla)
        ]
        resultado = db.session.execute(db.text(f'SELECT * FROM "{tabla}"'))
        filas = [dict(row._mapping) for row in resultado]
        
        tablas_completas[tabla] = {
            "columnas": columnas,
            "total": len(filas),
            "registros": filas
        }

    return jsonify({
        "motor": "SQLite",
        "archivo": "instance/datos.db",
        "total_tablas": len(tablas_nombres),
        "tablas": tablas_completas
    }), 200


if __name__ == '__main__':
    app.run(port=3000, debug=True)