import tensorflow as tf
import tensorflow_hub as hub
import PIL
from PIL import Image
from datetime import datetime
import os
def crop_center(image):
    shape = image.shape
    new_shape = min(shape[1], shape[2])
    offset_y = max(shape[1] - shape[2], 0) // 2
    offset_x = max(shape[2] - shape[1], 0) // 2
    image = tf.image.crop_to_bounding_box(image, offset_y, offset_x, new_shape, new_shape)
    return image

def download_image(image_url):
    file_name = os.path.basename(image_url).split('?')[0]
    file_name = ''.join([c for c in file_name if c.isalnum() or c in ('.', '_')]).rstrip()
    file_ext = file_name.rsplit('.', 1)[-1]
    if file_ext.lower() not in ['jpg', 'jpeg', 'png']:
        file_name += '.png'
    return tf.keras.utils.get_file(file_name, image_url)

def load_image(num, isfile, image_url, user_uni):
    try:
        if not isfile:
            image_path = download_image(image_url)
        else:
            dt_data = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"{user_uni}-{dt_data}-{'content' if num == 1 else 'style'}_image.png"
            image_path = tf.keras.utils.get_file(filename, 'file:/' + image_url)

        img = tf.io.decode_image(tf.io.read_file(image_path), channels=3, dtype=tf.float32)[tf.newaxis, ...]
        img = crop_center(img)
        return img
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

def display_img(image_tensor, size, num):
    img = tf.image.resize(image_tensor, (size, size))
    img = tf.clip_by_value(img, 0.0, 1.0)
    img = tf.cast(img[0] * 255, tf.uint8)
    return PIL.Image.fromarray(img.numpy())


def combine(user_uni, img_temp, style_weight=1.0):
    try:
        hub_handle = 'https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2'
        hub_module = hub.load(hub_handle)
        content_image = img_temp.get(user_uni + "content")
        style_image = img_temp.get(user_uni + "style")
        outputs = hub_module(tf.constant(content_image), tf.constant(style_image), style_image_weight=style_weight)
        stylized_image = outputs[0]
        return display_img(stylized_image, content_image_size, 2)
    except Exception as e:
        print(f"Error in image combination: {e}")
        return None

def uploadPicture1(img1, file1, user_uni, img_temp):
    try:
        content_image = load_image(1, file1, img1, user_uni)
        if content_image is None:
            return None
        global content_image_size
        content_image_size = min(content_image.shape[1], content_image.shape[2])
        if content_image_size > 2000:
            content_image_size = 1920
        content_image = tf.image.resize(content_image, (content_image_size, content_image_size), preserve_aspect_ratio=True)
        img_temp[user_uni+"content"] = content_image
        return display_img(content_image, content_image_size, 0)
    except Exception as e:
        print(f"Error uploading picture 1: {e}")
        return None

def uploadPicture2(img2, file2, user_uni, img_temp):
    try:
        style_image = load_image(2, file2, img2, user_uni)
        if style_image is None:
            return None
        style_image_size = 256
        style_image = tf.image.resize(style_image, (style_image_size, style_image_size), preserve_aspect_ratio=True)
        style_image = tf.nn.avg_pool(style_image, ksize=[3, 3], strides=[1, 1], padding='SAME')
        img_temp[user_uni+"style"] = style_image
        return display_img(style_image, style_image_size, 1)
    except Exception as e:
        print(f"Error uploading picture 2: {e}")
        return None