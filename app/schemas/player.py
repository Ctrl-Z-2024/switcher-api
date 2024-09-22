from pydantic import BaseModel
    
class PlayerSchemaOut(BaseModel):
    id: int
    name: str
    
    class ConfigDict:
        from_attributes = True