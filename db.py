from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_URI = "postgresql://postgres:postgres@localhost/script_helper"
engine = create_engine(DB_URI)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Script(Base):
    __tablename__ = 'scripts'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    command = Column(Text, nullable=False)


def create_tables():
    """Создает таблицы в базе данных (если они еще не существуют)."""
    Base.metadata.create_all(engine)


def get_scripts():
    """Возвращает список всех скриптов из базы данных."""
    with SessionLocal() as session:
        return session.query(Script).all()


def add_script_to_db(name, command):
    """
    Добавляет новый скрипт в базу данных.
    Возвращает объект добавленного скрипта.
    """
    with SessionLocal() as session:
        new_script = Script(name=name, command=command)
        session.add(new_script)
        session.commit()
        # Используем refresh, чтобы гарантировать наличие ID после commit
        session.refresh(new_script)
        return new_script


def delete_script_from_db(script_id):
    """
    Удаляет скрипт из базы данных по ID.
    Возвращает имя удаленного скрипта, если удаление прошло успешно.
    """
    with SessionLocal() as session:
        script_to_delete = session.query(Script).filter(Script.id == script_id).first()
        if not script_to_delete:
            raise ValueError(f"Script with ID {script_id} not found.")

        # Если объект отвязан, то связать его сессией через merge
        session.merge(script_to_delete)
        session.delete(script_to_delete)
        session.commit()
        return script_to_delete.name


def run_script_from_db(command):
    """
    Выполняет команду из базы данных через системный вызов.
    """
    import os
    try:
        os.system(command)
    except Exception as e:
        print(f"Error running script: {e}")
