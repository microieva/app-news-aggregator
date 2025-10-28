from pydantic import BaseModel, ConfigDict
from app.schemas import ArticleList


class ApiResponse(BaseModel):
  data: ArticleList

  class Config:
        from_attributes = True