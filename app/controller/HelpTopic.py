from flask import request, render_template, redirect, url_for, Blueprint, session
from app.models.base import db
from app.models.HelpTopic import HelpTopic
from app.models.course import Course
from app.models.LLM_Answer import LLM_Answer
from functools import wraps

HelpTopicBP = Blueprint('HelpTopic', __name__)

# Utility function to restrict access to logged-in users
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

@HelpTopicBP.route('/HelpTopic', methods=['GET', 'POST'])
@login_required
def SearchHelpTopic():
    searched = False
    topics = []

    if request.method == 'POST':
        searched = True
        search_type = request.form.get('search_type')
        search_query = request.form.get('search_query', '').strip()
        query = db.session.query(HelpTopic).join(Course, HelpTopic.course_id == Course.id)

        if search_type == 'course_name':
            query = query.filter(Course.course_name.ilike(f"%{search_query}%"))
        elif search_type == 'course_category':
            query = query.filter(Course.course_category.ilike(f"%{search_query}%"))

        topics = query.all()

    return render_template('search_help_topic.html', topics=topics, searched=searched, title='Help Topics', header='Help Topics')

@HelpTopicBP.route('/HelpTopic/subtopic/<int:subtopic_id>/questions')
@login_required
def ListQuestions(subtopic_id):
    subtopic = HelpTopic.query.get_or_404(subtopic_id)
    topic_helps_questions = subtopic.topic_helps_questions.split(';') if subtopic.topic_helps_questions else []

    return render_template('list_questions.html', subtopic=subtopic, topic_helps_questions=topic_helps_questions, title='Questions', header='Questions')

@HelpTopicBP.route('/HelpTopic/question/<int:question_id>/details')
@login_required
def QuestionDetails(question_id):
    question = LLM_Answer.query.get_or_404(question_id)
    subtopic = question.help_topics[0]
    images = [image.get_image_data_base64() for image in question.images]

    return render_template('question_details.html', question=question, subtopic=subtopic, images=images, title='Question Details', header='Question Details')

@HelpTopicBP.route('/HelpTopic/question/<int:subtopic_id>/<question>', methods=['GET'])
@login_required
def QuestionDetailsByQuestion(subtopic_id, question):
    subtopic = HelpTopic.query.get_or_404(subtopic_id)
    llm_answer = LLM_Answer.query.get_or_404(subtopic.llm_answer_id)
    images = [image.get_image_data_base64() for image in llm_answer.images]

    return render_template('question_details.html', question=question, subtopic=subtopic, llm_answer=llm_answer, images=images, title='Question Details', header='Question Details')
