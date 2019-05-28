from panda3d.core import (PNMImage, Filename, Texture)


def getImageFromFile(filename="sample.png"):
    image = PNMImage()
    image.read(Filename(filename))
    return image

def getTextureFromImage(pnmImage):
    print("myImage.getNumChannels(): ", pnmImage.getNumChannels())
    print("myImage.getXSize(): ", pnmImage.getXSize())
    print("myImage.getYSize(): ", pnmImage.getYSize())
    print("myImage.hasAlpha(): ", pnmImage.hasAlpha())

    # assign the PNMImage to a Texture (load PNMImage to Texture, opposite of store)
    myTexture = Texture()
    myTexture.load(pnmImage)
    return myTexture
