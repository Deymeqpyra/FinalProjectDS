import pandas as pd
from statsmodels.formula.api import ols
from fastapi import HTTPException
from typing import Dict, List, Tuple


def read_csv_file(file) -> pd.DataFrame:
    try:
        df = pd.read_csv(file)
        return df
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Помилка читання CSV: {e}")


def validate_config(df: pd.DataFrame, dependent: str, independents: List[str]):
    columns = set(df.columns)
    if dependent not in columns:
        raise HTTPException(status_code=400, detail=f"Залежна змінна '{dependent}' відсутня у CSV")
    for col in independents:
        if col not in columns:
            raise HTTPException(status_code=400, detail=f"Незалежна змінна '{col}' відсутня у CSV")
    if dependent in independents:
        raise HTTPException(status_code=400, detail="Залежна змінна не може бути серед незалежних")


def sanitize_column_name(name: str) -> str:
    # Прибираємо пробіли та інші проблемні символи, наприклад, замінимо пробіли на _
    return name.strip().replace(' ', '_').replace('-', '_')

def prepare_df_and_formula(df: pd.DataFrame, dependent: str, independents: List[str]) -> Tuple[pd.DataFrame, str]:
    # Створюємо словник відповідностей старих і нових назв колонок
    rename_map = {col: sanitize_column_name(col) for col in [dependent] + independents}
    df_renamed = df.rename(columns=rename_map)

    dep_renamed = rename_map[dependent]
    indeps_renamed = [rename_map[col] for col in independents]

    formula = f"{dep_renamed} ~ {' + '.join(indeps_renamed)}"
    return df_renamed, formula

def run_regression(
    df: pd.DataFrame,
    dependent: str,
    independents: List[str]
) -> Tuple[Dict, Dict, Dict, Dict, Dict, float, float, float, float, int, str]:
    df_prepared, formula = prepare_df_and_formula(df, dependent, independents)
    try:
        model = ols(formula, data=df_prepared).fit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Помилка регресійного аналізу: {e}")

    coefs = model.params.to_dict()
    std_errs = model.bse.to_dict()
    t_stats = model.tvalues.to_dict()
    p_vals = model.pvalues.to_dict()
    conf_int = {k: list(v) for k, v in model.conf_int().to_dict('index').items()}
    r2 = model.rsquared
    adj_r2 = model.rsquared_adj
    f_stat = float(model.fvalue) if model.fvalue is not None else None
    f_pval = float(model.f_pvalue) if model.f_pvalue is not None else None
    n_obs = int(model.nobs)
    return coefs, std_errs, t_stats, p_vals, conf_int, r2, adj_r2, f_stat, f_pval, n_obs, formula
