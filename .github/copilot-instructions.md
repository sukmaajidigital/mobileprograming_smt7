# Copilot Instructions for this Workspace

These instructions help AI coding agents work productively in this codebase. Focus on the concrete patterns, workflows, and architecture used here.

## Big Picture

- **Workspace layout:**
  - `uas/`: Flet GUI app for smart inventory with AI stock prediction.
  - `uts/`: Separate legacy CLI/desktop script (kasir) — not integrated with `uas`.
  - `template/`: SQL and Python templates unrelated to the running app.
- **App entry:** `uas/main.py` runs a Flet desktop/web UI. It renders a table of `barang`, supports CRUD add + delete, and uses an AI model to predict weekly sales per item.
- **Data layer:** `uas/koneksi.py` encapsulates all MySQL access using `fetch_data()` and `execute_query()` with a shared `DB_CONFIG` pointing at database `db_prediksi_stok`.
- **AI layer:** `uas/ai_model.py` pulls weekly "keluar" transactions for a given `id_barang`, builds a simple time-series feature (`Minggu_ke`) and fits `sklearn.linear_model.LinearRegression` to predict next week quantity.
- **Schema & seed:** `uas/db_prediksi_stok.sql` creates tables (`user`, `supplier`, `barang`, `transaksi`) and populates 200 `barang` rows plus 300+ `transaksi` examples.

## Data Flow

- UI events (`main.py`) → call CRUD helpers → call DB (`koneksi.py`).
- AI prediction (`main.py → ai_model.predict_sales(id_barang)`) → queries `transaksi` + `barang` via `fetch_data()` → returns a dict with `Prediksi_Mingguan`, `Sisa_Stok_Setelah_Prediksi`, `Status` used directly to render an `AlertDialog`.
- Delete uses `execute_query("DELETE FROM barang WHERE id_barang = %s", (id,))` and refreshes table via `load_data_table()`.

## Conventions & Patterns

- **UI framework:** Flet components and icons use string names (`Icon(name="insights")`, `IconButton(icon="analytics")`). Keep this pattern to avoid enum issues.
- **DB access:** Always go through `fetch_data(query, params)` or `execute_query(query, params)`; they open/close connections per call and return dictionaries (`cursor(dictionary=True)` in `fetch_data`).
- **Error handling:** Minimal; CRUD shows `SnackBar` on errors. Prefer returning empty lists from `fetch_data` and `0` from `execute_query` on failure.
- **Types:** Convert text-field inputs explicitly (`float`, `int`) before persisting.
- **Language/UI copy:** Labels and messages are Indonesian; maintain consistency.
- **Stock status coloring:** In table rows, color depends on `stok_saat_ini` vs `stok_minimum`.

## Setup & Run

- **Database:**
  1. Start MySQL locally.
  2. Execute `uas/db_prediksi_stok.sql` to create and seed `db_prediksi_stok`.
  3. Adjust `uas/koneksi.py:DB_CONFIG` (`host`, `user`, `password`) if needed.
- **Python deps (Windows):**
  ```bash
  python -m venv .venv
  .venv\Scripts\activate
  pip install flet mysql-connector-python pandas scikit-learn numpy
  ```
- **Run app:**
  ```bash
  cd uas
  python main.py
  ```

## Key Files to Read

- `uas/main.py`: UI structure, event handlers (`handle_tambah`, `show_prediksi`, `load_data_table`).
- `uas/koneksi.py`: DB connection, `fetch_data`, `execute_query` contract.
- `uas/ai_model.py`: `prepare_data_for_ai(id_barang)`, `predict_sales(id_barang)` logic and expected dict structure.
- `uas/db_prediksi_stok.sql`: table definitions and data ranges; helps craft queries over realistic data.

## Extending Functionality

- **Add CRUD fields:** Mirror existing `tambah_barang(...)` signature and form fields; update SQL insert accordingly.
- **Edit items:** Add an `UPDATE` path via a new dialog; follow `execute_query` pattern and refresh with `load_data_table()`.
- **More AI features:** If adding features (e.g., moving average, seasonality), keep `predict_sales` return shape consistent (`Prediksi_Mingguan`, `Sisa_Stok_Setelah_Prediksi`, `Status`) so `main.py` UI remains compatible.
- **Queries:** Prefer parameterized queries with `%s` placeholders; return dictionaries for ergonomics in Flet rendering.

## Testing & Debugging Tips

- **DB connectivity:** Temporarily print exceptions in `koneksi.py` (already done); verify with a simple `SELECT 1` via `fetch_data`.
- **AI inputs:** Ensure `transaksi` has enough weekly data; `prepare_data_for_ai` resamples to `W` and may drop NA rows.
- **UI icons:** Use string icon names known to Flet; avoid enum usage.

## Examples

- **Loading table data:**
  ```python
  data = fetch_data("SELECT id_barang, nama_barang, stok_saat_ini, stok_minimum FROM barang")
  for item in data:
      # build DataRow cells
  ```
- **Prediction call:**
  ```python
  hasil = predict_sales(id_barang)
  if isinstance(hasil, dict) and hasil["Status"].startswith("Wajib"):
      # render red status container
  ```

If anything is unclear (e.g., expected UI behavior, additional CRUD needs, deployment target), let me know and we’ll refine these instructions.
