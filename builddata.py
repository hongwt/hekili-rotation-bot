import os
from PIL import Image, ImageDraw, ImageFont

# Define the font and size
font_path = "C:/Windows/Fonts/ARIALN.TTF"
font_size = 12
font = ImageFont.truetype(font_path, font_size)

# Define the text color and stroke color
text_color = (255, 255, 255)  # White
stroke_color = (128, 128, 128)  # Gray

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


charset_train = "0123456789ABCDEFGHJKLMNPQRSTUVWXYZ"

# Iterate over each file in the directory
for filename in os.listdir("D:/tmp/wow"):
    if filename.endswith(".jpg"):
        # Load the image
        image_path = os.path.join("D:/tmp/wow", filename)
        image = Image.open(image_path)
        image = image.resize((50, 50))

        for i in range(5):
            for j in range(5):
                # Iterate over each character in charset_train
                for char in charset_train:
                    # Rest of the code...
                    newImage = image.crop((image.width - 24 - i, j, image.width - i, j + 24))
                    # Create a drawing object
                    draw = ImageDraw.Draw(newImage)
                    # Calculate text size using the correct method from ImageFont
                    font_text_size = get_font_text_size(char)

                    # Calculate the position to add the font picture
                    font_pic_position = (newImage.width - font_text_size[0] - 3, 3)

                    draw.text(font_pic_position, char, font=font, fill=text_color, stroke_width=stroke_width, stroke_fill=stroke_color)

                    # Save the modified image with the character name in the file name
                    output_path = f"images/{filename}_Gray_{(i+1)*(j+1)}_{char}.jpg"
                    newImage.save(output_path)

                    # Write the image path and corresponding character to gt.txt
                    with open("images/gt.txt", "a") as file:
                        file.write(f"{output_path}\t{char}\n")