from flask import Flask, jsonify, Response
import pandas as pd
import sqlite3
import os

app = Flask(__name__)

def getId():
    conn = sqlite3.connect('projeto_integrador.db')
    strSQL = "SELECT idGenero, nomeGenero FROM 'Genero'"
    df_id = pd.read_sql(strSQL, conn)
    conn.close()
    return df_id

def getAno():
    conn = sqlite3.connect('projeto_integrador.db')
    strSQL = "SELECT * FROM 'Ano'"
    df_ano = pd.read_sql(strSQL, conn)
    conn.close()
    return df_ano

def getData():
    conn = sqlite3.connect('projeto_integrador.db')
    strSQL = "SELECT * FROM 'Data'"
    df_data = pd.read_sql(strSQL, conn)
    conn.close()
    return df_data

def getGenero():
    conn = sqlite3.connect('projeto_integrador.db')
    strSQL = "SELECT * FROM 'Genero'"
    df_genero = pd.read_sql(strSQL, conn)
    conn.close()
    return df_genero

def getIdioma():
    conn = sqlite3.connect('projeto_integrador.db')
    strSQL = "SELECT * FROM 'Idioma'"
    df_idioma = pd.read_sql(strSQL, conn)
    conn.close()
    return df_idioma

@app.route('/', methods=['GET'])
def index():
    df_id = getId()
    return Response(df_id.to_json(orient = 'records'), mimetype = 'application/json')

@app.route('/ano', methods=['GET'])
def obter_anos():
    df_ano = getAno()
    return Response(df_ano.to_json(orient = 'records'), mimetype = 'application/json')

@app.route('/data', methods=['GET'])
def obter_datas():
    df_data = getData()
    return Response(df_data.to_json(orient = 'records'), mimetype = 'application/json')

@app.route('/genero', methods=['GET'])
def obter_generos():
    df_genero = getGenero()
    return Response(df_genero.to_json(orient = 'records'), mimetype = 'application/json')

@app.route('/idioma', methods=['GET'])
def obter_idiomas():
    df_idioma = getIdioma()
    return Response(df_idioma.to_json(orient = 'records'), mimetype = 'application/json')

if __name__ == '__main__':
    app.run(debug = True)