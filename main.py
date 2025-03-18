from src.Routes.routes import app
if __name__ == "__main__":
    import uvicorn
    print("Server running at: 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
    

# READ ME

# This server uses fastapi to handle queries
# run it with:
# uvicorn main:app --reload
