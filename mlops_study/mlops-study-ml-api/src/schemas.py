from pydantic import BaseModel, validator


class ModelFeatures(BaseModel):
    applicant_id: str
    gender: str
    married: str
    family_dependents: str | None = None
    education: str
    self_employed: str
    applicant_income: int
    coapplicant_income: int
    loan_amount_term: int | None = None
    credit_history: float
    property_area: str

    @validator('gender')
    def validate_gender(cls, value):
        if value in ("Male", "Female"):
            return value
        raise ValueError("Please enter 'Male' or 'Female'.")

    @validator('married', 'self_employed')
    def validate_married(cls, value):
        if value in ("Yes", "No"):
            return value
        raise ValueError("Please enter 'Yes' or 'No'.")

    @validator('family_dependents')
    def validate_family_dependents(cls, value):
        if value in ("0", "1", "2", "3+"):
            return value
        raise ValueError("Please enter '0', '1', '2' or '3+'.")

    @validator('education')
    def validate_education(cls, value):
        if value in ("Graduate", "Not Graduate"):
            return value
        raise ValueError("Please enter 'Graduate' or 'Not Graduate'.")

    @validator('property_area')
    def validate_property_area(cls, value):
        if value in ("Rural", "Semiurban", "Urban"):
            return value
        raise ValueError("Please enter 'Rural', 'Semiurban' or 'Urban'.")


class ModelScore(BaseModel):
    applicant_id: str
    predict: int
    score: float
