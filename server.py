from socket import *
import datetime
import time 
#File handling
def parseFile(fileName):
    data = {}
    #function to add songs with respective artists
    def addSong(song, artist):
        if artist not in data:
            data[artist] = []
        data[artist].append(song)
    
    with open(fileName, "r") as f: #using with to make sure file is closed
        
        overflow = False #if the song/artist takes up 2 lines
        currentSong = ""
        currentArtist = ""
        song = False #for use with overflow, states if its the song or the artist
        begin = False #will only begin adding to the dictionary when this is True
        for line in f:

            song = False
            if line[0].isnumeric(): #avoids un-numbered lines
                begin = True
                stuff = line.split("  ") #splits line into list with artist and song
                while len(stuff) != 3: #removes empty spaces until only useful elements remain
                    try:
                        stuff.remove('')
                    except ValueError: #if there is an overflow the remove function will fail
                        overflow = True
                        song = True
                        break
                    
                if len(stuff) == 3: #one exception in file with artist Lobo
                    if len(stuff[0].split("Lobo")) == 2:
                        currentSong = stuff[0][:34]
                        currentArtist = stuff[0][35:39]
                    else:
                        currentSong = stuff[0]
                        currentArtist = stuff[1]
                    
                
            if overflow: #if an overflow was found then account for it
                
                if song: #first overflow line is a song, will be changed in next loop
                    
                    currentSong = stuff[0].replace("\n","")
                else:
                    stuff = line.split("  ") #find the artist
                    while len(stuff) != 2:
                        stuff.remove('')
                        
                    currentArtist = stuff[0]
                    overflow = False

            if not overflow and begin: #adding songs when we're not overflowing
                for artist in currentArtist.split("/"): #if there are multiple artists
                    addSong(currentSong[4:].strip(),artist.strip())
            if currentSong[:3] == "100": #finish at 100th song
                break

    return data
#opening the log file and creating the function to append logs to the file
logFile = open("server.log", "a")

def log(message):
    print(message)
    timestamp = datetime.datetime.now()
    logFile.write(str(timestamp) + ": "+  message + "\n")
    logFile.flush()
#main server loop
def main():
    #defining host and port and reading in the file
    port = 2345 
    host = "localhost"
    songList = parseFile("100worst.txt")
    with socket(AF_INET, SOCK_STREAM) as sock: #socket will close once done(using with)
        #attmempt to bind 
        try:
            sock.bind((host,port))

        except Exception as e:
            log("Server failed to start because of {0}".format(e))
            return

        log("Server has started")
        #begin waiting for connections 
        sock.listen(1)
        connected = False #only try to accept connections when this is false
        while True:
            
            if not connected:
                #attempting to accept a connection
                log("Waiting for connection")
                try:

                    client, address = sock.accept()
                except Exception:
                    log("Connection from client failed to be received")
                    return
                connected = True
                log("connection received from {0}".format(address))
                #storing time connected for later use
                connectedTime = time.time()
            #attempting to recieve something from the client
            log("Waiting for input")
            try:
                artistRequest = client.recv(1024).decode()
            except Exception:
                log("Failed to receive artst request from client")
                return

            
            #checking if the client wants to quit
            if artistRequest.lower() == "quit":
                log("client wishes to quit")
                #attempting to close the connection and log the connection times
                try:
                    client.close()
                    connectionLength = time.time() - connectedTime
                    log("Client connection duration: "+str(connectionLength))
                except Exception as e:
                    log("Failed to close client socket")
                    return

                connected = False #allows another client to connect
                
            else:
                #if a request was made, server will handle it
                log("Artist request received with artist "+artistRequest)           

                songs = ""
                #creating a string of songs to send to the client
                
                try:
                    for song in songList[artistRequest]:
                        songs += "\n"+song        
                except KeyError: #if the artist is not a key in the dictionary
                    log("Client requested artist not in database") 

                #attempting to send a response to the client    
                try:
                    if not songs: # if no songs were found send this
                        client.send("No songs for that artist".encode())
                        
                    else:
                        client.send(songs.encode())  
                except Exception:
                    log("Client connection closed before sending response")
                    return

                log("Response sent to client")
        logFile.close()            
main()

                    
    
