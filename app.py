from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "chamados.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chamados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            solicitante TEXT NOT NULL,
            categoria TEXT NOT NULL,
            prioridade TEXT NOT NULL,
            descricao TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Aberto',
            criado_em TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    conn = get_connection()
    chamados = conn.execute("SELECT * FROM chamados ORDER BY id DESC").fetchall()
    total = conn.execute("SELECT COUNT(*) total FROM chamados").fetchone()["total"]
    abertos = conn.execute("SELECT COUNT(*) total FROM chamados WHERE status='Aberto'").fetchone()["total"]
    andamento = conn.execute("SELECT COUNT(*) total FROM chamados WHERE status='Em andamento'").fetchone()["total"]
    resolvidos = conn.execute("SELECT COUNT(*) total FROM chamados WHERE status='Resolvido'").fetchone()["total"]
    conn.close()
    return render_template("index.html", chamados=chamados, total=total, abertos=abertos, andamento=andamento, resolvidos=resolvidos)


@app.route("/novo", methods=["GET", "POST"])
def novo_chamado():
    if request.method == "POST":
        solicitante = request.form["solicitante"]
        categoria = request.form["categoria"]
        prioridade = request.form["prioridade"]
        descricao = request.form["descricao"]
        criado_em = datetime.now().strftime("%d/%m/%Y %H:%M")

        conn = get_connection()
        conn.execute(
            "INSERT INTO chamados (solicitante, categoria, prioridade, descricao, criado_em) VALUES (?, ?, ?, ?, ?)",
            (solicitante, categoria, prioridade, descricao, criado_em)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("novo.html")


@app.route("/atualizar/<int:id>", methods=["POST"])
def atualizar_status(id):
    novo_status = request.form["status"]
    conn = get_connection()
    conn.execute("UPDATE chamados SET status=? WHERE id=?", (novo_status, id))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
