# 🛒 E-Shop Brasil — Gestão de Dados com MongoDB, Docker e Streamlit

Projeto prático da disciplina **Advanced Databases and Big Data** (UniFECAF).

## 1. Introdução

A **E-Shop Brasil** é uma das maiores plataformas de comércio eletrônico do país, com mais de **5 milhões de clientes ativos** e cerca de **100 mil pedidos por dia**. Com esse volume, a empresa enfrenta desafios de:

- **Gestão de dados:** armazenar e analisar grandes volumes de dados de clientes e pedidos, protegendo informações pessoais conforme a **LGPD**;
- **Personalização:** usar o histórico de compras para recomendações;
- **Logística:** acompanhar pedidos e faturamento por região para melhorar prazos e entregas, principalmente em regiões distantes.

**Objetivo:** desenvolver uma aplicação funcional, em ambiente Dockerizado, que usa **MongoDB (NoSQL)** para simular a gestão e a análise de grandes volumes de dados da empresa, com uma interface gráfica em **Streamlit**.

### Por que MongoDB?

- **Esquema flexível:** pedidos e clientes podem ganhar novos campos sem alterar tabelas.
- **Documentos:** cada registro é um documento (JSON), natural para dados semi-estruturados do e-commerce.
- **Escalabilidade:** suporta réplicas e sharding para crescer junto com o volume de dados.
- **Aggregation Framework:** permite análises (agrupar, somar, juntar coleções) direto no banco.

## 2. Tecnologias utilizadas

| Tecnologia | Uso no projeto |
|---|---|
| **Docker / Docker Compose** | Ambiente reproduzível: sobe o banco e o app com um comando |
| **MongoDB 7** | Banco de dados NoSQL orientado a documentos |
| **Streamlit** | Interface web em Python para manipular e visualizar os dados |
| **PyMongo** | Conexão do Python com o MongoDB |
| **Pandas** | Manipulação e concatenação de dados |
| **Faker (pt_BR)** | Geração de dados falsos realistas |

## 3. Descrição da aplicação

O banco `eshop_brasil` possui as coleções `clientes` e `pedidos`:

```
clientes: nome, email, cidade, estado
pedidos : cliente_id, estado, valor, status (entregue | em transporte | cancelado)
```

### Inserção de dados no MongoDB
- **Dados falsos:** gera clientes com o Faker e pedidos ligados a clientes existentes, em lote (`insert_many`).
- **Importação de CSV:** envia um arquivo (ex.: dataset do Kaggle) e grava no MongoDB.

### Edição e exclusão
- **Clientes:** seleção de um cliente, edição de campos (`update_one` + `$set`) e exclusão (`delete_one`).
- **Pedidos:** edição de status e valor, e exclusão de pedidos individuais.
- A listagem é limitada a 100 documentos para manter a interface rápida.

### Manipulação e concatenação de dados
- **Empilhamento (`pd.concat`):** une os clientes do banco com um CSV enviado e salva o resultado em uma nova coleção.
- **Junção (`$lookup`):** une `pedidos` com `clientes` (equivalente a um JOIN do SQL), exibindo o nome e a cidade do cliente em cada pedido.

### Consultas e exibição na interface gráfica
- Clientes por estado
- Faturamento por estado (desconsiderando pedidos cancelados)
- Pedidos por status
- Busca de clientes por estado

Os resultados aparecem em tabelas e gráficos de barras, usando pipelines de agregação (`$match`, `$group`, `$sort`).

## 4. Comandos para execução

**Pré-requisito:** Docker instalado (ou um GitHub Codespace, que já vem com Docker).

```bash
# 1. Clonar o repositório
git clone https://github.com/mMarceloH/E-shopBR.git
cd E-shopBR

# 2. Subir o MongoDB e a aplicação
docker compose up --build
```

> Em versões antigas do Docker, use `docker-compose up --build`.

Depois, acesse **http://localhost:8501**.

- **No GitHub Codespaces:** abra a aba **Portas**, localize a porta **8501** e clique em **Abrir no navegador**.
- Para parar: `Ctrl + C` e depois `docker compose down`.
- Para apagar também os dados do banco: `docker compose down -v`.

### Alternativa: `docker build` + `docker run`

```bash
docker network create eshop-net
docker run -d --name mongo --network eshop-net -p 27017:27017 mongo:7
docker build -t eshop-app .
docker run -d --name eshop-app --network eshop-net -p 8501:8501 \
  -e MONGO_URI=mongodb://mongo:27017 eshop-app
```

### Execução do `app.py` no Streamlit (sem container para o app)

```bash
docker run -d --name mongo -p 27017:27017 mongo:7
pip install -r requirements.txt
streamlit run app.py
```

A aplicação lê o endereço do banco pela variável de ambiente `MONGO_URI` (padrão: `mongodb://localhost:27017`).

## 5. Testes e exemplos

Roteiro para testar a aplicação:

1. Na aba **Inserir**, gere clientes falsos e depois pedidos falsos.
2. Em **Consultas**, veja clientes por estado, faturamento por estado e pedidos por status.
3. Em **Editar/Excluir**, altere o nome de um cliente, mude o status de um pedido e exclua um registro.
4. Em **Concatenar**, empilhe um CSV com os clientes e execute a junção `$lookup`.


| Funcionalidade | Exemplo |
|---|---|
| Inserção de dados | ![Inserção](exemplos/01-insercao.png) |
| Consultas e gráficos | ![Consultas](exemplos/02-consultas.png) |
| Edição e exclusão | ![Edição](exemplos/03-edicao-exclusao.png) |
| Concatenação | ![Concatenação](exemplos/04-concatenacao.png) |

## 6. Impacto no negócio

- **Personalização:** o histórico de pedidos por cliente é a base para recomendações.
- **Logística:** o faturamento e os pedidos por estado mostram onde a operação concentra demanda e onde investir em centros de distribuição.
- **Escalabilidade:** a modelagem em documentos permite evoluir para um cluster MongoDB com sharding e integrar ferramentas de Big Data, como Spark.