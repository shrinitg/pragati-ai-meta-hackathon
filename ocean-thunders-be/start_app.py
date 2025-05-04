import uvicorn

if __name__ == "__main__":
    uvicorn.run("oceanthundersbe:app", host='0.0.0.0', port=12345)
