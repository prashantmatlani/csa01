
#from server.app import main
import uvicorn
#import server.app
from server.app import app, main  # import both app object and main()

if __name__ == "__main__":
    #main()
    uvicorn.run("server.app:app", host="127.0.0.1", port=8000, reload=True)