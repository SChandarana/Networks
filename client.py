from socket import *
import datetime
import time

#defining host and port(must be same as server

host ='127.0.0.1'
port = 2345

#opening the log file and creating the function to append logs to the file
logFile = open("client.log","a")

def log(message,ifShow = False): #message will be shown to user if ifShow = True
    if ifShow:
        print(message)
    timestamp = datetime.datetime.now()
    logFile.write(str(timestamp) + ": "+  message + "\n")
    logFile.flush()
    


#the main loop

def main():
    with socket(AF_INET,SOCK_STREAM) as sock:
        #attempting to connect to the server            
        try:
            sock.connect((host,port))
            
        except Exception:
            log("Failed to establish server connection",True)
            return

        log("Connection successful",True)
        #input request loop, will do this until user quits
        while True:
            artistRequest = input("Enter name of artist(or quit): ")
            #loop to make sure input isn't empty
            while artistRequest == "":
                print("Empty input received, please try again")
                artistRequest = input("Enter name of artist(or quit): ")
            if artistRequest.lower() =="quit":
                log("Client requests to close connection")
            else:
                log("Sending response to server",True)
            #attempting to send artistRequest(or quit)
            try:
                sock.send(artistRequest.encode())
            except Exception:
                log("Could not send artist Request",True)
                return
            log("Response Sent",True)
            #storing the time sent so it can be used to calculate response time
            sentTime = time.time()
            #attempting to receive the response from the server
            try:
                songs = sock.recv(4096)
            except Exception:
                log("Failed to recieve response from server", True)
                return
            #if user has not chosen to quit, client will return songs
            if artistRequest.lower() != "quit":
                print("server returned: ",songs.decode())   
                duration = time.time() - sentTime
                #logging the necessary data
                log("response recieved")
                log("response was {0} bytes".format(len(songs)))
                log("response time was {0}".format(duration))
            else:
                #once user has quit, breaks out of loop
                log("connection closed",True)
                break

            
        #closing sockets and file 
        sock.close()
        logFile.close()
main()
