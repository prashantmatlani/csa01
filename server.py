
#from server.app import main
import uvicorn
import server.app

if __name__ == "__main__":
    #main()
    uvicorn.run("server.app:app", host="127.0.0.1", port=8000, reload=True)