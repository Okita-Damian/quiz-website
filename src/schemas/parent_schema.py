
from pydantic import BaseModel, Field


# -------------------------
# Create Parent
# -------------------------

class ParentCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

 
# -------------------------
# Parent Login
# -------------------------

class ParentLogin(BaseModel):
    parent_id: str

 


# -------------------------
# Update Parent
# -------------------------

class ParentUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )


# -------------------------
# Parent Response
# -------------------------

class ParentResponse(BaseModel):
    id: str
    name: str
