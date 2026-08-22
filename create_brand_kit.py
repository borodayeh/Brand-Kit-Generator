#!/usr/bin/env python3
"""
Backwards-compatible entry point / نقطهٔ ورود سازگار با نسخه‌های قبلی.

The implementation now lives in the `brand_kit_generator` package, but the
original command keeps working:

    python create_brand_kit.py ./MyBrand

پیاده‌سازی به بستهٔ `brand_kit_generator` منتقل شده، اما دستور قبلی همچنان کار می‌کند.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from brand_kit_generator.cli import main

if __name__ == "__main__":
    sys.exit(main())
