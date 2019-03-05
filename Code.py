# Author: Muhammed Rahmetullah Kartal


import numpy as np
import time
import tkinter as tk
from tkinter.filedialog import *
from tkinter import messagebox
import copy
from PIL import Image, ImageTk
import csv
import pandas as pd


start_time = time.time()
iterationN = 0
NCC = 0
desired_width = 7000
np.set_printoptions(linewidth=desired_width)

flag = None

openedImage = None
openedImageName = None
binaryImage = None
borderedBinaryArray = None


algorithm = None
iterationAfterLev = 0
iterationAfterTSF = 0
NCCafterLev = 0
NCCafterTSF = 0
outputOfLev = []
outputOfTSF = []


def createBinaryImg(nrow,ncol,Value):
#creates a binary image with size nrow x ncol with pixel values Value
    x, y = np.indices((nrow, ncol))
    mask_lines = np.zeros(shape=(nrow,ncol))

    x0, y0, r0 = 30, 30, 10
    x2, y2, r2 = 70, 30, 10


    for i in range (50, 70):
        mask_lines[i][i] = 255
        mask_lines[i][i + 1] = 255
        mask_lines[i][i + 2] = 255
        mask_lines[i][i + 3] = 255
        mask_lines[i][i + 6] = 255

    mask_circle1 = np.abs((x - x0) ** 2 + (y - y0) ** 2 - r0 ** 2 ) <= 5
    # mask_square1 = np.fmax(np.absolute( x - x1), np.absolute( y - y1)) <= r1
    mask_square2 = np.fmax(np.absolute( x - x2), np.absolute( y - y2)) <= r2
    #mask_square3 = np.fmax(np.absolute( x - x3), np.absolute( y - y3)) <= r3
    #mask_square4 =  np.fmax(np.absolute( x - x4), np.absolute( y - y4)) <= r4
    imge = np.logical_or ( np.logical_or(mask_lines, mask_circle1), mask_square2) * Value
    # imge = np.logical_or(mask_lines, mask_square2) * Value
    # imge =  mask_square2 * Value

    return imge

#This method prints an array
def printImgArray(imgArray):
    for i in imgArray:
        print(i)

#This method writes current iteration number and number of conic components of levialdi algorithm to canvas 3.
def writeIterToScreenLEV():
    #deleting the 1vTag tagged elements of canvas 3, so we can rewrite NCC and iterationN
    c3.select_clear()
    c3.delete("lvTag")

    #rewriting NCC and iterationN to correct position on canvas 3.
    c3.create_text(fixedCanvasWidth/2+fixedCanvasWidth/7, fixedCanvasHeight/2.17223, text=iterationN, font=("Ariel", int((xSize+ySize)/125), "bold"), tag="lvTag", anchor=NW)
    c3.create_text(fixedCanvasWidth/2-fixedCanvasWidth/5.5, fixedCanvasHeight/2+fixedCanvasHeight/10.95238, text=NCC, font=("Ariel", int((xSize+ySize)/125), "bold"), tag="lvTag", anchor=NW)

    #this flag checks for "Done" command if flag is False we are writing Done onto canvas 3.
    #the flag is controlled in levialdi algorithm.
    if flag == False:
        c3.create_text(fixedCanvasWidth/2+fixedCanvasWidth/3.333334, fixedCanvasHeight/2+fixedCanvasWidth/3, text="Done", font=("Ariel", int((xSize+ySize)/125), "bold"), tag="lvTag", anchor=CENTER)

    #updating canvas 3.
    c3.update()


#This method writes current iteration number and number of conic components of TSF algorithm to canvas 6.
def writeIterToScreenTSF():
    # deleting the 1vTag tagged elements of canvas 6, so we can rewrite NCC and iterationN
    c6.select_clear()
    c6.delete("lvTag")

    # rewriting NCC and iterationN to correct position on canvas 6.
    c6.create_text(fixedCanvasWidth/2+fixedCanvasWidth/7, fixedCanvasHeight/2.17223, text=iterationN, font=("Ariel", int((xSize+ySize)/125), "bold"), tag="lvTag", anchor=NW)
    c6.create_text(fixedCanvasWidth/2-fixedCanvasWidth/5.5, fixedCanvasHeight/2+fixedCanvasHeight/10.95238, text=NCC, font=("Ariel", int((xSize+ySize)/125), "bold"), tag="lvTag", anchor=NW)

    # this flag checks for "Done" command if flag is False we are writing Done onto canvas 3.
    # the flag is controlled in TSF algorithm.
    if flag == False:
        c6.create_text(fixedCanvasWidth/2+fixedCanvasWidth/3.333334, fixedCanvasHeight/2+fixedCanvasWidth/3, text="Done", font=("Ariel", int((xSize+ySize)/125), "bold"), tag="lvTag", anchor=CENTER)

    # updating canvas 6.
    c6.update()


#This method writes the binary array of levialdi algorithm to the canvas 2.
def writeBinaryToScreenLEV(imgArray):
    fontSize = 3 #fontsize of every single element of array.

    #deleting the canvas 2's 1vTag tagged contents to rewrite array.
    c2.select_clear()
    c2.delete("lvTag")

    #rewriting array's contents to canvas 2.
    c2.create_text(fixedCanvasWidth/2,fixedCanvasHeight/2, text=createPixelMap(imgArray), font=("Ariel", fontSize, "bold"), tag="lvTag",anchor=CENTER)

    #updating canvas 2's contents.
    c2.update()


def writeBinaryToScreenTSF(imgArray):
    fontSize = 3#fontsize of every single element of array.

    # deleting the canvas 5's 1vTag tagged contents to rewrite array.
    c5.select_clear()
    c5.delete("lvTag")

    # rewriting array's contents to canvas 5.
    c5.create_text(fixedCanvasWidth/2,fixedCanvasHeight/2, text=createPixelMap(imgArray), font=("Ariel", fontSize, "bold"), tag="lvTag", anchor=CENTER)

    # updating canvas 5's contents.
    c5.update()


#This method converts an image array to a string for writing it into a canvas.
def createPixelMap(imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    temp = imgArray
    pixelMap = ""
    for row in range(rows):
        for col in range(cols):
            #I used 0 and 255's in my code so for better view of array converted 255s to 1s.
            if imgArray[row][col] == 255:
                imgArray[row][col] = 1

            pixelMap += str(int(temp[row][col]))

            #After adding 1s to string again converting them to 255s
            if imgArray[row][col] == 1:
                imgArray[row][col] = 255

        pixelMap += "\n" #adding string a new line after every row.
    return pixelMap


#This method converts numpy array to a PIL image
def arrayToImage(im):
    img = Image.fromarray(np.uint8(im))
    return img

#This method converts PIL image to a numpy array.
def imgToArray(img):
    imgArray = np.array(img).astype(int)
    return imgArray

#This method converts a RGB image to Gray image.
def colorToGray(img):
    img_gray = img.convert('L')
    return img_gray


#This method converts Gray image to Binary image
def grayToBinary(img):
    # Check whether if pixel is less than 150 then make it 0 else make it 255
    imgBinary = img.point(lambda x: 0 if x < 150 else 255)  # this img.point function maps the image through a lookup function.
    return imgBinary

#This method is for selecting another image on GUI, it resets the content.
def reset():
    pass


#This method adds a 1x black border around of a 2D array.
def borderArray(imgArray):

    #original row and column numbers.
    nrows = len(imgArray)
    ncols = len(imgArray[0])

    borderedImageArray = np.zeros([nrows + 2, ncols + 2]) #creating a zeroes to add borders

    #Transferring the content of our array to zeroes array.
    for i in range(0, nrows):
        for j in range(0, ncols):
            borderedImageArray[i + 1][j + 1] = imgArray[i][j]
    return borderedImageArray




###################################################################################################################################
#########################################################LEVIALDI ALGORITHM########################################################
###################################################################################################################################



#The levialdi algorithm search every pixel of an image and checks the left, bottom-left and bottom sides of that pixel.
#It has 1 deletion and 1 augmentation condition.
#It counts number of conic components by changing elements bottom left to top right.
#To change and control pixels we need to use a binary image.
#On every iteration we are looking for the last version of our array.
def levialdi(imgArray):
    try:
        #Global Variables
        global flag, NCC, iterationN, iterationAfterLev, NCCafterLev, outputOfLev, algorithm

        nrows = len(imgArray) - 2 #Number of rows without borders.
        ncols = len(imgArray[0]) - 2 #Number of columns without borders.

        outputOfLev = [] #Array of outputs to write CSV file.

        iterationAfterLev = 0 #Iteration number after levialdi algorithm to use in GUI and CSV.
        NCCafterLev = 0 #NCC number after levialdi algorithm to use in GUI and CSV.

        NCC = 0 #Reseting the value of NCC at the start of algorithm.
        iterationN = 0 #Reseting the value of iteration number at the start of algorithm.

        #To print first array on GUI after all iterations.
        firstArray = copy.deepcopy(imgArray) #Deep copying the content of array to a temp array.

        while True:
            #These flags are for breaking the while on no change situation.
            flag = False
            flagCheck = False

            # We are going to check that array for the next iteration.
            tempArray = copy.deepcopy(imgArray) #Deep copying the content of array to a temp array.

            #Single Iteration
            #Start checking from right top corner.
            for i in range(1, nrows + 1):
                for j in range(ncols, 0, -1):

                    #Isolated point.
                    #If point is isolated increase NCC.
                    if (imgArray[i][j + 1] == 0 and imgArray[i][j - 1] == 0
                            and (imgArray[i + 1][j] == 0
                                 and imgArray[i - 1][j] == 0)
                            and (imgArray[i + 1][j + 1] == 0
                                 and imgArray[i + 1][j - 1] == 0)
                            and (imgArray[i - 1][j + 1] == 0
                                 and imgArray[i - 1][j - 1] == 0)
                            and (imgArray[i][j] == 255)):
                        NCC = NCC + 1

                    #Deletion condition.
                    if imgArray[i + 1][j - 1] == 0 and imgArray[i][j - 1] == 0 and imgArray[i + 1][j] == 0 and imgArray[i][
                        j] == 255:
                        tempArray[i][j] = 0
                        flagCheck = True

                    #Augmentation condition.
                    elif imgArray[i + 1][j] == 255 and imgArray[i][j - 1] == 255 and imgArray[i][j] == 0:
                        tempArray[i][j] = 255
                        flagCheck = True


            #If there is a change make flag True
            if flagCheck:
                flag = True

            imgArray = tempArray
            writeBinaryToScreenLEV(imgArray)
            writeIterToScreenLEV()

            #If there is no change break the loop.
            if flag == False:
                break

            iterationN += 1

        #Outputs for using in CSV.
        iterationAfterLev = iterationN
        NCCafterLev = NCC
        algorithm = "LEV"

        outputOfLev.append(openedImageName)
        outputOfLev.append(nrows)
        outputOfLev.append(ncols)
        outputOfLev.append(NCCafterLev)
        outputOfLev.append(iterationAfterLev)

        writeBinaryToScreenLEV(firstArray)
    except:
        print("Please upload a file")




###################################################################################################################################
###########################################################TSF ALGORITHM###########################################################
###################################################################################################################################




#This method finds the B,C,T and numberOfConnectedZeroes to use in TSF
def neighbors(imgArray, i, j):
    B = 0 #The number of 255’s in p’s 8-neighborhood
    C = 0 #The number of distinct 8-connected components of 255’s in p’s 8-neighborhood
    T = 0 #The number of 0-255 transitions in p’s neighborhood
    connectedZeroCounter = 0
    neighbours = []

    #Adding 8 connected neighbours to an array
    neighbours.append(imgArray[i - 1][j - 1]) #p1
    neighbours.append(imgArray[i - 1][j]) #p2
    neighbours.append(imgArray[i - 1][j + 1]) #p3
    neighbours.append(imgArray[i][j + 1]) #p4
    neighbours.append(imgArray[i + 1][j + 1]) #p5
    neighbours.append(imgArray[i + 1][j]) #p6
    neighbours.append(imgArray[i + 1][j - 1]) #p7
    neighbours.append(imgArray[i][j - 1]) #p8

    #### CONNECTED ZEROES ####

    #At first we are looking for p8 and p0 if they are both 0 increase counter 1
    if neighbours[7] == 0 and neighbours[0] == 0:
        connectedZeroCounter += 1

    #Then check for is p(i) and p(i+1) 0 if they are increase counter 1
    #3 connection is enough for us, so we are breaking the loop if its 3.
    for a in range(len(neighbours)):
        if connectedZeroCounter == 3:
            break
        if neighbours[a] == 0:
            connectedZeroCounter += 1
        else:
            connectedZeroCounter += 0

    #### B  ####

    #To count number of 1s in 8 connected array we are looking for p(i) and p(i+1)
    for a in range(len(neighbours)):
        if neighbours[a] == 255:
            B += 1

    #### T  #####

    #To count 0 to 1 changes we are looking for p(i) is 0 and p(i+1) is 255 situation
    #After all we are looking for p8 and p0 again outside of loop
    for a in range(len(neighbours) - 1):
        if neighbours[a] == 0 and neighbours[a + 1] == 255:
            T += 1

    if neighbours[7] == 0 and neighbours[0] == 255:
        T += 1

    #### C ####

    #To count C easily we are looking for corners of a pixel if 1 corner is between 255s we are converting the value of it to 255
    #After that we are looking for 0 to 255 changes
    temp = neighbours

    if temp[7] == 255 and temp[1] == 255:
        neighbours[0] = 255
    if temp[1] == 255 and temp[3] == 255:
        neighbours[2] = 255
    if temp[3] == 255 and temp[5] == 255:
        neighbours[4] = 255
    if temp[5] == 255 and temp[7] == 255:
        neighbours[6] = 255

    #A special case: if pixel is surrounded by 255s that means it has 1 chain of connected 255s
    cFlag = True
    for b in neighbours:
        if b != 255:
            cFlag = False

    if cFlag == True:
        C = 1

    for b in range(len(neighbours) - 1):
        if neighbours[b] == 0 and neighbours[b + 1] == 255:
            C += 1
    if neighbours[7] == 0 and neighbours[0] == 255:
        C += 1

    #### RETURN ####
    return B, C, T, connectedZeroCounter


#The TSF algorithm search every pixel but in two subfields
#First subfield is for odd row odd columns even row even columns
#Second subfield is for odd row even columns even row odd columns
#It has 3 connected deletion , 2 connected augmentation conditions
#It counts number of conic components by changing elements bottom left , top left to right center of every conic component.
#To change and control pixels we need to use a binary image.
#On every iteration we are looking for the last version of our array.
def TSF(imgArray):
    try:
        #Global variables
        global flag, NCC, iterationN, iterationAfterTSF, NCCafterTSF, outputOfTSF, algorithm

        nrows = len(imgArray) - 2 #Row number without border
        ncols = len(imgArray[0]) - 2 #Column number without border

        NCC = 0 #Reseting the value of NCC at the start of algorithm.
        iterationN = 0 #Reseting the value of iteration number at the start of algorithm.

        #Outputs
        NCCafterTSF =0
        iterationAfterTSF = 0
        outputOfTSF = []

        #Temp array to print first array at the end
        firstArray = copy.deepcopy(imgArray)


        while True:

            #Flags for checking no change in other words to break loop.
            flag = False
            flagCheck = False

            tempArray = copy.deepcopy(imgArray) #Temp array for using on next iteration

            #Odd row odd column even row even column for loop.
            for i in range(1, nrows + 1):
                if i % 2 == 1:
                    k = 1
                else:
                    k = 2
                for j in range(k, ncols + 1, 2):
                    B, C, T, connectedZeroCounter = neighbors(imgArray, i, j) #getting B,C,T,CZC of current pixel.

                    #Deletion conditions
                    if imgArray[i][j] == 255:
                        #Isolated point
                        if B == 0:
                            NCC += 1
                            tempArray[i][j] = 0
                            flagCheck = True
                        elif C == 1:
                            if B == 1:
                                if imgArray[i - 1][j - 1] == 0 and imgArray[i + 1][j - 1] == 0:
                                    if connectedZeroCounter == 3:
                                        tempArray[i][j] = 0
                                        flagCheck = True
                            else:
                                if connectedZeroCounter == 3:
                                    tempArray[i][j] = 0
                                    flagCheck = True

                    #Augmentation conditions
                    else:
                        if C == 1:
                            if imgArray[i][j - 1] == 255 and imgArray[i - 1][j] == 255:
                                tempArray[i][j] = 255
                                flagCheck = True
                            elif imgArray[i][j - 1] == 255 and imgArray[i + 1][j] == 255:
                                tempArray[i][j] = 255
                                flagCheck = True

            imgArray = tempArray
            tempArray = copy.deepcopy(imgArray)

            # Odd row even column even row odd column for loop.
            for i in range(1, nrows + 1):
                if i % 2 == 0:
                    k = 1
                else:
                    k = 2
                for j in range(k, ncols + 1, 2):
                    B, C, T, connectedZeroCounter = neighbors(imgArray, i, j)

                    if imgArray[i][j] == 255:
                        if B == 0:
                            NCC += 1
                            flagCheck = True
                            tempArray[i][j] = 0
                        elif C == 1:
                            if B == 1:
                                if imgArray[i - 1][j - 1] == 0 and imgArray[i + 1][j - 1] == 0:
                                    if connectedZeroCounter == 3:
                                        tempArray[i][j] = 0
                                        flagCheck = True
                            else:
                                if connectedZeroCounter == 3:
                                    tempArray[i][j] = 0
                                    flagCheck = True

                    else:
                        if C == 1:
                            if imgArray[i][j - 1] == 255 and imgArray[i - 1][j] == 255:
                                tempArray[i][j] = 255
                                flagCheck = True
                            elif imgArray[i][j - 1] == 255 and imgArray[i + 1][j] == 255:
                                tempArray[i][j] = 255
                                flagCheck = True


            #If there is change don't break
            if flagCheck:
                flag = True

            imgArray = tempArray
            writeBinaryToScreenTSF(imgArray)
            writeIterToScreenTSF()

            #If there is no change break the while loop.
            if flag == False:
                break
            iterationN += 1

        #outputs
        algorithm = "TSF"
        iterationAfterTSF = iterationN
        NCCafterTSF = NCC

        outputOfTSF.append(openedImageName)
        outputOfTSF.append(nrows)
        outputOfTSF.append(ncols)
        outputOfTSF.append(NCCafterTSF)
        outputOfTSF.append(iterationAfterTSF)


        writeBinaryToScreenTSF(firstArray)
    except:
        print("Please upload a file")


########################################################################################################################################

def selectImage():
    openFileFormats = (("PNG Files", "*.png"), ("JPG Files", "*.jpg"), ("JPEG Files", "*.jpeg"))  # Image file formats
    path = askopenfilename(parent=window, filetypes=openFileFormats)  # Asking for file
    fp = open(path, "rb")  # Read file as a byte map
    return fp


messageBoxAskedImage = False

def openImage():
    #global variables
    global openedImage, openedImageName, borderedBinaryArray, messageBoxAskedImage

    if messagebox.askyesno("Question", "Do you want to select a Image File ?") == True:
        openedImage = Image.open(selectImage())
        openedImageName = openedImage.fp.name.split("/")[-1]
    else:
        openedImageArray = createBinaryImg(100, 100, 255)
        openedImageName = "Created"
        openedImage = arrayToImage(openedImageArray)

    grayImage = colorToGray(openedImage)
    grayImageArray = imgToArray(grayImage)
    borderedGrayImageArray = borderArray(grayImageArray)
    borderedGrayImage = arrayToImage(borderedGrayImageArray)

    borderedBinaryImage = grayToBinary(borderedGrayImage)
    borderedBinaryArray = imgToArray(borderedBinaryImage)

    #Putting images to GUI
    c1.image = ImageTk.PhotoImage(openedImage)
    c1.create_image(fixedCanvasWidth/2,fixedCanvasHeight/2, image=c1.image, anchor=CENTER)

    writeBinaryToScreenLEV(borderedBinaryArray)
    writeBinaryToScreenTSF(borderedBinaryArray)

    c4.image = ImageTk.PhotoImage(borderedBinaryImage)
    c4.create_image(fixedCanvasWidth/2,fixedCanvasHeight/2, image=c4.image, anchor=CENTER)

    #reseting if the new image
    reset()


#Calling method levialdi method for button.
def callLevialdi():
    try:
        levialdi(borderedBinaryArray)
    except Exception as ex:
        print(ex)

#Calling method of TSF for button
def callTSF():
    try:
        TSF(borderedBinaryArray)
    except Exception as ex:
        print(ex)


########################################################################################################################################

counter = 0 #Counter for is it the first save
messageBoxAskedCSV = False
path = None


#This method is for selecting CSV file.
def selectCSVFile():
    openFileFormats = (("CSV Files","*.csv"),("Excel Files", "*.xlsx"),("ALL Files","*.*"))  # File formats for easy search
    path = askopenfilename(parent=window, filetypes=openFileFormats)  # Basic file pick gui
    return path

#This method is for writing outputs to selected or a new CSV file.
def writeToCSV():
    global counter, messageBoxAskedCSV, path

    if messageBoxAskedCSV == False:
        if messagebox.askyesno("Question", "Do you want to select a CSV File ?") == True:
            path = selectCSVFile() #Selecting CSV file.
            messageBoxAskedCSV = True

        else:
            with open("Outputs.csv", 'a'): #Opening a empty CSV file
                path = "Outputs.csv"
                messageBoxAskedCSV = True

    checkEmptyFile=True
    try:
        df = pd.read_csv(path)
        checkEmptyFile = df.empty
    except:
        pass


    with open(path, 'a') as writeFile:
        fieldnames = ["File Name", "Image Size", "NCC", "Iteration Number", "Algorithm"]
        writer = csv.DictWriter(writeFile, fieldnames=fieldnames)
        if counter == 0 and checkEmptyFile:
             writer.writeheader()
        if algorithm == "LEV":
             writer.writerow(
                  {"File Name": outputOfLev[0], "Image Size": str(outputOfLev[1]* outputOfLev[2]),
                 "NCC": outputOfLev[3],
                  "Iteration Number": outputOfLev[4], "Algorithm": "LEV"})
        elif algorithm == "TSF":
             writer.writerow(
                 {"File Name": outputOfTSF[0], "Image Size": str(int(outputOfTSF[1])* int(outputOfTSF[2])),
                   "NCC": outputOfTSF[3],
                   "Iteration Number": outputOfTSF[4], "Algorithm": "TSF"})

    counter += 1



########################################################################################################################################

#These methods are for selecting resolution of GUI

def x640480():
    # changing the value of xSize and ySize
    global xSize,ySize
    xSize=640
    ySize=480
    window1.destroy() #destroying the resolution selection window.


def x720576():
    global xSize,ySize

    xSize=720
    ySize=576
    window1.destroy()


def x800600():
    global xSize,ySize

    xSize=800
    ySize=600
    window1.destroy()


def x1024768():
    global xSize,ySize

    xSize=1024
    ySize=768
    window1.destroy()


def x12801024():
    global xSize,ySize

    xSize=1280
    ySize=1024
    window1.destroy()


def x14401080():
    global xSize,ySize

    xSize=1440
    ySize=1080
    window1.destroy()


def x19201080():
    global xSize,ySize

    xSize=1920
    ySize=1080
    window1.destroy()

########################################################################################################################################

#Resolution select window.
window1 = tk.Tk()
window1.geometry("280x168")
window1.title("Resolution Select")
window1.configure(bg="White")


#This method adds buttons to resolution select window.
def selectResolution():

    Button1 = Button(window1, text='640x480', borderwidth=1, command=x640480, relief=RAISED)
    Button1.configure(width=40,height=1)
    Button1.grid(row=1, column=0, sticky=NW)

    Button2 = Button(window1, text='720x576', borderwidth=1, command=x720576, relief=RAISED)
    Button2.configure(width=40, height=1)
    Button2.grid(row=2, column=0, sticky=NW)

    Button3 = Button(window1, text='800x600', borderwidth=1, command=x800600, relief=RAISED)
    Button3.configure(width=40, height=1)
    Button3.grid(row=3, column=0, sticky=NW)

    Button4 = Button(window1, text='1024x768', borderwidth=1, command=x1024768, relief=RAISED)
    Button4.configure(width=40, height=1)
    Button4.grid(row=4, column=0, sticky=NW)

    Button5 = Button(window1, text='1280x1024', borderwidth=1, command=x12801024, relief=RAISED)
    Button5.configure(width=40, height=1)
    Button5.grid(row=5, column=0, sticky=NW)

    Button6 = Button(window1, text='1440x1080', borderwidth=1, command=x14401080, relief=RAISED)
    Button6.configure(width=40, height=1)
    Button6.grid(row=6, column=0, sticky=NW)

    Button7 = Button(window1, text='1920x1080', borderwidth=1, command=x19201080, relief=RAISED)
    Button7.configure(width=40, height=1)
    Button7.grid(row=7, column=0, sticky=NW)

selectResolution() #calling button adder

window1.mainloop() #running the resolution select window.


#creating the main window for our program
window = tk.Tk()
size = str(xSize) + "x" + str(ySize)
window.geometry(size)
window.title("Tkinter")
window.configure(bg='white')

#height and width of every canvas depending on resolutions.
fixedCanvasWidth = xSize/3-xSize/27
fixedCanvasHeight = ySize/2-ySize/12
############################################################################################################################################



fileButton = Button(window, text='File', borderwidth=1, command=openImage, relief=RAISED)
fileButton.grid(row=0, column=0, sticky=NW)



############################################################################################################################################

#Single Canvas

#Creating a frame for adding scroolbar to it
frame1=Frame(window,width=fixedCanvasWidth,height=fixedCanvasHeight)
frame1.grid(row=1,column=0)

#Creating a canvas and putting frame to it
c1 = Canvas(frame1,bg="white", width=fixedCanvasWidth,height=fixedCanvasHeight, relief="groove", bd=5,scrollregion=(-1500,-1500,1500,1500))
# c1.grid(row=1, column=0)

#Scroolbar adding
hbar=Scrollbar(frame1,orient=HORIZONTAL)
hbar.pack(side=BOTTOM,fill=X)
hbar.config(command=c1.xview)
vbar=Scrollbar(frame1,orient=VERTICAL)
vbar.config(command=c1.yview)
vbar.pack(side=RIGHT,fill=Y)
c1.config(width=fixedCanvasWidth,height=fixedCanvasHeight)
c1.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
c1.pack(side=LEFT,expand=True,fill=BOTH)


############################################################################################################################################

#Single Canvas

frame2 = Frame(window,width=fixedCanvasWidth,height=fixedCanvasHeight)
frame2.grid(row=1,column=1)

c2 = Canvas(frame2,bg="white", width=fixedCanvasWidth,height=fixedCanvasHeight, relief="groove", bd=5,scrollregion=(-3000,-3000,3000,3000))
# c2.grid(row=1, column=1)

hbar=Scrollbar(frame2,orient=HORIZONTAL)
hbar.pack(side=BOTTOM,fill=X)
hbar.config(command=c2.xview)
vbar=Scrollbar(frame2,orient=VERTICAL)
vbar.config(command=c2.yview)
vbar.pack(side=RIGHT,fill=Y)
c2.config(width=fixedCanvasWidth,height=fixedCanvasHeight)
c2.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
c2.pack(side=LEFT,expand=True,fill=BOTH)


############################################################################################################################################

#Single Canvas

frame4 = Frame(window,width=fixedCanvasWidth,height=fixedCanvasHeight)
frame4.grid(row=2,column=0)

c4 = Canvas(frame4,bg="white",width=fixedCanvasWidth,height=fixedCanvasHeight, relief="groove", bd=5,scrollregion=(-1500,-1500,1500,1500))
# c4.grid(row=2, column=0)

hbar=Scrollbar(frame4,orient=HORIZONTAL)
hbar.pack(side=BOTTOM,fill=X)
hbar.config(command=c4.xview)
vbar=Scrollbar(frame4,orient=VERTICAL)
vbar.config(command=c4.yview)
vbar.pack(side=RIGHT,fill=Y)
c4.config(width=fixedCanvasWidth,height=fixedCanvasHeight)
c4.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
c4.pack(side=LEFT,expand=True,fill=BOTH)


############################################################################################################################################

#Single Canvas

frame5 = Frame(window,width=fixedCanvasWidth,height=fixedCanvasHeight)
frame5.grid(row=2,column=1)

c5 = Canvas(frame5,bg="white", width=fixedCanvasWidth,height=fixedCanvasHeight, relief="groove", bd=5,scrollregion=(-3000,-3000,3000,3000))
# c5.grid(row=2, column=1)

hbar=Scrollbar(frame5,orient=HORIZONTAL)
hbar.pack(side=BOTTOM,fill=X)
hbar.config(command=c5.xview)
vbar=Scrollbar(frame5,orient=VERTICAL)
vbar.config(command=c5.yview)
vbar.pack(side=RIGHT,fill=Y)
c5.config(width=fixedCanvasWidth,height=fixedCanvasHeight)
c5.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
c5.pack(side=LEFT,expand=True,fill=BOTH)


############################################################################################################################################

#Single Canvas

#Creating canvas
c3 = Canvas(bg="white",width=fixedCanvasWidth,height=fixedCanvasHeight, relief="groove", bd=5)
c3.config(width=fixedCanvasWidth,height=fixedCanvasHeight)
c3.grid(row=1, column=2)

#Creating buttons

levialdiButton = Button(c3, text='LevialdiCall', borderwidth=1, command=callLevialdi, relief=RAISED, bg="Beige")
levialdiButton.place(x=fixedCanvasWidth / 2 - fixedCanvasWidth / 5, y=fixedCanvasHeight / 2 - fixedCanvasWidth / 8, anchor=CENTER)

levialdiButtonSave = Button(c3, text='Save', borderwidth=1, command=writeToCSV, relief=RAISED, bg="Beige")
levialdiButtonSave.place(x=fixedCanvasWidth / 2 + fixedCanvasWidth / 5, y=fixedCanvasHeight / 2 - fixedCanvasWidth / 8, anchor=CENTER)


#Creating the texts of canvas
c3.create_text(fixedCanvasWidth/2,fixedCanvasHeight/2-fixedCanvasHeight/3.83334, text="Levialdi", font=("Ariel", int((xSize+ySize)/93.75), "bold"))
c3.create_text(fixedCanvasWidth/2-fixedCanvasWidth/10,fixedCanvasHeight/2, text="Iteration Number: ", font=("Ariel", int((xSize+ySize)/125), "bold"))
c3.create_text(fixedCanvasWidth/2-fixedCanvasWidth/3.87096,fixedCanvasHeight/2+fixedCanvasHeight/7.66667, text="NCC: ", font=("Ariel", int((xSize+ySize)/125), "bold"))

############################################################################################################################################

#Single Canvas

#Creating canvas
c6 = Canvas(bg="white",width=fixedCanvasWidth,height=fixedCanvasHeight, relief="groove", bd=5)
c6.grid(row=2, column=2)

#Creating buttons

TSFButton = Button(c6, text='TSFCall', borderwidth=1, command=callTSF, relief=RAISED,bg="Beige")
TSFButton.place(x=fixedCanvasWidth / 2 - fixedCanvasWidth / 5, y=fixedCanvasHeight / 2 - fixedCanvasWidth / 8, anchor=CENTER)


TSFButtonSave = Button(c6, text='Save', borderwidth=1, command=writeToCSV, relief=RAISED, bg="Beige")
TSFButtonSave.place(x=fixedCanvasWidth / 2 + fixedCanvasWidth / 5, y=fixedCanvasHeight / 2 - fixedCanvasWidth / 8, anchor=CENTER)

#Creating the texts of canvas
c6.create_text(fixedCanvasWidth/2,fixedCanvasHeight/2-fixedCanvasHeight/3.83334, text="TSF", font=("Ariel", int((xSize+ySize)/93.75), "bold"))
c6.create_text(fixedCanvasWidth/2-fixedCanvasWidth/10,fixedCanvasHeight/2, text="Iteration Number: ", font=("Ariel", int((xSize+ySize)/125), "bold"))
c6.create_text(fixedCanvasWidth/2-fixedCanvasWidth/3.87096,fixedCanvasHeight/2+fixedCanvasHeight/7.66667, text="NCC: ", font=("Ariel", int((xSize+ySize)/125), "bold"))


window.mainloop()
