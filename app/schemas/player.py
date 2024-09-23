from pydantic import BaseModel
    
class PlayerSchemaOut(BaseModel):
    id: int
    name: str
    game_id: int
    
    class ConfigDict:
        from_attributes = True