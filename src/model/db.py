from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base
Base = declarative_base()
from sqlalchemy.orm import sessionmaker
from src.model.config import Config
from src.model.config import engine
from sqlalchemy import Date


# Carregar a URL do banco de dados a partir do arquivo de configuração
DATABASE_URL = Config.DATABASE_URL

# Criação da base de modelos
Base = declarative_base()

# Modelo de Tarefa
class Tarefa(Base):
    #Criação da tabela tarefas_WF
    __tablename__ = 'tarefas_WF'

    # Definição das colunas da tabela
    ID = Column(Integer, primary_key=True, autoincrement=True)
    DESCRICAO = Column(String(255), nullable=False)
    SITUACAO = Column(Boolean, default=False)
    CATEGORIA = Column(String(255), nullable=False)
    DATA_TAREFA = Column(Date, nullable=True)

# Criar as tabelas no banco de dados
Base.metadata.create_all(engine)

# Criar uma sessão para interagir com o banco
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
