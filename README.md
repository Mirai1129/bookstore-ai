## 初始化專案

- uv
    ```bash
    uv sync
    ```
- pip

    ```bash
    python -m venv .venv
    source .\Scripts\activate
    pip install -r requirements.txt
    ```

## 運行專案

```bash
uvicorn main:app
```
