from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.schemas import RegressionResponse, RegressionConfig, ModelSummary, ModelQuality
from src.models.regression import AnalysisRequest, RegressionResult
from src.models.scrapedproduct import ScrapedProduct
from src.routes.regrassion import run_regression, validate_config
import json
from typing import List, Dict, Any, Optional
import pandas as pd
from fastapi import status

router = APIRouter()

def extract_numeric_price(price_str: str) -> float:
    if not price_str:
        return None
    numeric_str = ''.join(c for c in price_str if c.isdigit() or c == '.')
    try:
        return float(numeric_str)
    except (ValueError, TypeError):
        return None

@router.post("/analyse-db-regression", response_model=RegressionResponse, tags=["Regression Analysis"])
async def analyse_db_regression(
    config: RegressionConfig,
    request_id: Optional[int] = None,
    marketplace_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):

    try:
        query = select(ScrapedProduct)
        
        if request_id is not None:
            query = query.where(ScrapedProduct.request_id == request_id)
        if marketplace_id is not None:
            query = query.where(ScrapedProduct.marketplace_id == marketplace_id)
            
        result = await db.execute(query)
        products = result.scalars().all()
        
        if not products:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Не знайдено жодного запису за вказаними параметрами"
            )
        
        data = []
        for product in products:
            price = extract_numeric_price(product.scraped_price)
            if price is None:
                continue
                
            data.append({
                'price': price,
                'marketplace_id': product.marketplace_id,
                'request_id': product.request_id,
                'scraped_at': product.scraped_at.isoformat() if product.scraped_at else None
            })
        
        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не вдалося отримати числові значення цін для аналізу"
            )
            
        df = pd.DataFrame(data)
        
        validate_config(df, config.dependent_variable, config.independent_variables)
        
        coefs, std_errs, t_stats, p_vals, conf_int, r2, adj_r2, f_stat, f_pval, n_obs, formula = run_regression(
            df, config.dependent_variable, config.independent_variables
        )
        
        db_request = AnalysisRequest(
            csv_filename=f"db_export_{request_id or 'all'}_{marketplace_id or 'all'}",
            dependent_variable=config.dependent_variable,
            independent_variables=json.dumps(config.independent_variables, ensure_ascii=False),
            formula=formula
        )
        
        db.add(db_request)
        await db.flush()
        
        result = RegressionResult(
            request_id=db_request.id,
            coefficients_json=json.dumps(coefs, ensure_ascii=False),
            std_errors_json=json.dumps(std_errs, ensure_ascii=False),
            t_statistics_json=json.dumps(t_stats, ensure_ascii=False),
            p_values_json=json.dumps(p_vals, ensure_ascii=False),
            r_squared=float(r2),
            adj_r_squared=float(adj_r2),
            f_statistic=float(f_stat) if f_stat is not None else None,
            f_p_value=float(f_pval) if f_pval is not None else None,
            n_observations=n_obs
        )
        
        db.add(result)
        await db.commit()
        
        model_summary = ModelSummary(
            coefficients=coefs,
            std_errors=std_errs,
            t_statistics=t_stats,
            p_values=p_vals,
            confidence_intervals=conf_int
        )
        
        model_quality = ModelQuality(
            r_squared=float(r2),
            adj_r_squared=float(adj_r2),
            f_statistic=float(f_stat) if f_stat is not None else None,
            f_p_value=float(f_pval) if f_pval is not None else None,
            n_observations=n_obs
        )
        
        return RegressionResponse(
            analysis_id=db_request.id,
            model_summary=model_summary,
            model_quality=model_quality,
            formula=formula
        )
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутрішня помилка сервера: {str(e)}"
        )
