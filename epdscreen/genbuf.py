from PIL import Image
import os, glob, zlib, sys
from io import BytesIO
# Display resolution
EPD_WIDTH       = 800
EPD_HEIGHT      = 480
dwidth = EPD_WIDTH
dheight = EPD_HEIGHT


def getbuffer(image):
    # Create a pallette with the 7 colors supported by the panel
    pal_image = Image.new("P", (1,1))
    pal_image.putpalette( (0,0,0,  255,255,255,  0,255,0,   0,0,255,  255,0,0,  255,255,0, 255,128,0) + (0,0,0)*249)

    # Check if we need to rotate the image
    imwidth, imheight = image.size
    if(imwidth == dwidth and imheight == dheight):
        image_temp = image
    elif(imwidth == dheight and imheight == dwidth):
        print("Rotating image")
        image_temp = image.rotate(90, expand=True)
    else:
        print("Invalid image dimensions: %d x %d, expected %d x %d" % (imwidth, imheight, dwidth, dheight))

    # Convert the soruce image to the 7 colors, dithering if needed
    image_7color = image_temp.convert("RGB").quantize(palette=pal_image)
    buf_7color = bytearray(image_7color.tobytes('raw'))

    # PIL does not support 4 bit color, so pack the 4 bits of color
    # into a single byte to transfer to the panel
    buf = [0x00] * int(dwidth * (dheight / 2))
    idx = 0
    for i in range(0, len(buf_7color), 2):
        buf[idx] = (buf_7color[i] << 4) + buf_7color[i+1]
        idx += 1
        
    return buf

def writebuf(buf, filename="image2"):
    with open(filename+".py", "w") as f:
        f.write(
            "image = %r\n" %
            buf
        )
def writebin(buf, filename="image"):
    # Ensure output directory exists
    out_dir = os.path.join(".", "bins")
    os.makedirs(out_dir, exist_ok=True)
    output_path = os.path.join(out_dir, filename+".bin")

    with open(output_path, "wb") as f:
        for b in buf:
            f.write(bytes([b & 0xff]))
    
    print("Wrote bin file to:", output_path)

def readbin(filename="image"):
    out_dir = os.path.join(".", "bins")
    output_path = os.path.join(out_dir, filename+".bin")

    with open(output_path, "rb") as f:
        buf = f.read()
    
    for i in range(3):
        print(buf[i])
    print(len(buf))
    print(type(buf))


wbits = 9


def writezlib(buf, filename="image"):
    with BytesIO() as f:
        for b in buf:
            f.write(bytes([b & 0xff]))
        f.seek(0)
        with open(filename+".zlib", "wb") as g:
            compressor = zlib.compressobj(wbits=wbits)
            compressed = compressor.compress(f.read())
            compressed += compressor.flush()
            g.write(compressed)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python genbuf.py <image_filename>")
        sys.exit(1)

    # Build the input file path: image must be inside the ./bmps folder
    image_filename = sys.argv[1]

    if image_filename != "all":
        in_path = os.path.join(".", "bmps", image_filename)
        if not os.path.isfile(in_path):
            print("File not found:", in_path)
            sys.exit(1)
        # Open image and generate buffer
        try:
            img = Image.open(in_path)
        except Exception as e:
            print("Error opening image:", e)
            sys.exit(1)
        buf = getbuffer(img)
        base_name = os.path.splitext(image_filename)[0]
        writebin(buf, base_name)
        readbin(image_filename[:-4])
    else:
        pass
        # bmps = glob.glob("./bmps/*.bmp")
        # for bmp in bmps:
        #     buf = getbuffer(Image.open(bmp))
        #     writebin(buf, bmp[:-4])
        #     readbin(bmp[:-4])

        # pngs = glob.glob("./bmps/*.png")
        # for png in pngs:
        #     buf = getbuffer(Image.open(png))
        #     writebin(buf, png[:-4])
        #     readbin(png[:-4])
    
    
    
    # pngs = glob.glob("*.png")
    # for png in pngs:
    #     buf = getbuffer(Image.open(png))
    #     writebin(buf, png[:-4])
        # readbin(png[:-4])
    
    # bmps = glob.glob("*.bmp")
    # for bmp in bmps:
    #     buf = getbuffer(Image.open(bmp))
    #     writebin(buf, bmp[:-4])
    #     readbin(bmp[:-4])

    # for bmp in bmps:
    #     if bmp == "esha-einked2.bmp":
    #         buf = getbuffer(Image.open(bmp))
    #         writezlib(buf, bmp[:-4])
    #     # readbin(bmp[:-4])