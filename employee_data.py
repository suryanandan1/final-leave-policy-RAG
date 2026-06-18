import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
EXCEL_PATH = os.path.join(DATA_DIR, "employees.xlsx")


def clean_columns(df):
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )
    return df


def load_employee_df():
    if not os.path.exists(EXCEL_PATH):
        os.makedirs(DATA_DIR, exist_ok=True)
        df = pd.DataFrame(columns=[
            "employee_id", "name", "grade/band", "joining_date",
            "pl_taken", "cl_taken", "sl_taken"
        ])
        df.to_excel(EXCEL_PATH, index=False)
        return clean_columns(df)

    df = pd.read_excel(EXCEL_PATH, header=0)
    df = clean_columns(df)

    if "employee_id" not in df.columns:
        df = pd.read_excel(EXCEL_PATH, header=1)
        df = clean_columns(df)

    return df


def save_employee_df(df):
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        df.to_excel(EXCEL_PATH, index=False)
        return True, "Employee data saved."
    except PermissionError:
        return False, "Please close employees.xlsx and try again."


def _safe_int(value):
    try:
        if pd.isna(value):
            return 0
        return int(float(value))
    except Exception:
        return 0


def get_employee_by_id(employee_id):
    df = load_employee_df()

    if "employee_id" not in df.columns:
        return None

    df["employee_id"] = df["employee_id"].astype(str).str.strip()
    employee_id = str(employee_id).strip()

    employee = df[df["employee_id"] == employee_id]

    if employee.empty:
        return None

    row = employee.iloc[0]

    return {
        "employee_id": str(row.get("employee_id", "")),
        "name": str(row.get("name", "")),
        "grade": str(row.get("grade/band", row.get("grade", ""))),
        "joining_date": str(row.get("joining_date", "")),
        "PL_taken": _safe_int(row.get("pl_taken", 0)),
        "CL_taken": _safe_int(row.get("cl_taken", 0)),
        "SL_taken": _safe_int(row.get("sl_taken", 0)),
    }


def signup_employee_excel(
    employee_id,
    name,
    grade,
    joining_date,
    pl_taken,
    cl_taken,
    sl_taken
):
    df = load_employee_df()

    if "employee_id" not in df.columns:
        df["employee_id"] = ""

    df["employee_id"] = df["employee_id"].astype(str).str.strip()
    employee_id = str(employee_id).strip()

    new_employee = {
        "employee_id": employee_id,
        "name": name,
        "grade/band": grade,
        "joining_date": joining_date,
        "pl_taken": pl_taken,
        "cl_taken": cl_taken,
        "sl_taken": sl_taken,
    }

    if employee_id in df["employee_id"].values:
        index = df[df["employee_id"] == employee_id].index[0]
        for key, value in new_employee.items():
            if key not in df.columns:
                df[key] = ""
            df.loc[index, key] = value
        return save_employee_df(df)

    df = pd.concat([df, pd.DataFrame([new_employee])], ignore_index=True)
    return save_employee_df(df)
