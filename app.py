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