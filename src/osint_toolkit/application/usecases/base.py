from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class UseCaseRequest:
    pass


@dataclass
class UseCaseResponse:
    success: bool
    data: Any = None
    error: str | None = None


class IUseCase(ABC):
    @abstractmethod
    async def execute(self, request: UseCaseRequest) -> UseCaseResponse:
        pass