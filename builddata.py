from PIL import Image, ImageDraw, ImageFont


# Define the font and size
font_path = "C:/Windows/Fonts/ARIALN.TTF"
font_size = 12
font = ImageFont.truetype(font_path, font_size)

# Define the text color and stroke color
text_color = (255, 255, 255)  # White
stroke_color = (0, 0, 0)  # Black

# Define the stroke width
stroke_width = 1

def get_font_pic(text):
    canvas = Image.new('RGB', (32,32))
    draw = ImageDraw.Draw(canvas)

    draw.text((0, 0), text, font=font, fill=text_color, stroke_width=stroke_width, stroke_fill=stroke_color)
    bbox = canvas.getbbox()
    # 宽高
    size = (bbox[2] - bbox[0], bbox[3] - bbox[1])
    # 重新生成图片
    font_pic = canvas.crop(bbox)
    return font_pic

# Load the image
image_path = r"C:\Users\jetth\Pictures\wow\spell_holy_blessingofprotection.jpg"
image = Image.open(image_path)
image.resize((50, 50))

# Create a drawing object
draw = ImageDraw.Draw(image)

# Calculate text size using the correct method from ImageFont
font_pic = get_font_pic("Z")

# Calculate the position to add the font picture
font_pic_position = (image.width - font_pic.width - 3, 3)

# Add the font picture to the image
image.paste(font_pic, font_pic_position)

# Save the modified image
output_path = "output.jpg"
image.save(output_path)