"""Build shared CSV products from manually downloaded Kaggle sources."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.pipeline import build

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-season",type=int,default=2015)
    build(parser.parse_args().start_season)
    from scripts.export_schedule import export_schedule
    export_schedule()
