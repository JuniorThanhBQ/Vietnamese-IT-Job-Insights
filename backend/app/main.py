from fastapi import FastAPI

app = FastAPI(title="Vietnamese IT Job Insights API")


@app.get("/health")
def health_check():
    return {"status": "ok"}
