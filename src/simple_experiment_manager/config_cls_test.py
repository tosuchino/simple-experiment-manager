from __future__ import annotations

from typing import Annotated, Any

from pydantic import BaseModel, Field, create_model


class ConfigClass:
    def __init__(self, **kwargs: Any):
        fields: dict[str, Any] = {k: (type(v), v) for k, v in kwargs.items()}
        self._Model = create_model("DynamicConfig", **fields)
        self._instance = self._Model.model_validate(kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._instance, name)

    def __repr__(self) -> str:
        return f"{self._Model.__name__}({self._instance.model_dump()})"

    def to_dict(self) -> dict[str, Any]:
        return self._instance.model_dump()

    @classmethod
    def from_dict(cls, obj: dict[str, Any]) -> ConfigClass:
        return cls(**obj)


if __name__ == "__main__":

    class MyClass(BaseModel):
        lr: Annotated[float, Field(ge=0.0, description="lerning rate.")] = Field(
            default=1.5
        )
        batch_size: Annotated[int, Field(ge=0)] = Field(default=32)

    print(f"MyClass name: {MyClass.__name__}")

    config_cls = ConfigClass(lr=1.5, batch_size=32)
    print(isinstance(config_cls, BaseModel))
    print(config_cls)
    print(config_cls.lr)
    print(config_cls.to_dict())

    config_cls2 = ConfigClass.from_dict({"name": "yamada", "age": 37})
    print(config_cls2)
    print(config_cls2.age)

    my_class = MyClass()
    print(my_class)

    # new_config = config_cls(lr=2.0, batch_size=64).to_pydantic()
    # print(new_config)

    # instance = MyClass(lr=3.0)

    # print(instance)

    # config_cls_custom = ConfigClass(name="yamada", age=30)
    # instance = config_cls_custom.to_pydantic()
    # print(instance)
    # print(instance.age)
