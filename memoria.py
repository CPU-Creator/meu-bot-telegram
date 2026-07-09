import os
import sqlite3
from typing import Optional

DB_PATH = "promocoes.db"


def criar_banco() -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id TEXT PRIMARY KEY,
            titulo TEXT,
            preco REAL,
            desconto INTEGER,
            score INTEGER,
            publicado INTEGER,
            origem TEXT,
            termo TEXT,
            busca_ts INTEGER
        )
        """
    )
    # garantir colunas novas em bancos existentes
    cursor.execute("PRAGMA table_info(produtos)")
    cols = {row[1] for row in cursor.fetchall()}
    if "origem" not in cols:
        cursor.execute("ALTER TABLE produtos ADD COLUMN origem TEXT")
    if "termo" not in cols:
        cursor.execute("ALTER TABLE produtos ADD COLUMN termo TEXT")
    if "busca_ts" not in cols:
        cursor.execute("ALTER TABLE produtos ADD COLUMN busca_ts INTEGER")
    # criar tabela de métricas agregadas por data/termo/origem
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS metricas_busca (
            date TEXT,
            termo TEXT,
            origem TEXT,
            coletados INTEGER DEFAULT 0,
            publicados INTEGER DEFAULT 0,
            PRIMARY KEY (date, termo, origem)
        )
        """
    )
    conn.commit()
    conn.close()


def produto_existe(produto_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM produtos WHERE id = ?", (str(produto_id),))
    existe = cursor.fetchone() is not None
    conn.close()
    return existe


def salvar_produto(
    produto_id: str,
    titulo: str,
    preco: float,
    desconto: int,
    score: int,
    publicado: int,
    origem: Optional[str] = None,
    termo: Optional[str] = None,
    busca_ts: Optional[int] = None,
) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO produtos (id, titulo, preco, desconto, score, publicado, origem, termo, busca_ts)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(produto_id),
            titulo,
            preco,
            desconto,
            score,
            publicado,
            origem,
            termo,
            busca_ts,
        ),
    )
    conn.commit()
    conn.close()


def incrementar_metricas(
    termo: str,
    origem: str,
    coletados_inc: int = 0,
    publicados_inc: int = 0,
    data: Optional[str] = None,
) -> None:
    """Incremente métricas agregadas por dia, termo e origem."""
    if data is None:
        import time as _time

        data = _time.strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO metricas_busca (date, termo, origem, coletados, publicados)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(date, termo, origem) DO UPDATE SET
                coletados = coletados + excluded.coletados,
                publicados = publicados + excluded.publicados
            """,
            (data, termo, origem, int(coletados_inc), int(publicados_inc)),
        )
    except Exception:
        # fallback: ler e atualizar manualmente (compatibilidade)
        cursor.execute(
            "SELECT coletados, publicados FROM metricas_busca WHERE date = ? AND termo = ? AND origem = ?",
            (data, termo, origem),
        )
        row = cursor.fetchone()
        if row:
            coletados = row[0] + int(coletados_inc)
            publicados = row[1] + int(publicados_inc)
            cursor.execute(
                "UPDATE metricas_busca SET coletados = ?, publicados = ? WHERE date = ? AND termo = ? AND origem = ?",
                (coletados, publicados, data, termo, origem),
            )
        else:
            cursor.execute(
                "INSERT INTO metricas_busca (date, termo, origem, coletados, publicados) VALUES (?, ?, ?, ?, ?)",
                (data, termo, origem, int(coletados_inc), int(publicados_inc)),
            )
    conn.commit()
    conn.close()


def obter_metricas(data: Optional[str] = None, termo: Optional[str] = None, origem: Optional[str] = None):
    """Retorna métricas agregadas para a data (YYYY-MM-DD). Filtra por termo e/ou origem quando informados."""
    if data is None:
        import time as _time

        data = _time.strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "SELECT date, termo, origem, coletados, publicados FROM metricas_busca WHERE date = ?"
    params = [data]
    if termo:
        query += " AND termo = ?"
        params.append(termo)
    if origem:
        query += " AND origem = ?"
        params.append(origem)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows
