
import random
import string
import io
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def add_gaussian_noise(image, mean=0, var=500):
    img_array = np.array(image, dtype=np.float32)
    noise = np.random.normal(mean, var ** 0.5, img_array.shape)
    noisy_img = np.clip(img_array + noise, 0, 255).astype(np.uint8)

    return Image.fromarray(noisy_img)

def add_random_lines(draw, width, height, num_lines=3):
    for _ in range(num_lines):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill='black', width=2)

def add_random_dots(draw, width, height, num_dots=100):
    for _ in range(num_dots):
        x, y = random.randint(0, width), random.randint(0, height)
        draw.point((x, y), fill='black')

def add_main_obstruction_line(draw, width, height):
    x1, y1 = random.randint(0, width // 3), random.randint(height // 3, 2 * height // 3)
    x2, y2 = random.randint(2 * width // 3, width), random.randint(height // 3, 2 * height // 3)
    draw.line([(x1, y1), (x2, y2)], fill='black', width=4)

def generate_captcha_text(length=4):
    return ''.join(random.choices(string.digits, k=length))

def generate_captcha_image(text):
    width, height = 150, 50
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except IOError:
        font = ImageFont.load_default()

    draw.text((20, 10), text, font=font, fill='black')

    add_random_lines(draw, width, height, num_lines=3)
    add_random_dots(draw, width, height, num_dots=150)

    # add_main_obstruction_line(draw, width, height)

    noisy_image = add_gaussian_noise(image)

    img_io = io.BytesIO()
    try:
        noisy_image.save(img_io, format='PNG')
        img_io.seek(0)
        return img_io
    except Exception as e:
        return None


