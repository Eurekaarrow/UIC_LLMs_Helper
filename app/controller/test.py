from flask import Blueprint, Flask, request, render_template, jsonify, Response, redirect, url_for
from werkzeug.utils import secure_filename
import io
from PIL import Image
from app.models.LLM_Answer_Imgae import LLM_Answer_Image
from app.models.base import db

testBP = Blueprint('test', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@testBP.route('/test', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        file = request.files['image']
        if file and allowed_file(file.filename):
            image = Image.open(file.stream)
            image = image.resize((1024, 768))  # 调整图片大小
            imgByteArr = io.BytesIO()
            image.save(imgByteArr, format='JPEG')
            image_data = imgByteArr.getvalue()

            # 创建一个新的LLM_Answer_Image对象
            new_image = LLM_Answer_Image(image_data=image_data)
            db.session.add(new_image)
            db.session.commit()

            return jsonify({'message': 'Image successfully uploaded!'})
        return jsonify({'message': 'Invalid file or file upload failed.'})
    return render_template('upload_image.html')

@testBP.route('/image/<int:image_id>')
def serve_image(image_id):
    image_record = LLM_Answer_Image.query.filter_by(image_id=image_id).first()
    if image_record:
        return Response(image_record.image_data, mimetype='image/jpeg')
    else:
        return 'Image Not Found', 404