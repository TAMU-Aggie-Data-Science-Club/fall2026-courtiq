"""One explicit daily cache refresh; never invoked by normal app navigation."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.odds_api import refresh

if __name__=="__main__":
    try:
        _,message=refresh(); print(message)
    except ValueError as exc:
        raise SystemExit(str(exc)) from None
