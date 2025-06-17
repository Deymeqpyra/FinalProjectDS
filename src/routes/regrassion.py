from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.schemas import RegressionResponse, RegressionConfig, ModelSummary, ModelQuality
from src.models.regression import AnalysisRequest, RegressionResult
import shutil
import os
import json
from typing import List, Dict, Any
import pandas as pd
from statsmodels.formula.api import ols
from fastapi import status

router = APIRouter()


async def read_csv_file(file_path: str) -> pd.DataFrame:
    """Читання CSV файлу з обробкою потенційних помилок."""
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Помилка читання CSV файлу: {str(e)}"
        )


def validate_config(df: pd.DataFrame, dep_var: str, indep_vars: List[str]) -> None:
    """Валідація вхідних даних та конфігурації."""
    if dep_var not in df.columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Залежна змінна '{dep_var}' не знайдена у файлі"
        )

    for var in indep_vars:
        if var not in df.columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Незалежна змінна '{var}' не знайдена у файлі"
            )


def run_regression(df: pd.DataFrame, dep_var: str, indep_vars: List[str]) -> tuple:
    """Виконання регресійного аналізу."""
    try:
        formula = f"{dep_var} ~ {' + '.join(indep_vars)}"
        model = ols(formula=formula, data=df).fit()

        coefs = model.params.to_dict()
        std_errs = model.bse.to_dict()
        t_stats = model.tvalues.to_dict()
        p_vals = model.pvalues.to_dict()
        conf_int = {k: list(v) for k, v in model.conf_int().to_dict('index').items()}

        return (
            coefs,
            std_errs,
            t_stats,
            p_vals,
            conf_int,
            model.rsquared,
            model.rsquared_adj,
            model.fvalue,
            model.f_pvalue,
            len(df),
            formula
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка під час виконання регресії: {str(e)}"
        )


@router.post("/analyse-regression", response_model=RegressionResponse, tags=["Regression Analysis"])
async def analyse_regression(
        csv_file: UploadFile = File(...),
        config: str = Form(...),
        db: AsyncSession = Depends(get_db)
):
    """
    Виконує регресійний аналіз завантаженого CSV-файлу.
    Приймає CSV-файл та конфігурацію аналізу у форматі JSON.
    """
    temp_path = None
    try:
        temp_path = f"temp_{csv_file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(csv_file.file, buffer)

        df = await read_csv_file(temp_path)

        try:
            config_dict = json.loads(config)
            config_obj = RegressionConfig(**config_dict)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Некоректний формат JSON конфігурації"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Помилка валідації конфігурації: {str(e)}"
            )

        validate_config(df, config_obj.dependent_variable, config_obj.independent_variables)

        coefs, std_errs, t_stats, p_vals, conf_int, r2, adj_r2, f_stat, f_pval, n_obs, formula = run_regression(
            df, config_obj.dependent_variable, config_obj.independent_variables
        )

        req = AnalysisRequest(
            csv_filename=csv_file.filename,
            dependent_variable=config_obj.dependent_variable,
            independent_variables=json.dumps(config_obj.independent_variables, ensure_ascii=False),
            formula=formula
        )
        db.add(req)
        await db.flush()

        res = RegressionResult(
            request_id=req.id,
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
        db.add(res)
        await db.commit()

        return RegressionResponse(
            analysis_id=req.id,
            model_summary=ModelSummary(
                coefficients=coefs,
                std_errors=std_errs,
                t_statistics=t_stats,
                p_values=p_vals,
                confidence_intervals=conf_int
            ),
            model_quality=ModelQuality(
                r_squared=float(r2),
                adj_r_squared=float(adj_r2),
                f_statistic=float(f_stat) if f_stat is not None else None,
                f_p_value=float(f_pval) if f_pval is not None else None,
                n_observations=n_obs
            ),
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
    finally:
        # Очистка тимчасових файлів
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass