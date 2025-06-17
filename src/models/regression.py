from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from src.database import Base


class AnalysisRequest(Base):
    __tablename__ = 'analysis_requests'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    csv_filename: Mapped[str] = mapped_column(String, nullable=False)
    dependent_variable: Mapped[str] = mapped_column(String, nullable=False)
    independent_variables: Mapped[str] = mapped_column(Text, nullable=False)
    formula: Mapped[str] = mapped_column(String, nullable=False)


class RegressionResult(Base):
    __tablename__ = 'regression_results'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    request_id: Mapped[int] = mapped_column(ForeignKey('analysis_requests.id'))
    coefficients_json: Mapped[str] = mapped_column(Text, nullable=False)
    std_errors_json: Mapped[str] = mapped_column(Text, nullable=False)
    t_statistics_json: Mapped[str] = mapped_column(Text, nullable=False)
    p_values_json: Mapped[str] = mapped_column(Text, nullable=False)
    r_squared: Mapped[float] = mapped_column(Float, nullable=False)
    adj_r_squared: Mapped[float] = mapped_column(Float, nullable=False)
    f_statistic: Mapped[float] = mapped_column(Float, nullable=False)
    f_p_value: Mapped[float] = mapped_column(Float, nullable=False)
    n_observations: Mapped[int] = mapped_column(Integer, nullable=False)
