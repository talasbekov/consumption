from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core import Base
from exceptions import NotFoundException

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class ServiceBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    def __init__(self, model: Type[ModelType]):
        """_summary_

        Base Service class with default methods to Create, Read, Update, Delete (CRUD).
        """

        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_by_id(self, db: Session, id: Any) -> ModelType:
        res = self.get(db, id)
        if res is None:
            raise NotFoundException(
                detail=f"{self.model.__name__} with id {id} not found!"
            )
        return res

    def get_multi(
            self, db: Session, skip: int = 0, limit: int = 500
    ) -> List[ModelType]:
        return db.query(self.model).order_by(self.model.id).offset(skip).limit(limit).all()

    def create(
        self,
        db: Session,
        obj_in: Union[CreateSchemaType, Dict[str, Any]],
        model: ModelType = None,
    ) -> ModelType:
        if model is None:
            model = self.model
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.flush()
        return db_obj

    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        print(obj_data, "obj")
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        print(db_obj, "obj2")
        db.add(db_obj)
        db.flush()
        return db_obj

    def remove(self, db: Session, id: str) -> ModelType:
        obj = self.get_by_id(db, id)
        print(obj, "remove_obj")
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"{obj.name} not found"
            )
        db.delete(obj)
        db.flush()
        return obj

    def transliterate(self, text: str) -> str:
        # Простой словарь для транслитерации
        translit_dict = {
            "а": "a",
            "б": "b",
            "в": "v",
            "г": "g",
            "д": "d",
            "е": "e",
            "ё": "yo",
            "ж": "zh",
            "з": "z",
            "и": "i",
            "й": "y",
            "к": "k",
            "л": "l",
            "м": "m",
            "н": "n",
            "о": "o",
            "п": "p",
            "р": "r",
            "с": "s",
            "т": "t",
            "у": "u",
            "ф": "f",
            "х": "kh",
            "ц": "ts",
            "ч": "ch",
            "ш": "sh",
            "щ": "shch",
            "ы": "y",
            "э": "e",
            "ю": "yu",
            "я": "ya",
            "ь": "",
            "ъ": "",
        }

        result = []
        for char in text:
            lower_char = char.lower()
            if lower_char in translit_dict:
                translit_char = translit_dict[lower_char]
                if char.isupper():
                    translit_char = translit_char.capitalize()
                result.append(translit_char)
            else:
                result.append(char)

        return "".join(result)
