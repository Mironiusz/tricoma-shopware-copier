#!/usr/bin/env bash
# ==== aktywuj venv i uruchom main.py ====

# katalog, w którym znajduje się ten plik
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# aktywacja virtual-env
source "$ROOT/venv/bin/activate"

# przejście do kodu i start
cd "$ROOT/tricoma-shopware-copier"
python main.py
