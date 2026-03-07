"""
Personal Task Routes for AU Event System
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models.task import Task
from extensions import db
from datetime import datetime, date

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    """Get user's tasks for calendar display"""
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    query = Task.query.filter_by(
        user_id=current_user.id,
        user_type=current_user.__class__.__name__.lower(),
        is_active=True
    )
    
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Task.date >= start, Task.date <= end)
        except ValueError:
            pass
    
    tasks = query.all()
    return jsonify([task.to_dict() for task in tasks])

@tasks_bp.route('/api/task', methods=['POST'])
@login_required
def create_task():
    """Create new personal task"""
    try:
        data = request.get_json() or request.form
        
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        task_date = data.get('date')
        task_time = data.get('time')
        priority = data.get('priority', 'medium')
        color = data.get('color', '#007bff')
        
        if not title:
            return jsonify({'success': False, 'message': 'Task title is required'})
        
        if not task_date:
            return jsonify({'success': False, 'message': 'Task date is required'})
        
        # Parse date
        try:
            parsed_date = datetime.strptime(task_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid date format'})
        
        # Parse time (optional)
        parsed_time = None
        if task_time:
            try:
                parsed_time = datetime.strptime(task_time, '%H:%M').time()
            except ValueError:
                try:
                    parsed_time = datetime.strptime(task_time, '%I:%M %p').time()
                except ValueError:
                    return jsonify({'success': False, 'message': 'Invalid time format'})
        
        # Create task
        task = Task(
            title=title,
            description=description,
            date=parsed_date,
            time=parsed_time,
            user_id=current_user.id,
            user_type=current_user.__class__.__name__.lower(),
            priority=priority,
            color=color
        )
        
        db.session.add(task)
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Task created successfully!',
                'task': task.to_dict()
            })
        
        flash('Task created successfully!', 'success')
        return redirect(url_for('main.calendar_view'))
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error creating task: {str(e)}'})

@tasks_bp.route('/api/task/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    """Update existing task"""
    task = Task.query.get_or_404(task_id)
    
    if not task.can_edit(current_user):
        return jsonify({'success': False, 'message': 'Permission denied'})
    
    try:
        data = request.get_json() or request.form
        
        # Update fields if provided
        if 'title' in data:
            title = data['title'].strip()
            if not title:
                return jsonify({'success': False, 'message': 'Task title is required'})
            task.title = title
        
        if 'description' in data:
            task.description = data['description'].strip()
        
        if 'date' in data:
            try:
                task.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid date format'})
        
        if 'time' in data:
            if data['time']:
                try:
                    task.time = datetime.strptime(data['time'], '%H:%M').time()
                except ValueError:
                    try:
                        task.time = datetime.strptime(data['time'], '%I:%M %p').time()
                    except ValueError:
                        return jsonify({'success': False, 'message': 'Invalid time format'})
            else:
                task.time = None
        
        if 'priority' in data:
            task.priority = data['priority']
        
        if 'status' in data:
            task.status = data['status']
        
        if 'color' in data:
            task.color = data['color']
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Task updated successfully!',
            'task': task.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error updating task: {str(e)}'})

@tasks_bp.route('/api/task/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task_status(task_id):
    """Toggle task completion status"""
    task = Task.query.get_or_404(task_id)
    
    if not task.can_edit(current_user):
        return jsonify({'success': False, 'message': 'Permission denied'})
    
    try:
        if task.status == 'completed':
            task.mark_pending()
            message = 'Task marked as pending'
        else:
            task.mark_completed()
            message = 'Task marked as completed'
        
        return jsonify({
            'success': True,
            'message': message,
            'task': task.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error toggling task: {str(e)}'})

@tasks_bp.route('/api/task/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    """Delete task"""
    task = Task.query.get_or_404(task_id)
    
    if not task.can_edit(current_user):
        return jsonify({'success': False, 'message': 'Permission denied'})
    
    try:
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Task deleted successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error deleting task: {str(e)}'})

@tasks_bp.route('/task/create', methods=['GET', 'POST'])
@login_required
def create_task_form():
    """Task creation form page"""
    if request.method == 'POST':
        return create_task()
    
    # GET request - show form with optional date pre-selected
    selected_date = request.args.get('date', datetime.now().date().isoformat())
    
    return render_template('tasks/create_task.html', selected_date=selected_date)

@tasks_bp.route('/tasks')
@login_required
def my_tasks():
    """View user's tasks"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    
    query = Task.query.filter_by(
        user_id=current_user.id,
        user_type=current_user.__class__.__name__.lower(),
        is_active=True
    )
    
    if status == 'pending':
        query = query.filter_by(status='pending')
    elif status == 'completed':
        query = query.filter_by(status='completed')
    
    tasks = query.order_by(Task.date.desc(), Task.time.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('tasks/my_tasks.html', 
                         tasks=tasks, 
                         current_status=status)
