from flask import Blueprint, render_template, redirect, url_for, session, flash

from app.models.Request import Request
from app.models.ScoreChangeLog import ScoreChangeLog
from app.models.base import db
from flask import Flask, request, jsonify
from app.models.AssignQ import AssignQ
from app.models.LLM_Answer import LLM_Answer
from app.models.LLM_Answer_Imgae import LLM_Answer_Image
from app.models.course import Course
from functools import wraps

from collections import defaultdict

AssignQBP = Blueprint('AssignQ', __name__)

def login_required_teacher(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # print("teacher!!!")
        # print(session)
        if 'user_id' not in session:
            return redirect(url_for('user.login'))
        if session.get('user_type') == 'student':
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

@AssignQBP.route('/AssignQ', methods=['GET', 'POST'])
@login_required_teacher
def SearchAssignment():
    searched = False
    results = defaultdict(list)

    if request.method == 'POST':
        searched = True
        course_name_or_number_query = request.form.get('search_course_name_or_number', '').strip()
        course_category_query = request.form.get('search_course_category', '').strip()
        score_query = request.form.get('search_score', '').strip()

        query = db.session.query(AssignQ, LLM_Answer, LLM_Answer_Image, Course).join(
            LLM_Answer, AssignQ.llm_answer_id == LLM_Answer.LLM_id
        ).outerjoin(
            LLM_Answer_Image, LLM_Answer.LLM_id == LLM_Answer_Image.llm_answer_id
        ).join(
            Course, AssignQ.course_id == Course.id
        )

        if course_name_or_number_query:
            query = query.filter(
                (Course.course_name.ilike(f"%{course_name_or_number_query}%")) |
                (Course.course_number.ilike(f"%{course_name_or_number_query}%"))
            )

        if course_category_query:
            query = query.filter(Course.course_category.ilike(f"%{course_category_query}%"))

        if score_query:
            try:
                score = float(score_query)
                query = query.filter(LLM_Answer.score == score)
            except ValueError:
                pass

        # 将结果按 Qtext 分组
        for assignq, llm_answer, llm_answer_image, course in query.all():
            results[assignq.Qtext].append((llm_answer, llm_answer_image, course))

    return render_template('search_assignment.html', results=results, searched=searched, title='Search Assignment', header='Search Assignment')


@AssignQBP.route('/change_score_direct', methods=['POST'])
@login_required_teacher
def change_score_direct():
    llm_answer_id = request.form.get('llm_answer_id')
    new_score = request.form.get('new_score')
    explanation = request.form.get('explanation', '').strip()
    user_id = session.get('user_id')  # 获取当前登录用户的 ID

    new_request = Request(
        qtext=None,  # 如果没有问题文本，可以为空
        course_id=None,  # 使用刚刚插入课程的 ID
        llm_used=None,  # 没有使用 LLM
        score=None,  # 没有分数
        comment=None,  # 没有评论
        llm_answer_id=llm_answer_id,  # 没有回答 ID
        new_score=new_score,
        explanation=explanation,
        user_id=user_id,  # 可以设置为当前用户的 ID（如适用）
        course_number=None,
        course_name=None,
        course_category=None,
        request_type='change_score'
    )    

    try:
        db.session.add(new_request)
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # 出错时回滚
        print(f"Error: {e}")
        return jsonify({"error": str(e)})
    
    try:
        new_score = float(new_score)
    except ValueError:
        return "Invalid score value", 400

    # 查询当前答案的 `AssignQ` 记录以获取 `qtext`
    assignq = AssignQ.query.filter_by(llm_answer_id=llm_answer_id).first()
    if not assignq:
        return "Associated question text not found.", 404
    qtext = assignq.Qtext  # 获取相关的 `qtext`

    # 检查用户是否已经修改过该答案的分数
    existing_log = ScoreChangeLog.query.filter_by(llm_answer_id=llm_answer_id, user_id=user_id).first()

    if existing_log:
        # 用户已修改过，返回错误消息
        flash("You have already modified the score for this answer.", "error")
        return redirect(url_for('AssignQ.details_by_qtext', qtext=qtext))

    # 获取或初始化该答案的初始日志记录
    llm_answer = LLM_Answer.query.get(llm_answer_id)
    if llm_answer:
        # 检查是否已有初始日志记录
        initial_logs = ScoreChangeLog.query.filter_by(llm_answer_id=llm_answer_id).count()

        if initial_logs == 0:
            # 如果没有初始日志记录，将初始分数和解释保存到日志中
            initial_comment = llm_answer.comment
            log_entry = ScoreChangeLog(
                llm_answer_id=llm_answer_id,
                original_score=None,  # 用 None 表示初始记录
                new_score=llm_answer.score,  # 记录最初的分数
                explanation=initial_comment,
                user_id=user_id  # 关联当前用户
            )
            db.session.add(log_entry)
            db.session.commit()

        # 添加新的更改日志记录
        log_entry = ScoreChangeLog(
            llm_answer_id=llm_answer_id,
            original_score=llm_answer.score,
            new_score=new_score,
            explanation=explanation,
            user_id=user_id  # 添加用户 ID
        )
        db.session.add(log_entry)
        db.session.commit()

        # 获取所有与 llm_answer_id 匹配的日志记录
        logs = ScoreChangeLog.query.filter_by(llm_answer_id=llm_answer_id).all()
        scores = [float(log.new_score) if log.original_score is not None else float(llm_answer.score) for log in logs]

        average_score = sum(scores) / len(scores)
        average_score = round(average_score, 0)

        # 更新 LLM_Answer 中的平均分和解释
        llm_answer.score = average_score
        llm_answer.comment = explanation
        db.session.commit()

    return redirect(url_for('AssignQ.details_by_qtext', qtext=qtext))
    # return redirect(url_for('AssignQ.details_by_qtext'))

@AssignQBP.route('/details/<int:llm_answer_id>', methods=['GET'])
@login_required_teacher
def details(llm_answer_id):
    # 获取特定的 LLM_Answer 及相关信息
    llm_answer = LLM_Answer.query.get_or_404(llm_answer_id)
    llm_answer_image = LLM_Answer_Image.query.filter_by(llm_answer_id=llm_answer_id).first()
    assignq = AssignQ.query.filter_by(llm_answer_id=llm_answer_id).first()
    course = Course.query.get(assignq.course_id)

    # 获取更改日志
    score_change_logs = ScoreChangeLog.query.filter_by(llm_answer_id=llm_answer_id).all()

    # 渲染新的详细页面
    return render_template('details.html', llm_answer=llm_answer, llm_answer_image=llm_answer_image, assignq=assignq, course=course, score_change_logs=score_change_logs)

@AssignQBP.route('/details_by_qtext/<qtext>', methods=['GET'])
@login_required_teacher
def details_by_qtext(qtext):
    # 获取所有具有相同 Qtext 的回答
    query = db.session.query(AssignQ, LLM_Answer, LLM_Answer_Image, Course).join(
        LLM_Answer, AssignQ.llm_answer_id == LLM_Answer.LLM_id
    ).outerjoin(
        LLM_Answer_Image, LLM_Answer.LLM_id == LLM_Answer_Image.llm_answer_id
    ).join(
        Course, AssignQ.course_id == Course.id
    ).filter(AssignQ.Qtext == qtext)

    results = query.all()

    return render_template('details_by_qtext.html', qtext=qtext, results=results)
