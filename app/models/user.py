from dataclasses import dataclass, field


@dataclass(frozen=True)
class User:
    id: str
    name: str = ""
    email: str = ""
    role: str = "student"
    level: int = 1
    cellId: str | None = None
    ledCellIds: list[str] = field(default_factory=list)
    publicationTargets: dict[str, list[str]] = field(default_factory=dict)

    @property
    def is_authenticated(self) -> bool:
        return True

    @classmethod
    def from_document(cls, data: dict) -> "User":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
