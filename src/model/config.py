from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Importa a função load_dotenv da biblioteca dotenv para carregar variáveis de ambiente a partir de um arquivo .env
load_dotenv()

# Definição de uma classe de configuração para gerenciar variáveis de ambiente relacionadas à configuração do banco de dados
class Config():
    # Recupera o nome do banco de dados a partir da variáveis de ambiente 
    DB_DATABASE = os.getenv('DB_DATABASE')  
    DB_USER = os.getenv('DB_USER')  
    DB_HOSTNAME = os.getenv('DB_HOSTNAME')  
    DB_PORT = os.getenv("DB_PORT", 3306)  
    DB_PASSWORD = os.getenv("DB_PASSWORD")  


# Criar a URL

    DATABASE_URL = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}/{DB_DATABASE}"
    )

# Criar a Engine 

engine = create_engine(Config.DATABASE_URL)

# Testar a conexao

try:
    with engine.connect() as connection:
        print("Conexão com MySQL bem-sucedida!")
except Exception as e:
    print(f"Erro ao conectar: {e}")