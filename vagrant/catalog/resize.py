from PIL import Image
from resizeimage import resizeimage
import os

'''
Resize all .jpg files in current directory to 400x300 pixels,
new picture name will be: pic_{number}.jpg
'''
i = 0
for filename in os.listdir("./"):
    if filename.endswith(".jpg"):
        i = i + 1
        new_filename = "pic_"+str(i)+".jpg"
        try:
            # Try to resize the picture
            fd_img = open(filename, 'r')
            img = Image.open(fd_img)
            img = resizeimage.resize_contain(img, [400, 300])
            img.save(new_filename, img.format)
            fd_img.close()
            print "Resized %s into %s" % (filename, new_filename)
        except:
            # Could not resize, just use the uploaded file instead
            print "Couldn't resize %s, renamed it to %s" % (filename, new_filename)
            os.rename(filename, new_filename)
print "Processed %d files." % (i)