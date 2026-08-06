"""
IO Utilities for loading YAML configs and sample CSV datasets.
"""
from pathlib import Path
import pandas as pd
import yaml

def get_workspace_dir() -> Path:
    """Return absolute path to gpu_price_forecasting workspace root."""
    return Path(__file__).resolve().parent.parent

def load_yaml_config(config_name: str) -> dict:
    """Load YAML config file by name from configs/ directory."""
    workspace_dir = get_workspace_dir()
    config_path = workspace_dir / "configs" / config_name
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_sample_dataset(csv_name: str) -> pd.DataFrame:
    """Load sample CSV dataset from data/sample/ directory."""
    workspace_dir = get_workspace_dir()
    csv_path = workspace_dir / "data" / "sample" / csv_name
    if not csv_path.exists():
        raise FileNotFoundError(f"Sample CSV dataset not found at {csv_path}")
    return pd.read_csv(csv_path)

def save_processed_dataset(df: pd.DataFrame, csv_name: str) -> Path:
    """Save processed dataframe to data/processed/ directory."""
    workspace_dir = get_workspace_dir()
    output_dir = workspace_dir / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / csv_name
    df.to_csv(output_path, index=False)
    return output_path
