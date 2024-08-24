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

def get_font_text_size(text):
    canvas = Image.new('RGB', (32,32))
    draw = ImageDraw.Draw(canvas)

    draw.text((0, 0), text, font=font, fill=text_color, stroke_width=stroke_width, stroke_fill=stroke_color)
    bbox = canvas.getbbox()
    # 宽高
    size = (bbox[2] - bbox[0], bbox[3] - bbox[1])
    return size

# Load the image
image_path = r"C:\Users\jetth\Pictures\wow\spell_holy_blessingofprotection.jpg"
image = Image.open(image_path)
image.resize((50, 50))

# Create a drawing object
draw = ImageDraw.Draw(image)

# Calculate text size using the correct method from ImageFont
font_text_size = get_font_text_size("Z")

# Calculate the position to add the font picture
font_pic_position = (image.width - font_text_size[0] - 3, 3)

draw.text(font_pic_position, "Z", font=font, fill=text_color, stroke_width=stroke_width, stroke_fill=stroke_color)

# Save the modified image
output_path = "output.jpg"
image.save(output_path)