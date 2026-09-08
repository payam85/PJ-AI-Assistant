import os
from pathlib import Path
from dataclasses import dataclass

ROOT = Path(__file__).resolve().parents[1]

@dataclass
class Config:
    model: str = "gpt-5"
    daily_calls: int = 6
    max_output: int = 2500
    input_price: float | None = None
    output_price: float | None = None

    @classmethod
    def load(cls):
        from dotenv import load_dotenv
        load_dotenv(os.environ.get("PJ_ENV_FILE", str(ROOT / ".env")), override=False)
        def price(name):
            v = os.environ.get(name, "")
            if not v:
                return None
            n = float(v)
            if not 0 <= n < 100000:
                raise ValueError("Invalid token price")
            return n
        result = cls(os.environ.get("PJ_MODEL", "gpt-5"),
                     int(os.environ.get("PJ_DAILY_CALLS", "6")),
                     int(os.environ.get("PJ_MAX_OUTPUT_TOKENS", "2500")),
                     price("PJ_INPUT_PRICE"), price("PJ_OUTPUT_PRICE"))
        if not 1 <= result.daily_calls <= 100 or not 256 <= result.max_output <= 8000:
            raise ValueError("Invalid call or output limit")
        return result
