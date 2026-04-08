from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="Product API")

class Product(BaseModel):
    product_id: int
    name: str
    category: str
    price: float
    
sample_products = [
    {
        "product_id": 123,
        "name": "Smartphone",
        "category": "Electronics",
        "price": 599.99
    },
    {
        "product_id": 456,
        "name": "Phone Case",
        "category": "Accessories",
        "price": 19.99
    },
    {
        "product_id": 789,
        "name": "Iphone",
        "category": "Electronics",
        "price": 1299.99
    },
    {
        "product_id": 101,
        "name": "Headphones",
        "category": "Accessories",
        "price": 99.99
    },
    {
        "product_id": 202,
        "name": "Smartwatch",
        "category": "Electronics",
        "price": 299.99
    }
]

products_db: List[Product] = [Product(**p) for p in sample_products]

@app.get("/product/{product_id}", response_model=Product)
async def get_product(product_id: int):
    for product in products_db:
        if product.product_id == product_id:
            return product
    
    raise HTTPException(
        status_code=404, 
        detail=f"Product with id {product_id} not found"
    )


@app.get("/products/search", response_model=List[Product])
async def search_products(
    keyword: str = Query(..., description="Ключевое слово для поиска"),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество результатов")
):
    keyword_lower = keyword.lower()

    results = []
    for product in products_db:
        if keyword_lower in product.name.lower():
            if category is None or product.category.lower() == category.lower():
                results.append(product)
        
        if len(results) >= limit:
            break

    return results