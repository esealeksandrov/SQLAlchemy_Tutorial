from sqlalchemy import select
from str_patterns import underline_for_header



# ORM и Core для запросов на выборку данных пользуются оператором sqlalchemy.select
# Однако в ORM есть возможность использовать достаточно много дополнительных опций.
from SQL_Alchemy_metadata import *
from SQL_Alchemy_metadata import engine
import Insert


print(underline_for_header.format("Select Block"))
stmt = select(user_table).where(user_table.c.name == "spongebob")
print(stmt)

with engine.connect() as conn:
    for row in conn.execute(stmt):
        print(row)
# Пример простого Select. Как и в остальных случаях, Оператор передается на исполнение либо
# объекту Connections, в случае с core режимом, либо Объекту Session, в случае, когда мы работаем с ORM.
# Вывод:
# SELECT user_account.id, user_account.name, user_account.fullname
# FROM user_account
# WHERE user_account.name = :name_1
# 2021-09-14 00:17:11,224 INFO sqlalchemy.engine.Engine BEGIN (implicit)
# 2021-09-14 00:17:11,224 INFO sqlalchemy.engine.Engine SELECT user_account.id, user_account.name, user_account.fullname
# FROM user_account
# WHERE user_account.name = ?
# 2021-09-14 00:17:11,224 INFO sqlalchemy.engine.Engine [generated in 0.00020s] ('spongebob',)
# (1, 'spongebob', 'Spongebob Squarepants')
# 2021-09-14 00:17:11,224 INFO sqlalchemy.engine.Engine ROLLBACK


print(underline_for_header.format("Select Block with ORM style"))

stmt = select(User).where(User.name == 'spongebob')
from sqlalchemy.orm import Session
with Session(engine) as session:
    for row in session.execute(stmt):
        print(row)
# В случае с ORM результатом select будет не набор Row обхектов, а набор Экземпляров класса модели, которую вы
# пытаетесь получить.
# Вывод:
# 2021-09-14 00:31:34,414 INFO sqlalchemy.engine.Engine BEGIN (implicit)
# 2021-09-14 00:31:34,414 INFO sqlalchemy.engine.Engine SELECT user_account.id, user_account.name, user_account.fullname
# FROM user_account
# WHERE user_account.name = ?
# 2021-09-14 00:31:34,414 INFO sqlalchemy.engine.Engine [generated in 0.00013s] ('spongebob',)
# (User(id=1, name='spongebob', fullname='Spongebob Squarepants'),)
# 2021-09-14 00:31:34,414 INFO sqlalchemy.engine.Engine ROLLBACK




