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