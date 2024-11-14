import datetime

from sqlalchemy import TIMESTAMP, Column, String, text, CLOB, Integer
from sqlalchemy.sql.sqltypes import Boolean
from abc import abstractmethod

from core import Base

"""
    This class is abstract entity class,
    which provides following columns to all inherited entities:
    - **id** : UUID - clustered index of table
    - **created_at**: datetime - Creation timestamp of entity
    - **updated_at**: datetime - Update timestamp of entity
"""


class Cloneable:

    @abstractmethod
    def clone(self, **attr):
        new_obj = self.__class__()

        for c in self.__table__.c:
            if c.name == "namekz":
                setattr(new_obj, "nameKZ", getattr(self, "nameKZ"))
            else:
                setattr(new_obj, c.name, getattr(self, c.name))

        new_obj.__dict__.update(attr)
        new_obj.id = Integer
        new_obj.created_at = datetime.datetime.now()
        new_obj.updated_at = datetime.datetime.now()

        return new_obj


class Model(Base, Cloneable):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


"""
    This class is abstract entity class,
    which provides following columns to all inherited entities:
    - **name** : str - required
"""


class NamedModel(Model):
    __abstract__ = True

    name = Column(String, nullable=False)
    nameKZ = Column("namekz", String, nullable=True)
    nameEN = Column("nameen", String, nullable=True)


"""
    This class is abstract entity class, which can be nested.
    This is merely markdown of nested classes.
    This Model doesn't do anything except marking all nested classes
"""


class NestedModel(Model):
    __abstract__ = True


"""
    This class is abstract entity class, which can be nested.
    This is merely markdown of nested classes.
    This Model doesn't do anything except marking all nested classes.
    Only difference between nested models is **name**
"""


class NamedNestedModel(NamedModel):
    __abstract__ = True


"""
    This class is abstract entity class,
    which provides following columns to all inherited entities:
    - **is_active** : bool - required
"""


class isActiveModel(Model):
    __abstract__ = True

    is_active = Column(Boolean, nullable=False, default=True)


class TextModel(Model):
    __abstract__ = True

    text = Column(CLOB, nullable=False)
    textKZ = Column("textkz", CLOB, nullable=True)
    textEN = Column("texten", CLOB, nullable=True)
