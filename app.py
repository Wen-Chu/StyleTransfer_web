from flask import Flask, render_template, request, flash, url_for, redirect
from PIL import Image
import os, shutil
import base64
from io import BytesIO
from datetime import datetime
import json
from img_process import uploadPicture1, uploadPicture2, combine
# import s_data

app = Flask(__name__)
app.secret_key = "dhfuihsomakne,wpa"
# app.config['SERVER_NAME'] = s_data.server_name

img_temp = {}

def setup_user_dic(user_uni):
    user_dir = os.path.join("static", "Images", user_uni)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    else:
        shutil.rmtree(user_dir)
        os.makedirs(user_dir)

def handle_image_upload(user_uni, image_data, image_type):
    img_temp[user_uni + "upload_pass"] = False
    result = image_data.split(',')[1]
    im = Image.open(BytesIO(base64.b64decode(result)))
    im.convert('RGB').save(f"static/Images/{user_uni}/{user_uni}-{image_type}_image.png")
    img_temp[user_uni + "upload_pass"] = True
    return result

@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.route("/")
def index():
    global user_uni
    user_uni = request.environ['REMOTE_ADDR']
    setup_user_dic(user_uni)
    return render_template("index.html")

@app.route("/again")
def again():
	return redirect(url_for('index'))

@app.route('/img1file', methods=['POST'])
def img1file():
    output = request.get_json()
    result = json.loads(output)
    return handle_image_upload(user_uni, result["img_base64"], "content")


@app.route('/img2file', methods=['POST'])
def img2file():
    output = request.get_json()
    result = json.loads(output)
    return handle_image_upload(user_uni, result["img_base64"], "style")

def process_image(request_form, image_type, user_uni):
    if request_form[f'rad{image_type}'] == f'rad{image_type}_url':
        img_input = str(request_form[f'img{image_type}_url']).strip()
        file_flag = False
    else:
        img_input = os.path.abspath(os.path.join('static', 'Images', user_uni, f"{user_uni}-{image_type}_image.png"))
        file_flag = True
        while img_temp[user_uni + "upload_pass"] != True:
            continue  # Consider an efficient wait mechanism
    return img_input, file_flag

@app.route("/img1", methods=['POST', 'GET'])
def readimg1():
    user_uni = request.environ['REMOTE_ADDR']
    img1_input, file1 = process_image(request.form, "1", user_uni)
    if img1_input == '':
        flash("請輸入內容圖片")
    else:
        try:
            img1 = uploadPicture1(img1_input, file1, user_uni, img_temp)
            img1.save("static/Images/" + user_uni + "/" + user_uni + "-content_image.png")
        except Exception as e:
            app.logger.error(f"Content image upload error: {e}")
            flash("內容圖片上傳錯誤！")
    return render_template("index.html", file1="../static/Images/" + user_uni + "/" + user_uni + "-content_image.png")

@app.route("/img2", methods=['POST', 'GET'])
def readimg2():
    user_uni = request.environ['REMOTE_ADDR']
    img2_input, file2 = process_image(request.form, "2", user_uni)
    if img2_input == '':
        flash("請輸入風格圖片")
    else:
        try:
            img2 = uploadPicture2(img2_input, file2, user_uni, img_temp)
            img2.save("static/Images/" + user_uni + "/" + user_uni + "-style_image.png")
        except Exception as e:
            app.logger.error(f"Style image upload error: {e}")
            flash("風格圖片上傳錯誤!")
    return render_template("index.html", file1="../static/Images/" + user_uni + "/" + user_uni + "-content_image.png", file2="../static/Images/" + user_uni + "/" + user_uni + "-style_image.png")

@app.route("/trans", methods=['POST', 'GET'])
def showimg3():
    user_uni = request.environ['REMOTE_ADDR']
    dt_img3 = datetime.now().strftime("%Y%m%d-%H%M%S")
    try:
        img3 = combine(user_uni, img_temp)
        img3.save("static/Images/" + user_uni + "/" + dt_img3 + "-stylized_image.png")
    except Exception as e:
        app.logger.error(f"Image combining error: {e}")
        flash("圖像處理錯誤")
    return render_template("index.html", file1="../static/Images/" + user_uni + "/" + user_uni + "-content_image.png", file2="../static/Images/" + user_uni + "/" + user_uni + "-style_image.png", file3="../static/Images/" + user_uni + "/" + dt_img3 + "-stylized_image.png")

if __name__ == "__main__":
    app.run()
#     app.run(ssl_context=(s_data.cert, s_data.privkey), host='0.0.0.0', port=66)