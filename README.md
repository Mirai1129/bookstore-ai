## 初始化專案

1. 在專案最外層設定 `.env`。
  
    ```env
    MONGODB_CONNECTION_URL=
    DATABASE_NAME=bookbot
    
    ; Cloudinary settings
    CLOUDINARY_CLOUD_NAME=
    CLOUDINARY_API_KEY=
    CLOUDINARY_API_SECRET=
    
    ; App settings
    JWT_SECRET=
    API_SERVER_PORT=5000
    ```

2. 設定環境

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
