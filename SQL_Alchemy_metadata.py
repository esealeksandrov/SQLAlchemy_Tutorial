from sqlalchemy import MetaData

# SQLalchemy работает с такими абстракциями как таблицы (sqlalchemy.Table)
# с заключенными внутри колонками (sqlalchemy.Column).
# В свою очередь все таблицы можно объеденить в один объект коллекции метаданных (sqlalchemy.Metadata)
# По своей обхект метадата создается один раз для своего приложения и является переменной уровня модуля.
# В любом случае связанные таблицы лучше держать в одном обхекте метаданных, чтоб не было проблем со отношениями.

# привер создания объекта Metadata
metadata_obj = MetaData()

# Так же объявим классическую таблицу
from sqlalchemy import Table, Column, Integer, String

# Код создание таблицы очень похоже на sql аналог.
# Первым параметром передается имя таблицы, вторым обхект метаданных
user_table = Table(
    "user_account",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(30)),
    Column("fullname", String)
)

# Коллекция колонок обычно существует в виде словаря/ассоциативного массива расположенного по адресу Table.c
print(user_table.c.name, type(user_table.c.name))
# Вывод: user_account.name <class 'sqlalchemy.sql.schema.Column'>

print(user_table.c.keys())
# Вывод: ['id', 'name', 'fullname']

# id - является первичным ключем таблицы, и так же расположено по адресу Table.primary_key
# обернутое в конструкция PrimaryKeyConstraint (Ограничение первичного ключа)

print(user_table.primary_key, type(user_table.primary_key))
print(user_table.c.id, type(user_table.c.id)) # Само поле не обернуто в этот класс.

# Так же есть понятие ForeingKeyConstraint (Ограничение внешнего ключа). Как правило, это поле
# по которому осуществляется привязка к таблице. Внешний ключ.
# Объявляется он при помощи типа колонки sqlalchemy.ForeingKey

from sqlalchemy import ForeignKey

address_table = Table(
    "address",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column('user_id', ForeignKey('user_account.id'), nullable=False), # Указание внешнего ключа
    Column('email_address', String, nullable=False)
)
# При определении ForeingKey, тип данных столбца определяется связанным столбцом.
# В нашем случае Тип данных берется изиз столбца таблицы user_account.id (Integer)

# параметр nullable=False - аналог оператора NOT NULL при создании таблицы средствами SQL.
# Это ограничение так же доступно для анализа по пути Column.nullable
print(address_table.c.email_address.nullable)
# Вывод: False


print("{:_^80s}".format("Create Table"))
# После описания таблиц в виде классов Python, можно их создать при помощи метода create_all.
# Первым параметром нужно будет указать заранее созданный engine.

from sqlalchemy import create_engine

engine = create_engine('sqlite+pysqlite:///:memory:', echo=True, future=True)
metadata_obj.create_all(engine)
# Вывод:
# __________________________________Create Table__________________________________
# 2021-09-04 19:54:23,670 INFO sqlalchemy.engine.Engine BEGIN (implicit)
# 2021-09-04 19:54:23,671 INFO sqlalchemy.engine.Engine PRAGMA main.table_info("user_account")
# 2021-09-04 19:54:23,671 INFO sqlalchemy.engine.Engine [raw sql] ()
# 2021-09-04 19:54:23,671 INFO sqlalchemy.engine.Engine PRAGMA temp.table_info("user_account")
# 2021-09-04 19:54:23,671 INFO sqlalchemy.engine.Engine [raw sql] ()
# 2021-09-04 19:54:23,671 INFO sqlalchemy.engine.Engine PRAGMA main.table_info("address")
# 2021-09-04 19:54:23,671 INFO sqlalchemy.engine.Engine [raw sql] ()
# 2021-09-04 19:54:23,672 INFO sqlalchemy.engine.Engine PRAGMA temp.table_info("address")
# 2021-09-04 19:54:23,672 INFO sqlalchemy.engine.Engine [raw sql] ()
# 2021-09-04 19:54:23,672 INFO sqlalchemy.engine.Engine
# CREATE TABLE user_account (
# 	id INTEGER NOT NULL,
# 	name VARCHAR(30),
# 	fullname VARCHAR,
# 	PRIMARY KEY (id)
# )
#
#
# 2021-09-04 19:54:23,672 INFO sqlalchemy.engine.Engine [no key 0.00009s] ()
# 2021-09-04 19:54:23,673 INFO sqlalchemy.engine.Engine
# CREATE TABLE address (
# 	id INTEGER NOT NULL,
# 	user_id INTEGER NOT NULL,
# 	email_address VARCHAR NOT NULL,
# 	PRIMARY KEY (id),
# 	FOREIGN KEY(user_id) REFERENCES user_account (id)
# )
#
#
# 2021-09-04 19:54:23,673 INFO sqlalchemy.engine.Engine [no key 0.00008s] ()
# 2021-09-04 19:54:23,673 INFO sqlalchemy.engine.Engine COMMIT

# При создании таблиц учитывались особенности движка, это можно увидеть по цпецифичным для sqlite опратору PRAGMA
# , который перед созданием проверяет наличие таблицы в базе.
# Порядок создания таблиц определяется их связями через ForeingKey. Однако в сложных структурах таблицы могут быть
# созданы постфактум при использовании оператора ALTER.

# Удалить таблицы можно при помощи оператора MetaData.drop_all()
# В этом случае последовательность операторов DROP в запросе будет генерироваться в обратном порядке относительно
# процесса создания.

# операторы create_all и drop_all рекомендуется применять исключительно при тестах или для создания временных таблиц
# в памяти. Для долгосрочной перспективы рекомендуется использовать инструменты типа Alembic.
# Они позволяют работать с изменениями


# ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ORM

# Пользователи ORM в данном случае будут пользоваться объектом registry.
from sqlalchemy.orm import registry
mapper_registry = registry()

# registr уже содержит в себе MetaData по адресу registry().metadata
print(mapper_registry.metadata, type(mapper_registry.metadata))
# Вывод:
# MetaData() <class 'sqlalchemy.sql.schema.MetaData'>

# Так же меняется метод объявления объектов Table
# Теперь они объявляются не напрямую, а через предварительно созданный класс известный как декларативная база.
# Создать его можно двумя способами:
#   1) при помощи метода generate_base у объекта registry
Base = mapper_registry.generate_base()

#   2) при помощи специальной функции declarative_base из модуля sqlalchemy.orm
from sqlalchemy.orm import declarative_base
Base = declarative_base()  # Base перегружен

# Далее от этого класса нужно наследовать все объекты описывающие таблицы нашей дб

from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "user_account"

    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    fullname = Column(String)

    #addresses = relationship("Address", back_populates="user")

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True)
    email_addres = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user_account.id")) #, nullable=False)

    #user = relationship("User", back_populates="address")

    def __repr__(self):
        return f"Address(id={self.id!r}, email_addres={self.email_addres!r})"


# Перечисленные выше классы теперь являются сопоставленными классами и доступны для работы с операчиями добавления
# Посмотреть его основу можно через параметр __table__
print(repr(User.__table__))

# Это Table объект, который создан в результате декларативного процесса но основе поля __tablename__,
# полей класса созданных при помощи класса Column
# Так же между двумя таблицами были заданы отношения при помощи функции sqlalchemy.orm.relationship
# Это показывает ORM, что эти таблицы могут быть связанры в отношении один-ко-многим/многие-ко-многим.

# После объявления таблиц в виде классов, их так же можно отправить на инициализацию через MetaData.create_all(engine)
# Но так как в этом примере используется ORM стиль и классы наследуются от Base,
# то и обращаться нужно к параметрам Base, а именно к Base.metadata.create_all(engine)

# Объеденять классы таблиц можно и с заранее созданным объектом в стиле Core. Для этого при описании класса
# вместо присваивании имени таблицы в виде строки в __tablename__ делаем присваивание самого объекта в __table__

# Однако с таблицами реальной базы не всегда нужно работать через обхявление классов.
# Иногда можно просто загрузить/отразить их в момент исполнения кода. Делается это в момент создания объекта Table.
# если у него указан параметр autoload_with=<engine>, то класс проинициализируется на основе уже имеющейсяс
# в БД Таблицы.

from SQLAlchemy_Connect_Session import engine as other_engine

some_table = Table("some_table", metadata_obj, autoload_with=other_engine)

print(some_table, repr(some_table))
