from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.crud import scrape as crud_scrape
from src.models import scrapedproduct
from typing import Optional, Dict, Any
import csv
import io
import re

router = APIRouter()

def process_price(price_str: Optional[str]) -> str:
    if not price_str:
        return ""
    return re.sub(r'[^\d.]', '', price_str)


def extract_memory(title: Optional[str]) -> str:
    if not title:
        return ""
    
    patterns = [
        (r'(\d+)\s*GB', 1),           # 128GB -> 128
        (r'(\d+)\s*ГБ', 1),           # 128ГБ -> 128
        (r'(\d+)\s*TB', 1024),        # 1TB -> 1024
        (r'(\d+)\s*ТБ', 1024),        # 1ТБ -> 1024
        (r'(\d+)\s*GB\s+RAM', 1),    # 8GB RAM -> 8
        (r'(\d+)\s*ГБ\s+ОЗП', 1),   # 8ГБ ОЗП -> 8
    ]
    
    for pattern, multiplier in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            try:
                value = int(match.group(1)) * multiplier
                return str(value) + "GB"
            except (ValueError, IndexError):
                continue
    
    return ""


def extract_model_number(title: Optional[str]) -> str:
    if not title:
        return ""
    
    patterns = [
        r'(?:iPhone|iPad|Samsung|Xiaomi|Huawei|Sony|Google Pixel|Pixel|OnePlus|Oppo|Vivo|Realme|Redmi|Poco|Motorola|Nokia|ASUS|Lenovo|TECNO|Infinix|POCO|Blackview|Ulefone|Doogee|Umidigi|Cubot|UMIDIGI|Blackview|Oukitel|Xiaomi Redmi|Redmi Note|Xiaomi Mi|Mi )\s*(\d+)',  # iPhone 16 Pro -> 16
        r'\b(\d+)(?:\s*GB|\s*ГБ|\s*inch|\s*дюйм|\s*"|\s*см|\s*cm)\b',  # 16GB, 16 ГБ, 16", 16 дюймів
        r'\b(\d+)(?:\s*GB|\s*ГБ|$)'  # Просто число в кінці рядка або перед GB/ГБ
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            try:
                return match.group(1)
            except (ValueError, IndexError):
                continue
    
    return ""

def extract_screen_size(description: Optional[Dict[str, Any]]) -> Optional[float]:
    if not description or not isinstance(description, dict):
        return None
        
    possible_keys = ["Діагональ екрану", "Діагональ", "Екран", "Screen", "Screen Size"]
    
    for key in possible_keys:
        if key in description:
            try:
                match = re.search(r'\d+[.,]?\d*', str(description[key]))
                if match:
                    value = match.group(0).replace(',', '.')
                    return float(value)
            except (ValueError, TypeError):
                continue
    
    return None

def flatten_description(description: Optional[Dict[str, Any]]) -> Dict[str, str]:
    if not description:
        return {}
    
    flat = {}
    for key, value in description.items():
        if value is None:
            flat[key] = ""
        elif isinstance(value, (str, int, float, bool)):
            flat[key] = str(value)
        else:
            flat[key] = str(value)
    return flat

@router.get("/export-all-to-csv", response_class=Response)
async def export_all_to_csv(
    db: AsyncSession = Depends(get_db),
):

    try:
        products = await crud_scrape.get_all_scraped_products(db)
        if not products:
            raise HTTPException(status_code=404, detail="No products found in the database")
        
        all_description_keys = set()
        products_data = []
        
        for product in products:
            if not isinstance(product, scrapedproduct.ScrapedProduct):
                continue
                
            price = process_price(product.scraped_price)
            
            description = product.scraped_description or {}
            flat_desc = flatten_description(description)
            all_description_keys.update(flat_desc.keys())
            
            memory = extract_memory(product.scraped_product_title)
            model_number = extract_model_number(product.scraped_product_title)
            
            screen_size = extract_screen_size(flat_desc)
            
            product_data = {
                "Model": model_number,
                "Memory_GB": memory,
                "Screen_Size_Inches": f"{screen_size:.1f}" if screen_size is not None else "",
                "Price_UAH": price
            }
            
            # Only process the fields we need
            if any(f in ["Тип екрану", "Тип дисплею"] for f in flat_desc):
                value = flat_desc.get("Тип екрану") or flat_desc.get("Тип дисплею", "")
                product_data["Is_OLED"] = 1 if value and "oled" in str(value).lower() else 0
            else:
                product_data["Is_OLED"] = 0
                
            if "NFC" in flat_desc:
                value = flat_desc["NFC"]
                product_data["Has_NFC"] = 1 if value and (value == "Є" or "так" in str(value).lower()) else 0
            else:
                product_data["Has_NFC"] = 0
            products_data.append(product_data)
        
        # Define only the required columns in the specified order
        fieldnames = [
            "Model",
            "Memory_GB",
            "Screen_Size_Inches",
            "Price_UAH",
            "Is_OLED",
            "Has_NFC"
        ]
        
        output = io.StringIO()
        
        def clean_value(value, is_header=False):
            if value is None:
                return ""
            
            if is_header:
                return str(value)
                
            cleaned = re.sub(r'[^\d.-]', '', str(value))
            cleaned = re.sub(r'\.$', '', cleaned)
            return cleaned if cleaned else ""
        
        output.write(",".join(fieldnames) + "\n")
        
        for product_data in products_data:
            row = []
            for field in fieldnames:
                value = product_data.get(field, "")
                row.append(clean_value(value, is_header=False))
            output.write(",".join(row) + "\n")
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": "attachment; filename=products_export.csv",
                "Content-Encoding": "utf-8",
                "Content-Type": "text/csv; charset=utf-8"
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка при експорті даних: {str(e)}")
