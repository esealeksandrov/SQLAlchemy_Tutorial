from sqlalchemy import engine, insert
from SQL_Alchemy_metadata import user_table, address_table, engine

print("\n{:_^80s}".format("Inser Log Statret")) # Для выделения лога исполнения Insert конструкций

stmt = insert(user_table).values(name="spongebob", fullname="Spongebob Squarepants")
print(stmt)
# Вывод: INSERT INTO user_account (name, fullname) VALUES (:name, :fullname)
# Как видно из примера, подготовка запроса на вставку осуществляется при помощи функции insert
# Не стоит ошибаться и предполагать, что данннная функция возвращает именно строковое представление оператора.
# Вернется объект типа Insert. Это пример параметризированной конструкции.
# Что-то аналогичное мы встречали при использовании функции text().

# Преобразование Insert в конструкцию со строковым представлением и набором параметров
compiled = stmt.compile()
# Параметры передаются в поле params у скомпилированного.
print(compiled.params, type(compiled))
# Сам обхект представлен в виде класса sqlalchemy.sql.compiler.StrSQLCompiler

# Сам объект Insert можно употребить при помощи объекта Connection соответствущего движка.
with engine.connect() as conn:
    result = conn.execute(stmt)
    conn.commit()
    print(result.inserted_primary_key)
#   Вывод:(1, ) - первичный ключ вновь добавленного объекта в БД.
#   В случае добавления нескольких записей результат будет другой.
# Вывод:
# INSERT INTO user_account (name, fullname) VALUES (:name, :fullname)
# {'name': 'spongebob', 'fullname': 'Spongebob Squarepants'} <class 'sqlalchemy.sql.compiler.StrSQLCompiler'>
# 2021-09-05 17:25:57,028 INFO sqlalchemy.engine.Engine BEGIN (implicit)
# 2021-09-05 17:25:57,028 INFO sqlalchemy.engine.Engine INSERT INTO user_account (name, fullname) VALUES (?, ?)
# 2021-09-05 17:25:57,028 INFO sqlalchemy.engine.Engine [generated in 0.00021s] ('spongebob', 'Spongebob Squarepants')
# 2021-09-05 17:25:57,029 INFO sqlalchemy.engine.Engine COMMIT

# Однако не обязательно использовать именно функцию values, для заполнения полей таблицы. Можно добавит их на этапе
# исполнения в виде списка словарей, как было при использования функции text()

with engine.connect() as conn:
    result = conn.execute(
        insert(user_table),
        [
            {"name": "sandy", "fullname": "Sandy Cheeks"},
            {"name": "patric", "fullname": "Patrick Star"},
        ]
    )
    conn.commit()
# Данная конструкция представляет собой форму ExecuteMany.
# Однако в этом случае не нужно писать SQL, он генерируется из объекта Insert.
# Вывод:
# 2021-09-05 17:36:41,090 INFO sqlalchemy.engine.Engine BEGIN (implicit)
# 2021-09-05 17:36:41,090 INFO sqlalchemy.engine.Engine INSERT INTO user_account (name, fullname) VALUES (?, ?)
# 2021-09-05 17:36:41,090 INFO sqlalchemy.engine.Engine [generated in 0.00019s] (('sandy', 'Sandy Cheeks'), ('patric', 'Patrick Star'))
# 2021-09-05 17:36:41,090 INFO sqlalchemy.engine.Engine COMMIT

# Заметка
# _________________________________Пример подзапроса__________________________________

print("\n{:_^80s}".format("Subquery Example"))
from sqlalchemy import select, bindparam


scalar_subq = (
    select(user_table.c.id).
        where(user_table.c.name==bindparam('username')).
        scalar_subquery()
)

with engine.connect() as conn:
    result = conn.execute(
        insert(address_table).values(user_id=scalar_subq),
        [
            {"username": 'spongebob', "email_address": "spongebob@sqlalchemy.org"},
            {"username": 'sandy', "email_address": "sandy@sqlalchemy.org"},
            {"username": 'sandy', "email_address": "sandy@squirrelpower.org"}
        ]
    )
    conn.commit()

# Вывод:
# 2021-09-06 00:46:28,674 INFO sqlalchemy.engine.Engine BEGIN (implicit)
# 2021-09-06 00:46:28,674 INFO sqlalchemy.engine.Engine INSERT INTO address (user_id, email_address) VALUES ((SELECT user_account.id
# FROM user_account
# WHERE user_account.name = ?), ?)
# 2021-09-06 00:46:28,674 INFO sqlalchemy.engine.Engine [generated in 0.00021s] (('spongebob', 'spongebob@sqlalchemy.org'), ('sandy', 'sandy@sqlalchemy.org'), ('sandy', 'sandy@squirrelpower.org'))
# 2021-09-06 00:46:28,674 INFO sqlalchemy.engine.Engine COMMIT



# INSERT FROM SELECT
# Вставку из выборки (например для заполнения таблицы значениями из другой таблицы)
# можно сделать при помощи специальной функции from_select обзекта Insert.
# Первым параметром передается список полей, которые используются для вставки,
# вторым сам запрос на выборку созданый при помощи sqlalchemy.select.
print("\n{:_^80s}".format("INSERT FROM SELECT Example"))

select_stmt = select(user_table.c.id, user_table.c.name + "@aol.com")
insert_stmt = insert(address_table).from_select(
    ["user_id", "email_address"], select_stmt
)

print(insert_stmt)
# Вывод:
# INSERT INTO address (user_id, email_address) SELECT user_account.id, user_account.name || :name_1 AS anon_1
# FROM user_account

# INSERT RETURNING
# Обычно возврат первого значения поддерживается по умолчанию, но его можно указать явно с помощью Insert.returning()
print("\n{:_^80s}".format("INSERT FROM SELECT Example"))

insert_stmt = insert(address_table).returning(address_table.c.id, address_table.c.email_address)
print(insert_stmt)

# Вывод:
# INSERT INTO address (id, user_id, email_address)
# VALUES (:id, :user_id, :email_address)
# RETURNING address.id, address.email_address

# Заметка:
# Returning так же поддерживается операторами UPDATE и DELETE, однако обычно его не стоит использовать
# при выполнении операций сразу с несколькими строками. Форма Executemany, как и API некоторых движков (например Oracle)
# позволяют возвращать только одно значение.