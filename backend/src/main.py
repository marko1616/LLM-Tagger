from src.api import db, config

if __name__ == "__main__":
    import uvicorn

    db.init_db()
    uvicorn.run(
        "src.api:app",
        host=config.listen.split(":")[0],
        port=int(config.listen.split(":")[1]),
        reload=True,
    )
