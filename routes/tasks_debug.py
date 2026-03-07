"""
Debug route for task display issues
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models.task import Task
from datetime import datetime

tasks_debug_bp = Blueprint('tasks_debug', __name__)

@tasks_debug_bp.route('/debug/tasks/info')
@login_required
def debug_task_info():
    """Debug endpoint to check task creation and retrieval"""
    
    # Get current user info
    user_info = {
        'id': current_user.id,
        'type': current_user.__class__.__name__,
        'type_lower': current_user.__class__.__name__.lower()
    }
    
    # Get all user tasks
    all_tasks = Task.query.filter_by(
        user_id=current_user.id,
        user_type=current_user.__class__.__name__.lower()
    ).all()
    
    # Get active tasks
    active_tasks = Task.query.filter_by(
        user_id=current_user.id,
        user_type=current_user.__class__.__name__.lower(),
        is_active=True
    ).all()
    
    # Get today's tasks
    today = datetime.now().date()
    today_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.user_type == current_user.__class__.__name__.lower(),
        Task.date == today,
        Task.is_active == True
    ).all()
    
    # Get this month's tasks
    year = datetime.now().year
    month = datetime.now().month
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date()
    else:
        end_date = datetime(year, month + 1, 1).date()
        
    monthly_tasks = Task.query.filter(
        Task.date >= start_date,
        Task.date < end_date,
        Task.user_id == current_user.id,
        Task.user_type == current_user.__class__.__name__.lower(),
        Task.is_active == True
    ).all()
    
    # Convert tasks to dict for JSON response
    def task_to_debug_dict(task):
        try:
            return {
                'id': task.id,
                'title': task.title,
                'date': task.date.isoformat(),
                'time': task.time.isoformat() if task.time else None,
                'display_time': task.display_time,
                'priority': task.priority,
                'color': task.color,
                'priority_color': task.priority_color,
                'is_active': task.is_active,
                'is_completed': task.is_completed,
                'user_id': task.user_id,
                'user_type': task.user_type,
                'created_at': task.created_at.isoformat()
            }
        except Exception as e:
            return {
                'id': task.id,
                'error': str(e),
                'title': getattr(task, 'title', 'ERROR')
            }
    
    return jsonify({
        'user_info': user_info,
        'total_tasks': len(all_tasks),
        'active_tasks': len(active_tasks),
        'today_tasks': len(today_tasks),
        'monthly_tasks': len(monthly_tasks),
        'date_range': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        },
        'all_tasks_detail': [task_to_debug_dict(task) for task in all_tasks],
        'monthly_tasks_detail': [task_to_debug_dict(task) for task in monthly_tasks]
    })

@tasks_debug_bp.route('/debug/tasks/create_test')
@login_required
def create_test_task():
    """Create a test task for debugging"""
    from extensions import db
    from datetime import date
    
    try:
        # Create test task for today
        test_task = Task(
            title="Debug Test Task",
            description="This is a test task created for debugging",
            date=date.today(),
            user_id=current_user.id,
            user_type=current_user.__class__.__name__.lower(),
            priority='high',
            color='#dc3545'
        )
        
        db.session.add(test_task)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Test task created',
            'task': {
                'id': test_task.id,
                'title': test_task.title,
                'date': test_task.date.isoformat(),
                'user_id': test_task.user_id,
                'user_type': test_task.user_type
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        })
