# При работе с данными в ORM стиле за манипуляцию с данными отвечает объект Session.
# Он создает транзакции выполняет действия с моделью. Если потребуется, может выполнить сброс.

from sqlalchemy.orm import Session
from DataOperations.Insert import engine
from SQL_Alchemy_metadata import User, Address
from str_patterns import underline_for_header

# При добавлении данных в core стиле мы использовали словари. В случае с ORM нужно использовать
# экземпляры классов соответствующей моделей.

print(underline_for_header.format("DATA MANIPULATION ORM STYLE"))

squidward = User(name="squidward", fullname="Squidward Tentacles")
krabs = User(name="ehkrabs", fullname="Eugene H. Krabs")

print(squidward)
# Вывод:
# User(id=None, name='squidward', fullname='Squidward Tentacles')
# Как видно из вывода поле автоинкремента заполняется самостоятельно значением None.
# Это происходит в момент инициализации объекта. Метод __init__ создался автоматически.
# (особенности работы моделей SQLAlchemy)
# После создания экземпляра, его сущность находится в так называемом переходном состоянии,
# оно не связано ни с каким объектом Session, который поможет в последствии генерировать для него insert

print(underline_for_header.format("INSERT ORM STYLE"))

# Для илюстрации работы INSERT в ORM стиле нужно создать сессию без использования менеджера контекста.
session = Session(engine)

# Добавление новых объектов в модель происходит при помощи метода Session.add()
session.add(squidward)
session.add(krabs)

# Однако после добавления объекты просто связаны с Сессией.
# Они в состоянии ожидания, и список ожидающих объектов модно посмотреть в Session.new
print(session.new)

# Вывод:
# IdentitySet([
#   User(id=None, name='squidward', fullname='Squidward Tentacles'),
#   User(id=None, name='ehkrabs', fullname='Eugene H. Krabs')
# ])
# IdentitySet - коллекция использующая для хеширования объектов функцию id, а не hash.
# в противном случае с обхектами не удалось бы работать ( наверное :) ).

# При работе с данными через Session использутеся такой шаблон как единица работы.
# По сути изменения накапливаются до тех пор пока не потребуются, После происходит процесс смывки даных в базу.
# Сам процесс можно проилюстрировать при помощи метода Session().flush()

session.flush()
# Вывод:
# 2021-09-15 01:17:52,164 INFO sqlalchemy.engine.Engine BEGIN (implicit)
# 2021-09-15 01:17:52,165 INFO sqlalchemy.engine.Engine INSERT INTO user_account (name, fullname) VALUES (?, ?)
# 2021-09-15 01:17:52,165 INFO sqlalchemy.engine.Engine [generated in 0.00013s] ('squidward', 'Squidward Tentacles')
# 2021-09-15 01:17:52,165 INFO sqlalchemy.engine.Engine INSERT INTO user_account (name, fullname) VALUES (?, ?)
# 2021-09-15 01:17:52,165 INFO sqlalchemy.engine.Engine [cached since 0.0004343s ago] ('ehkrabs', 'Eugene H. Krabs')
# Как видно из вывода Session сначала генерирует начало транзакции далее выражения для добавления обхектов.
# Однако транзакция остается открытой до тех пор пока не будет вызван соответствующий метод commit, rollback или close.
# Хотя Session().flush() может использоваться для ручного выталкивания изменений в транзакцию,
# обычно в этом нет необходимости, Поскольку функция Session известная как автозапуск так же выталкивает все изменения,
# когда происходит Session.commit().

# После вставки строк объекты обзаведутся своими id, которые были извлечены из базы.
# Для получения id был использован метод CursorResult.inserted_primary_key.
print(squidward.id, krabs.id)
# Вывод:
# 4 5

# Для проведения транзакции двух обхектов было сгенерировано соответствующее количество запросов,
# это связано с тем, что id на этом этапе еще не были извлечены. Если бы мы предоставили id,
# запрос сработал бы оптимальнее через executemany.



