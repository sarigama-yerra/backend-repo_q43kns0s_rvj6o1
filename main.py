import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product, Order, ServiceRequest

app = FastAPI(title="Producer Shop API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProductFilter(BaseModel):
    category: Optional[str] = None
    type: Optional[str] = None
    featured: Optional[bool] = None
    q: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Producer Shop Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Seed some demo products if empty
@app.post("/seed")
def seed_products():
    try:
        count = db["product"].count_documents({}) if db else 0
        if count > 0:
            return {"seeded": False, "message": "Products already exist"}
        demo = [
            {
                "title": "808 Warfare Vol. 1",
                "description": "Hard-hitting 808s crafted for trap and drill.",
                "price": 29.0,
                "category": "Drum Kits",
                "type": "drum_kit",
                "image": "https://images.unsplash.com/photo-1511379938547-c1f69419868d?auto=format&fit=crop&w=1200&q=60",
                "tags": ["808", "trap", "drill", "bass"],
                "is_service": False,
                "is_featured": True,
                "in_stock": True,
                "rating": 4.8
            },
            {
                "title": "Soul Samples Pack Vol. 2",
                "description": "Royalty-free soulful samples for boom bap vibes.",
                "price": 39.0,
                "category": "Samples",
                "type": "sample_pack",
                "image": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=1200&q=60",
                "tags": ["soul", "boom bap", "loops"],
                "is_service": False,
                "is_featured": True,
                "in_stock": True,
                "rating": 4.7
            },
            {
                "title": "Mixing Service (per track)",
                "description": "Professional mixing tailored for modern hip-hop.",
                "price": 99.0,
                "category": "Services",
                "type": "mixing",
                "image": "https://images.unsplash.com/photo-1513863323963-624d16b7bb15?auto=format&fit=crop&w=1200&q=60",
                "tags": ["service", "mixing"],
                "is_service": True,
                "is_featured": True,
                "in_stock": True,
                "rating": 4.9
            },
            {
                "title": "Mastering Service (per track)",
                "description": "Radio-ready loudness with clarity and punch.",
                "price": 59.0,
                "category": "Services",
                "type": "mastering",
                "image": "https://images.unsplash.com/photo-1483412033650-1015ddeb83d1?auto=format&fit=crop&w=1200&q=60",
                "tags": ["service", "mastering"],
                "is_service": True,
                "is_featured": False,
                "in_stock": True,
                "rating": 4.9
            }
        ]
        for p in demo:
            create_document("product", p)
        return {"seeded": True, "count": len(demo)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/products/query")
def query_products(filters: ProductFilter):
    try:
        query = {}
        if filters.category:
            query["category"] = filters.category
        if filters.type:
            query["type"] = filters.type
        if filters.featured is not None:
            query["is_featured"] = filters.featured
        if filters.q:
            query["$or"] = [
                {"title": {"$regex": filters.q, "$options": "i"}},
                {"description": {"$regex": filters.q, "$options": "i"}},
                {"tags": {"$in": [filters.q]}}
            ]
        products = get_documents("product", query)
        # Convert ObjectId to string
        for p in products:
            p["_id"] = str(p["_id"])
        return {"items": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CreateOrder(BaseModel):
    customer_name: str
    customer_email: str
    notes: Optional[str] = None
    items: List[dict]

@app.post("/orders")
def create_order(order: CreateOrder):
    try:
        total = sum([it.get("price", 0) * it.get("quantity", 1) for it in order.items])
        order_doc = Order(
            customer_name=order.customer_name,
            customer_email=order.customer_email,
            notes=order.notes,
            total=total,
            items=[
                {
                    "product_id": it.get("product_id"),
                    "title": it.get("title"),
                    "quantity": it.get("quantity", 1),
                    "price": it.get("price", 0)
                } for it in order.items
            ],
            status="pending"
        )
        inserted_id = create_document("order", order_doc)
        return {"id": inserted_id, "status": "pending", "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/service-request")
def service_request(req: ServiceRequest):
    try:
        inserted_id = create_document("servicerequest", req)
        return {"id": inserted_id, "message": "Thanks! We'll get back to you shortly."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
