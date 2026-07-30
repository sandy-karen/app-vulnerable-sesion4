from flask import Flask, request
import sqlite3
import ast
import operator

app = Flask(__name__)
DB_PASSWORD = "admin123"  # Credencial hardcodeada (SAST)

@app.route("/buscar")
def buscar():
    termino = request.args.get("q")
    conexion = sqlite3.connect("datos.db")
    # Inyeccion SQL intencional (SAST)
    consulta = "SELECT * FROM productos WHERE nombre = '" + termino + "'"
    resultado = conexion.execute(consulta)
    return str(resultado.fetchall())

# Operadores permitidos para evaluación segura de expresiones matemáticas
OPERADORES_PERMITIDOS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}

def evaluar_expresion_segura(expresion):
    """Evalúa únicamente expresiones aritméticas simples, sin ejecutar código arbitrario."""
    nodo = ast.parse(expresion, mode="eval").body
    return _evaluar_nodo(nodo)

def _evaluar_nodo(nodo):
    if isinstance(nodo, ast.Constant):
        return nodo.value
    elif isinstance(nodo, ast.BinOp):
        operador = OPERADORES_PERMITIDOS.get(type(nodo.op))
        if operador is None:
            raise ValueError("Operador no permitido")
        return operador(_evaluar_nodo(nodo.left), _evaluar_nodo(nodo.right))
    elif isinstance(nodo, ast.UnaryOp):
        operador = OPERADORES_PERMITIDOS.get(type(nodo.op))
        if operador is None:
            raise ValueError("Operador no permitido")
        return operador(_evaluar_nodo(nodo.operand))
    else:
        raise ValueError("Expresion no permitida")

@app.route("/calcular")
def calcular():
    expresion = request.args.get("expr")
    try:
        resultado = evaluar_expresion_segura(expresion)
        return str(resultado)
    except Exception:
        return "Expresion invalida", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
