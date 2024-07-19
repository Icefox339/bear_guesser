
from os import listdir, remove
from PIL import Image
stringus = "valid\\people"
for filename in listdir(stringus):
    if filename.endswith(".jpg"):   
        try:
            img = Image.open(stringus + "\\" + filename) # open the image file
            img.verify() # verify that it is, in fact an image
        except (IOError) as e:
            print("Bad file:", filename)
            remove(stringus + "\\" + filename)
            print("removed file", stringus + "\\" + filename)
print("good output")