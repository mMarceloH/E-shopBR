import os
import random
import pandas as pd
import streamlit as st
from faker import Faker
from pymongo import MongoClient

fake = Faker("pt_BR")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
db = MongoClient(MONGO_URI)["eshop_brasil"]

st.title("🛒 E-Shop Brasil")
pagina = st.sidebar.radio("Menu", ["Inserir", "Editar/Excluir", "Concatenar", "Consultas"])
if pagina == "Inserir":
    st.header("Inserir dados")

    qtd = st.number_input("Quantidade de clientes", 1, 10000, 100)
    if st.button("Gerar clientes falsos"):
        clientes = [{
            "nome": fake.name(),
            "email": fake.email(),
            "cidade": fake.city(),
            "estado": fake.estado_sigla(),
        } for _ in range(int(qtd))]
        db.clientes.insert_many(clientes)
        st.success(f"{qtd} clientes inseridos!")

    st.subheader("Importar CSV (ex.: Kaggle)")
    arq = st.file_uploader("Arquivo CSV", type="csv")
    if arq:
        df = pd.read_csv(arq)
        st.dataframe(df.head())
        if st.button("Importar para o MongoDB"):
            db.dados_csv.insert_many(df.to_dict("records"))
            st.success("CSV importado!")
elif pagina == "Editar/Excluir":
    st.header("Editar ou excluir cliente")
    docs = list(db.clientes.find().limit(100))

    if not docs:
        st.info("Nenhum cliente. Insira dados primeiro.")
    else:
        opcoes = {f"{d['nome']} ({d['email']})": d["_id"] for d in docs}
        escolhido = st.selectbox("Cliente", list(opcoes))
        _id = opcoes[escolhido]
        doc = db.clientes.find_one({"_id": _id})

        novo_nome = st.text_input("Nome", doc["nome"])
        nova_cidade = st.text_input("Cidade", doc["cidade"])

        c1, c2 = st.columns(2)
        if c1.button("💾 Salvar"):
            db.clientes.update_one({"_id": _id},
                                   {"$set": {"nome": novo_nome, "cidade": nova_cidade}})
            st.success("Atualizado!")
        if c2.button("🗑️ Excluir"):
            db.clientes.delete_one({"_id": _id})
            st.rerun()            
elif pagina == "Concatenar":
    st.header("Concatenação de dados")

    st.subheader("A) Empilhar coleção + CSV")
    arq = st.file_uploader("CSV para concatenar", type="csv", key="concat")
    if arq:
        df_banco = pd.DataFrame(list(db.clientes.find({}, {"_id": 0})))
        df_csv = pd.read_csv(arq)
        df_final = pd.concat([df_banco, df_csv], ignore_index=True)
        st.write(f"{len(df_banco)} do banco + {len(df_csv)} do CSV = {len(df_final)} linhas")
        st.dataframe(df_final.head(50))
        if st.button("Salvar em 'clientes_concatenado'"):
            db.clientes_concatenado.drop()
            db.clientes_concatenado.insert_many(df_final.to_dict("records"))
            st.success("Salvo!")
elif pagina == "Consultas":
    st.header("Consultas")
    consulta = st.selectbox("Escolha", [
        "Clientes por estado",
        "Faturamento por estado",
        "Pedidos por status",
        "Busca de clientes",
    ])

    if consulta == "Clientes por estado":
        df = pd.DataFrame(list(db.clientes.aggregate([
            {"$group": {"_id": "$estado", "total": {"$sum": 1}}},
            {"$sort": {"total": -1}},
        ]))).rename(columns={"_id": "estado"})
        st.bar_chart(df.set_index("estado")["total"])
        st.dataframe(df)

    elif consulta == "Faturamento por estado":
        df = pd.DataFrame(list(db.pedidos.aggregate([
            {"$match": {"status": {"$ne": "cancelado"}}},
            {"$group": {"_id": "$estado", "faturamento": {"$sum": "$valor"}}},
            {"$sort": {"faturamento": -1}},
        ]))).rename(columns={"_id": "estado"})
        st.bar_chart(df.set_index("estado")["faturamento"])
        st.dataframe(df)

    elif consulta == "Pedidos por status":
        df = pd.DataFrame(list(db.pedidos.aggregate([
            {"$group": {"_id": "$status", "total": {"$sum": 1}}},
        ]))).rename(columns={"_id": "status"})
        st.bar_chart(df.set_index("status")["total"])

    else:
        uf = st.text_input("Estado (ex.: SP)").upper()
        if uf:
            df = pd.DataFrame(list(db.clientes.find({"estado": uf}, {"_id": 0}).limit(200)))
            st.dataframe(df)            