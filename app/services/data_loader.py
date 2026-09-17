from pathlib import Path
import pandas as pd


# Find the project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Location of the CSV file
DATA_PATH = BASE_DIR / "data" / "support_tickets.csv"


def load_data():
    """
    Load the support ticket CSV and prepare the data.
    """

    # Check whether the file exists
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {DATA_PATH}"
        )

    # Load CSV
    df = pd.read_csv(DATA_PATH)

    # Convert created_at to datetime
    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce"
    )

    # Convert numeric columns
    numeric_columns = [
        "response_time_hrs",
        "resolution_time_hrs",
        "customer_rating"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


if __name__ == "__main__":

    df = load_data()

    print("\n===== DATASET INFORMATION =====")

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nStatus distribution:")
    print(df["status"].value_counts())

    print("\nPriority distribution:")
    print(df["priority"].value_counts())

    print("\nCategory distribution:")
    print(df["category"].value_counts())