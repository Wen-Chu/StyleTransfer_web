from flask import Flask, render_template, request, flash
from PIL import Image
import functools
import os
import tensorflow as tf
import tensorflow_hub as hub

app = Flask(__name__)
app.secret_key = "dhfuihsomakne,wpa"

content_img_size = (384, 384)
style_img_size = (256, 256)

@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/again")
def again():
	return render_template("index.html")

@app.route("/img1", methods=['POST', 'GET'])
def readimg1():
    if request.form['rad1'] == 'rad1_url':
        img1_input = str(request.form['img1_url']).strip()
    else:
        img1_input = request.form['img1_file']
    if img1_input == '':
        flash("請輸入內容圖片")
        return render_template("index.html")
    else:
        try:
            img1 = uploadPicture1(img1_input)
            img1.save("static/Images/content_image.png")
            return render_template("index.html", file1="../static/Images/content_image.png")
        except:
            flash("內容圖片上傳錯誤!")
            return render_template("index.html")

@app.route("/img2", methods=['POST', 'GET'])
def readimg2():
    if request.form['rad2'] == 'rad2_url':
        img2_input = str(request.form['img2_url']).strip()
    else:
        img2_input = request.form['img2_file']
    if img2_input == '':
        flash("請輸入風格圖片")
        return render_template("index.html", file1="../static/Images/content_image.png")
    else:
        try:
            img2 = uploadPicture2(img2_input)
            img2.save("static/Images/style_image.png")
            return render_template("index.html", file1="../static/Images/content_image.png",
                                   file2="../static/Images/style_image.png")
        except:
            flash("風格圖片上傳錯誤!")
            return render_template("index.html", file1="../static/Images/content_image.png")

@app.route("/trans", methods=['POST', 'GET'])
def showimg3():
    img3 = combine()
    img3.save("static/Images/stylized_image.png")
    return render_template("index.html", file1="../static/Images/content_image.png",
                           file2="../static/Images/style_image.png", file3="../static/Images/stylized_image.png")

def crop_center(image):
    shape = image.shape
    new_shape = min(shape[1], shape[2])
    offset_y = max(shape[1] - shape[2], 0) // 2
    offset_x = max(shape[2] - shape[1], 0) // 2
    image = tf.image.crop_to_bounding_box(image, offset_y, offset_x, new_shape, new_shape)
    return image

@functools.lru_cache(maxsize=None)
def load_image(image_url, image_size=(256, 256), preserve_aspect_ratio=True):
    file_name = os.path.basename(image_url)[-128:]
    try:
        image_path = tf.keras.utils.get_file(file_name, image_url)
    except:
        if '.jpg' in file_name:
            temp = file_name.split('.jpg')[0]
            file_name = temp + '.jpg'
        elif '.jpeg' in file_name:
            temp = file_name.split('.jpeg')[0]
            file_name = temp + '.jpg'
        elif '.png' in file_name:
            temp = file_name.split('.png')[0]
            file_name = temp + '.png'
        else:
            file_name = file_name.replace('/', '').replace('\\', '').replace(':', '').replace('*', '').replace('?', '') \
                .replace('"', '').replace('<', '').replace('>', '').replace('|', '')
            file_name = file_name+'.png'
        image_path = tf.keras.utils.get_file(file_name, image_url)
    img = tf.io.decode_image(
        tf.io.read_file(image_path),
        channels=3, dtype=tf.float32)[tf.newaxis, ...]
    img = crop_center(img)
    img = tf.image.resize(img, image_size, preserve_aspect_ratio=True)
    return img

def display_img(images, num):
    rgbList = images[0].numpy() * 255
    rgbList = rgbList.astype(int)
    maxval = 255
    height = [384, 256, 384]
    pixels = []
    for y in range(height[num]):
        for x in range(height[num]):
            pix = rgbList[y][x][0], rgbList[y][x][1], rgbList[y][x][2], maxval
            pixels.append(pix)
    img = Image.new('RGBA', (height[num], height[num]))
    img.putdata(pixels)
    if num == 0 or num == 2:
        img = img.resize((256, 256), Image.ANTIALIAS)
    return img

def combine():
    hub_handle = 'https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2'
    hub_module = hub.load(hub_handle)
    outputs = hub_module(tf.constant(content_image), tf.constant(style_image))
    stylized_image = outputs[0]
    return display_img(stylized_image, 2)

def uploadPicture1(img1):
    global content_image
    content_image = load_image(img1, content_img_size)
    return display_img(content_image, 0)

def uploadPicture2(img2):
    global style_image
    style_image = load_image(img2, style_img_size)
    style_image = tf.nn.avg_pool(style_image, ksize=[3, 3], strides=[1, 1], padding='SAME')
    return display_img(style_image, 1)