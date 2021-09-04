from sqlalchemy import create_engine

# sqlalchemy.__versio__ shows sqlalchemy version
# print(sqlalchemy.__version__) current version is 1.4.23

# create engine is first thing what i need to do for every paticular database
# it's created with function create_engine. First property is db connection driver and url to db.
# Next we can set echo mod. If echo = true, every action will be write to log
# engine.future say that we use sqlalchemy 2.0 style


engine = create_engine('sqlite+pysqlite:///:memory:', echo=True, future=True)

# Connection - объект, через который производятся все действия с бд. Так как это открытый ресурс,
# то область его действия стоит ограничить. Проще всего сделать это через менеджер контекста
# Connection можно вызвать из объекта engine через engine.connect()


# -------------------- Code --------------------
# from sqlalchemy import text
#
# with engine.connect() as conn:
#     result = conn.execute(text("SELECT 'Hello World'"))
#     print(result.all())


# В приведенном выше примере менеджер контекста предоставил соединение с бд, а так же создал операцию внутри транзакции.
# Повдеение Python DBAPI завершение транзакции в момент закрытия контекста и вызывает ROLLBACK.
# 2021-09-02 00:23:32,617 INFO sqlalchemy.engine.Engine BEGIN (implicit)
# 2021-09-02 00:23:32,617 INFO sqlalchemy.engine.Engine SELECT 'Hello World'
# 2021-09-02 00:23:32,617 INFO sqlalchemy.engine.Engine [generated in 0.00027s] ()
# [('Hello World',)]
# 2021-09-02 00:23:32,618 INFO sqlalchemy.engine.Engine ROLLBACK
# В Этом случае фиксацию нужно производить вручную,
# через Connect.commit(). В противном случае ROLLBACK откатит все изменения.


# -------------------- Code --------------------
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(
        text("CREATE TABLE some_table (x int, y int)")
    )
    conn.execute(
        text("INSERT INTO some_table (x, y) VALUES(:x, :y)"),
        [{"x": 1, "y": 1 }, {"x": 2, "y": 4}]
    )
    conn.commit()

# В Этом примере commit происходить по инициативе пользователя.
# 2021-09-02 00:05:04,374 INFO sqlalchemy.engine.Engine BEGIN (implicit)
# 2021-09-02 00:05:04,374 INFO sqlalchemy.engine.Engine CREATE TABLE some_table (x int, y int)
# 2021-09-02 00:05:04,374 INFO sqlalchemy.engine.Engine [generated in 0.00028s] ()
# 2021-09-02 00:05:04,375 INFO sqlalchemy.engine.Engine INSERT INTO some_table (x, y) VALUES(?, ?)
# 2021-09-02 00:05:04,375 INFO sqlalchemy.engine.Engine [generated in 0.00012s] ((1, 1), (2, 4))
# 2021-09-02 00:05:04,375 INFO sqlalchemy.engine.Engine COMMIT
# этот стиль называется фиксацией на ходу.


# Это первый, но не единственный стиль фиксации изменений.
# Во втором случае мы можем объявить соединение через engine.begin()
# Этот стиль предполагает, что в конце контекста произойдет COMMIT в случае успеха, либо ROLLBACK в случае исключения.
# Получается , что весь блок будет заключен в одну транзакцию.
# Такой стиль называется начать один раз.


# -------------------- Code --------------------
with engine.begin() as conn:
    conn.execute(
        text("INSERT INTO some_table (x, y) VALUES(:x, :y)"),
        [{"x": 6, "y": 8}, {"x": 9, "y": 10}]
    )

# 2021-09-02 00:29:58,619 INFO sqlalchemy.engine.Engine BEGIN (implicit)
# 2021-09-02 00:29:58,619 INFO sqlalchemy.engine.Engine INSERT INTO some_table (x, y) VALUES(?, ?)
# 2021-09-02 00:29:58,619 INFO sqlalchemy.engine.Engine [cached since 0.0007425s ago] ((6, 8), (9, 10))
# 2021-09-02 00:29:58,619 INFO sqlalchemy.engine.Engine COMMIT
# Такой стиль более лаконичен и от этого предпочтителен, но фиксация на ходу более гибкая.

# Как видно из лога, транзакция начианиется с BEGIN (implicit).
# Это означает, что в базу данных никак команд пока не отправлялось,
# а сама транзакция происходит неявно, в рамках DBAPI.

# Результатом запроса к БД является объект Result. Как в случае работы с Core при работе через Connect.execute,
# так и в случае с ORM при работе через Session.execute


# -------------------- Code --------------------
with engine.connect() as conn:
    result = conn.execute(text("SELECT x, y FROM some_table"))
    for row in result:
        print(f"x: {row.x}, y: {row.y}")

# 2021-09-02 01:17:43,911 INFO sqlalchemy.engine.Engine BEGIN (implicit)
# 2021-09-02 01:17:43,911 INFO sqlalchemy.engine.Engine SELECT x, y FROM some_table
# 2021-09-02 01:17:43,911 INFO sqlalchemy.engine.Engine [generated in 0.00037s] ()
# x: 1, y: 1
# x: 2, y: 4
# x: 6, y: 8
# x: 9, y: 10
# 2021-09-02 01:17:43,911 INFO sqlalchemy.engine.Engine ROLLBACK


# Как видно из примера, Result реалезует протокол итератора.
# Каждая итерация возвращает объект типа Row. Row по своей сути похож на именованный кортеж.
# Полям строки может происходить несколькими способами:
#   1) Как к полю именованного кортежа row.x
#   2) По индексу row[0]
#   3) Как к отдельным переменным разименованного кортежа при инициализации цикла - for x, y in result:
#   4) В виде обхекта RowMapping, на словарь.
#      Это можно сделать, если итерироваться по маппингу,
#      возвращаемому в виде результата функции Result.mapping() - for row in result.mapping():


# Параметры отправки (Связные параметры)
with engine.connect() as conn:
    result = conn.execute(
        text("SELECT x, y FROM some_table WHERE y > :y"),
        {"y": 2}
    )
    for row in result:
        print(f"x: {row.x}, y: {row.y}")

# Значения в запрос передаются вторым парамтром функции execute в виде списка словарей
# В запрос в функции text параметры транслируются через маску вида :<ключ из словаря>.
# Лог запроса на вывод данных можно видеть ниже
# 2021-09-02 18:03:58,407 INFO sqlalchemy.engine.Engine BEGIN (implicit)
# 2021-09-02 18:03:58,407 INFO sqlalchemy.engine.Engine SELECT x, y FROM some_table WHERE y > ?
# 2021-09-02 18:03:58,407 INFO sqlalchemy.engine.Engine [generated in 0.00016s] (2,)
# x: 2, y: 4
# x: 6, y: 8
# x: 9, y: 10
# 2021-09-02 18:03:58,407 INFO sqlalchemy.engine.Engine ROLLBACK
# Как видно из лога, значение :y преобразовалось в "?". Если действовать так, то можно избеждать sql-инъекций.
# Если в параметрах передавать несколько словарей, то под капотом будет вызвана функция cursor.executemany()

with engine.connect() as conn:
    conn.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 11, "y": 12}, {"x": 13, "y": 14}]
    )
    conn.commit()

# Объединение параметров
# Так же параметры можно передавать через функцию bindparams(<параметр>=<значение>) у объекта возвращаемого из text(),
# а именно TextClause.



with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM some_table WHERE y > :y ORDER BY x, y").bindparams(y=6))
    for row in result:
        print(f"x: {row.x}, y: {row.y}")

# 2021-09-03 00:11:21,246 INFO sqlalchemy.engine.Engine BEGIN (implicit)
# 2021-09-03 00:11:21,246 INFO sqlalchemy.engine.Engine SELECT * FROM some_table WHERE y > ? ORDER BY x, y
# 2021-09-03 00:11:21,246 INFO sqlalchemy.engine.Engine [generated in 0.00017s] (6,)
# x: 6, y: 8
# x: 9, y: 10
# x: 11, y: 12
# x: 13, y: 14
# 2021-09-03 00:11:21,247 INFO sqlalchemy.engine.Engine ROLLBACK


# Все предыдущие примеры так же можно применить к фундаментальному объекту ORM, а Именно к Session
# Вариантов создания есть несколько, самый простой из них - вызвать создание сессии серез иницализацию объекта,
# передав ей в качестве параметра engine

# Основной особенностью сессии является то, что он не держит соединение после транзакции,
# и получает новое соединение при следующем запросе.

from sqlalchemy.orm import Session
with Session(engine) as session:
    session.execute(
        text("UPDATE some_table SET y=:y WHERE x=:x"),
        [{"x": 9, "y":11}, {"x": 13, "y": 15}]
    )
    session.commit()

# 2021-09-03 00:23:20,646 INFO sqlalchemy.engine.Engine BEGIN (implicit)
# 2021-09-03 00:23:20,646 INFO sqlalchemy.engine.Engine UPDATE some_table SET y=? WHERE x=?
# 2021-09-03 00:23:20,647 INFO sqlalchemy.engine.Engine [generated in 0.00014s] ((11, 9), (15, 13))
# 2021-09-03 00:23:20,647 INFO sqlalchemy.engine.Engine COMMIT