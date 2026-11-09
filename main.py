from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/saludo", methods=["GET"])
def saludo():
    return jsonify({"mensaje": "¡Hola desde Flask!"})

@app.route("/api/productos", methods=["POST"])  # ← Sin la "k"
def listar_productos():
    productos = [
        {"id": 1, "nombre": "Teclado"},
        {"id": 2, "nombre": "Mouse"}
    ]
    return jsonify(productos)
@app.route("/api/tareas", methods=["GET"])  # ← Sin la "k"
def listar_tareas():
    tareas = [
        {"id": 1, "titulo": "materiaUno", "completada": True},
        {"id": 2, "titulo": "Mouse"},
        {"id": 3, "titulo": "Teclado"}
    ]

if __name__ == "__main__":
    app.run(debug=True, port=5000)