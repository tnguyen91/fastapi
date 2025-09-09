from typing import Annotated
from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel, Field, field_validator

app = FastAPI()

@app.get("/")
def hello():
    return {"ok": True}

@app.get("/greet")
def greet(name: str = "world"):
    return {"greeting": f"Hello, {name}!"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"id": item_id}

class SumRequest(BaseModel):
    a: float
    b: float

class SumResponse(BaseModel):
    result: float

@app.post("/sum", response_model=SumResponse)
def sum_numbers(payload: SumRequest):
    return SumResponse(result=payload.a + payload.b)

@app.get("/double")
def double_number(x: int):
    return {"x": x, "double": x * 2}

class ItemIn(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(gt=0, description="Price must be > 0")
    tax_rate: float | None = Field(default=None, ge=0, le=1, description="0..1")

    @field_validator("name")
    @classmethod
    def strip_and_check(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name cannot be blank")
        return v

class ItemOut(BaseModel):
    id: int
    name: str
    price: float
    price_with_tax: float

_FAKE_ID = 0

@app.post("/items", response_model=ItemOut, status_code=201)
def create_item(item: ItemIn):
    """Validate body with Pydantic; enforce a business rule with HTTPException."""
    if item.price > 1_000_000:
        raise HTTPException(status_code=400, detail="price too high")
    global _FAKE_ID
    _FAKE_ID += 1
    price_with_tax = item.price * (1 + (item.tax_rate or 0))
    return ItemOut(
        id=_FAKE_ID,
        name=item.name,
        price=item.price,
        price_with_tax=price_with_tax,
    )

# Query/Path constraints with Annotated
@app.get("/safe-items/{item_id}")
def get_safe_item(
    item_id: Annotated[int, Path(gt=0)],
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    return {"item_id": item_id, "limit": limit}
