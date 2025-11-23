"""
Example router demonstrating API endpoint structure
موجه مثال يوضح بنية نقطة نهاية API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class ExampleItem(BaseModel):
    """Example data model - نموذج بيانات مثال"""
    id: int
    name: str
    description: Optional[str] = None
    tags: List[str] = []


class ExampleResponse(BaseModel):
    """Example response model - نموذج استجابة مثال"""
    success: bool
    message: str
    data: Optional[dict] = None


@router.get("/examples", response_model=List[ExampleItem])
async def get_examples():
    """
    Get example items
    الحصول على عناصر مثال
    
    This is a placeholder endpoint demonstrating the router structure.
    هذه نقطة نهاية توضيحية تظهر بنية الموجه.
    """
    return [
        ExampleItem(
            id=1,
            name="Example 1",
            description="First example item",
            tags=["demo", "test"]
        ),
        ExampleItem(
            id=2,
            name="Example 2",
            description="Second example item",
            tags=["demo"]
        ),
    ]


@router.get("/examples/{item_id}", response_model=ExampleItem)
async def get_example(item_id: int):
    """
    Get a specific example item by ID
    الحصول على عنصر مثال محدد بواسطة المعرف
    """
    if item_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid item ID")
    
    # Placeholder implementation
    return ExampleItem(
        id=item_id,
        name=f"Example {item_id}",
        description=f"Example item with ID {item_id}",
        tags=["demo"]
    )


@router.post("/examples", response_model=ExampleResponse)
async def create_example(item: ExampleItem):
    """
    Create a new example item
    إنشاء عنصر مثال جديد
    """
    # Placeholder implementation - في بيئة الإنتاج، سيتم حفظ هذا في قاعدة البيانات
    return ExampleResponse(
        success=True,
        message=f"Created example item: {item.name}",
        data=item.model_dump()
    )
