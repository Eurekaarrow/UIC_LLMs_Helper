import base64
from app.models.AssignQ import AssignQ
from app.models.LLM_Answer import LLM_Answer
from flask import Blueprint, Flask, request, render_template, jsonify, Response, redirect, url_for, session
import io
from PIL import Image
from app.models.LLM_Answer_Imgae import LLM_Answer_Image
from app.models.Request import Request
from app.models.Request_image import Request_image
from app.models.base import db
from app.models.course import Course
from app.models.PersonalExperiment import PersonalExperiment

RequestBP = Blueprint('Request', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@RequestBP.route('/Request', methods=['GET', 'POST'])
def create_assignq():
    courses = Course.query.all()  # 获取所有课程
    if request.method == 'POST':
        qtext = request.form['qtext']
        course_id = request.form.get('course_id')  # 从表单获取课程 ID
        llm_used = request.form['llm_used']
        score = int(request.form['score'])
        comment = request.form['comment']

        new_request = Request(
            qtext=qtext,
            course_id=course_id,  # 保存课程 ID
            llm_used=llm_used,
            score=score,
            comment=comment,
            llm_answer_id=None,
            new_score=None,
            explanation=None,
            user_id=None,
            course_number=None,
            course_name=None,
            course_category=None,
            request_type='create_assignq'
        )
        db.session.add(new_request)
        db.session.flush()

        request_id = new_request.request_id

        files = request.files.getlist('images')  # 获取所有上传的图片文件
        for file in files:
            if file and allowed_file(file.filename):
                image = Image.open(file.stream)
                if image.mode == 'RGBA':
                    image = image.convert('RGB')
                image = image.resize((1024, 768))
                imgByteArr = io.BytesIO()
                image.save(imgByteArr, format='JPEG')
                image_data = imgByteArr.getvalue()

                new_image = Request_image(image_data=image_data, llm_answer_id=request_id)
                db.session.add(new_image)

        db.session.commit()

        return redirect(url_for('Request.create_assignq'))

    return render_template('create_assignq.html', courses=courses)


@RequestBP.route('/image/<int:image_id>')
def serve_image(image_id):
    image_record = LLM_Answer_Image.query.filter_by(id=image_id).first()
    if image_record:
        return Response(image_record.image_data, mimetype='image/jpeg')
    else:
        return 'Image Not Found', 404

@RequestBP.route('/add_course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        course_number = request.form['course_number']
        course_name = request.form['course_name']
        course_category = request.form['course_category']
        
        new_request = Request(
            qtext=None,  # 如果没有问题文本，可以为空
            course_id=None,  # 使用刚刚插入课程的 ID
            llm_used=None,  # 没有使用 LLM
            score=None,  # 没有分数
            comment=None,  # 没有评论
            llm_answer_id=None,  # 没有回答 ID
            new_score=None,
            explanation=None,
            user_id=None,  # 可以设置为当前用户的 ID（如适用）
            course_number=course_number,
            course_name=course_name,
            course_category=course_category,
            request_type='add_course'
        )

        # 添加并提交请求到数据库
        db.session.add(new_request)
        db.session.commit()

        return redirect(url_for('Request.add_course'))

    return render_template('addcourse.html')

# @RequestBP.route('/change_score', methods=['GET', 'POST'])
# def change_score():
#     if request.method == 'POST':
#         llm_answer_id = request.form['llm_answer_id']
#         new_score = int(request.form['new_score'])

#         llm_answer = LLM_Answer.query.get(llm_answer_id)
#         if llm_answer:
#             llm_answer.score = new_score
#             db.session.commit()

#         return redirect(url_for('Request.change_score'))

#     return render_template('change_score.html')

@RequestBP.route('/admin/change_score', methods=['GET', 'POST'])
def admin_change_score():
    if request.method == 'GET':
        # Fetch all change_score type requests and join with LLM_Answer table
        requests = db.session.query(Request, LLM_Answer.score.label('current_score')).join(LLM_Answer, Request.llm_answer_id == LLM_Answer.LLM_id).filter(Request.request_type == 'change_score').all()
        return render_template('admin_change_score.html', requests=requests)
    elif request.method == 'POST':
        request_id = request.form.get('request_id')
        # Fetch the specific request based on request_id
        req = Request.query.get(request_id)
        if req:
            llm_answer = LLM_Answer.query.get(req.llm_answer_id)
            if llm_answer:
                # Update the score in LLM_Answer as per the new score in the request
                llm_answer.score = req.new_score
                # Commit the score update
                db.session.commit()
                # Delete the processed request from the database
                db.session.delete(req)
                # Commit the deletion
                db.session.commit()
        return redirect(url_for('Request.admin_change_score'))
    

@RequestBP.route('/admin/add_course', methods=['GET', 'POST'])
def admin_add_course():
    if request.method == 'GET':
        # Fetch all add_course type requests
        requests = Request.query.filter_by(request_type='add_course').all()
        return render_template('admin_add_course.html', requests=requests)
    elif request.method == 'POST':
        request_id = request.form.get('request_id')
        # Fetch the specific request based on request_id
        req = Request.query.get(request_id)
        if req:
            # Create a new course and add it to the database
            new_course = Course(
                course_number=req.course_number,
                course_name=req.course_name,
                course_category=req.course_category
            )
            db.session.add(new_course)
            # Delete the processed request from the database
            db.session.delete(req)
            # Commit changes
            db.session.commit()
        return redirect(url_for('Request.admin_add_course'))


@RequestBP.route('/admin/create_assignq', methods=['GET', 'POST'])
def admin_create_assignq():
    if request.method == 'GET':
        requests_with_images = []
        requests = Request.query.filter_by(request_type='create_assignq').all()
        for req in requests:
            images = Request_image.query.filter_by(llm_answer_id=req.request_id).all()
            encoded_images = [base64.b64encode(img.image_data).decode('utf-8') for img in images]
            requests_with_images.append((req, encoded_images))

        return render_template('admin_create_assignq.html', requests_with_images=requests_with_images)
    elif request.method == 'POST':
        request_id = request.form.get('request_id')
        req = Request.query.get(request_id)
        if req:
            llm_answer = LLM_Answer(LLM_used=req.llm_used, score=req.score, comment=req.comment)
            db.session.add(llm_answer)
            db.session.flush()

            assignq = AssignQ(Qtext=req.qtext, course_id=req.course_id, llm_answer=llm_answer)  # 保存课程 ID
            db.session.add(assignq)

            images = Request_image.query.filter_by(llm_answer_id=req.request_id).all()
            for image in images:
                new_image = LLM_Answer_Image(image_data=image.image_data, llm_answer_id=llm_answer.LLM_id)
                db.session.add(new_image)
                db.session.delete(image)

            db.session.delete(req)
            db.session.commit()

        return redirect(url_for('Request.admin_create_assignq'))


@RequestBP.route('/view_personal_experiments')
def view_personal_experiments():
    experiments = PersonalExperiment.query.filter_by(user_id=session.get('user_id')).all()
    return render_template('view_experiments.html', experiments=experiments)


@RequestBP.route('/personal_experiment', methods=['GET', 'POST'], endpoint='personal_experiment')
def personal_experiment():
    courses = Course.query.all()  # 获取所有课程
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            return "User not logged in", 403

        question_text = request.form['qtext']
        llm_used = request.form['llm_used']
        score = int(request.form['score'])
        course_id = request.form.get('course_id')  # 获取所选课程的 ID

        file = request.files.get('image')
        if file and allowed_file(file.filename):
            image = Image.open(file.stream)
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            image = image.resize((1024, 768))
            imgByteArr = io.BytesIO()
            image.save(imgByteArr, format='JPEG')
            image_data = imgByteArr.getvalue()
        else:
            image_data = None

        new_experiment = PersonalExperiment(
            user_id=user_id,
            question_text=question_text,
            llm_used=llm_used,
            llm_answer_image=image_data,
            score=score,
            course_id=course_id,  # 保存课程 ID
            is_submitted=0
        )
        db.session.add(new_experiment)
        db.session.commit()

        return redirect(url_for('Request.personal_experiment'))

    return render_template('experiment.html', courses=courses)

@RequestBP.route('/submit_experiment/<int:experiment_id>', methods=['POST'])
def submit_experiment(experiment_id):
    experiment = PersonalExperiment.query.get(experiment_id)
    if experiment:
        experiment.is_submitted = 1
        db.session.commit()

        new_request = Request(
            qtext=experiment.question_text,
            course_id=experiment.course_id,  # 保存课程 ID
            llm_used=experiment.llm_used,
            score=experiment.score,
            comment=None,
            llm_answer_id=None,
            new_score=None,
            explanation=None,
            user_id=experiment.user_id,
            course_number=None,
            course_name=None,
            course_category=None,
            request_type='personal_experiment'
        )
        db.session.add(new_request)
        db.session.flush()

        request_id = new_request.request_id

        if experiment.llm_answer_image:
            new_image = Request_image(image_data=experiment.llm_answer_image, llm_answer_id=request_id)
            db.session.add(new_image)

        db.session.commit()

    return redirect(url_for('Request.view_personal_experiments'))


@RequestBP.route('/admin/pending_requests', methods=['GET', 'POST'])
def admin_pending_requests():
    if request.method == 'POST':
        request_id = request.form.get('request_id')
        action = request.form.get('action')

        req = Request.query.get(request_id)
        if req:
            if action == 'approve':
                # 创建一个新的 LLM_Answer 对象
                llm_answer = LLM_Answer(
                    LLM_used=req.llm_used,
                    score=req.score,
                    comment=req.comment
                )
                db.session.add(llm_answer)
                db.session.flush()  # 确保获取到自增的 llm_answer_id

                # 获取刚刚插入的 llm_answer_id
                llm_answer_id = llm_answer.LLM_id

                # 创建一个新的 AssignQ 对象，将问题文本插入到数据库中
                assignq = AssignQ(
                    Qtext=req.qtext,
                    course_id=req.course_id,
                    llm_answer=llm_answer
                )
                db.session.add(assignq)
                db.session.flush()  # 确保获取到自增的 q_Id

                # 获取刚刚插入的 q_Id
                assignq_id = assignq.q_Id

                # 处理图片
                images = Request_image.query.filter_by(llm_answer_id=req.request_id).all()
                for image in images:
                    new_image = LLM_Answer_Image(
                        image_data=image.image_data,
                        llm_answer_id=llm_answer_id
                    )
                    db.session.add(new_image)
                    db.session.delete(image)  # 删除临时数据库中的图片

                # 删除请求
                db.session.delete(req)
            elif action == 'reject':
                # 处理拒绝请求的逻辑
                req.request_type = 'rejected'

            db.session.commit()

        return redirect(url_for('Request.admin_pending_requests'))

    # 获取所有待审核的请求
    pending_requests = Request.query.filter_by(request_type='personal_experiment').all()
    return render_template('admin_pending_requests.html', pending_requests=pending_requests)