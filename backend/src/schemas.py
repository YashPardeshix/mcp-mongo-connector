from pydantic import BaseModel, Field


class QueryCollectionInput(BaseModel):
    collection_name: str = Field(
        ..., description="The name of the collection to query"
    )
    query: str = Field(
        ..., description="The natural language text query to execute"
    )

class DescribeSchemaInput(BaseModel):
    collection_name: str = Field(
        ..., description="The name of the collection to describe"
    )

class InsertDocumentInput(BaseModel):
    collection_name: str = Field(
        ..., description="The name of the collection to insert the document into"
    )
    document_description: str = Field(
        ..., description="A natural language description of the document to insert"
    )

class UpdateDocumentInput(BaseModel):
    collection_name: str = Field(
        ..., description="The name of the collection to update the document in"
    )
    filter_description:str = Field(
        ..., description="A natural language description of the filter to apply to the document"
    )
    update_description:str = Field(
        ..., description="A natural language description of the update to apply to the document"
    )

class DeleteDocumentInput(BaseModel):
    collection_name: str = Field(
        ..., description="The name of the collection to delete the document from"
    )
    condition_description:str = Field(
        ..., description="A natural language description of the condition to apply to the document"
    )
    