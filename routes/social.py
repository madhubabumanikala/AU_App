"""
Social Media Routes for AU Event System
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.social import Post, PostLike, PostComment, PostShare, PostView
from models.event import Event
from extensions import db
from utils.media_handler import MediaHandler
from utils.mobile_detector import mobile_template
from datetime import datetime
import os

social_bp = Blueprint('social', __name__)

@social_bp.route('/feed')
@login_required
def social_feed():
    """Main social feed page"""
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('filter', 'all')  # all, department, following
    
    # Build query based on filter
    query = Post.query.filter_by(is_active=True)
    
    if filter_type == 'department' and hasattr(current_user, 'department'):
        # Show posts from same department or public posts
        query = query.join(Post.author).filter(
            db.or_(
                Post.visibility == 'public',
                db.and_(
                    Post.visibility == 'department',
                    Post.author.department == current_user.department
                )
            )
        )
    elif filter_type == 'events':
        # Show only event-related posts
        query = query.filter(Post.event_id.isnot(None))
    
    # Order by pinned first, then by date
    posts = query.order_by(Post.is_pinned.desc(), Post.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template(mobile_template('social/feed.html'), 
                         posts=posts, 
                         filter_type=filter_type)

@social_bp.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """Create new post"""
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        event_id = request.form.get('event_id', type=int)
        visibility = request.form.get('visibility', 'public')
        
        if not content:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Post content is required'})
            flash('Post content is required', 'error')
            return redirect(url_for('social.create_post'))
        
        # Handle media upload
        media_url = None
        media_type = None
        media_thumbnail = None
        
        if 'media_file' in request.files:
            file = request.files['media_file']
            if file and file.filename and MediaHandler.is_allowed_file(file.filename):
                file_type = MediaHandler.get_file_type(file.filename)
                user_type = current_user.__class__.__name__.lower()
                
                result, error = MediaHandler.save_file(file, file.filename, file_type, user_type)
                if result:
                    media_url = result['file_url']
                    media_type = result['file_type']
                    media_thumbnail = result.get('thumbnail_url')
                elif error:
                    if request.is_json:
                        return jsonify({'success': False, 'message': error})
                    flash(error, 'error')
                    return redirect(url_for('social.create_post'))
        
        try:
            # Create post
            post = Post(
                content=content,
                media_type=media_type,
                media_url=media_url,
                media_thumbnail=media_thumbnail,
                author_id=current_user.id,
                author_type=current_user.__class__.__name__.lower(),
                event_id=event_id,
                visibility=visibility
            )
            
            db.session.add(post)
            db.session.commit()
            
            if request.is_json:
                return jsonify({
                    'success': True, 
                    'message': 'Post created successfully!',
                    'post': post.to_dict()
                })
            
            flash('Post created successfully!', 'success')
            return redirect(url_for('social.social_feed'))
            
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'success': False, 'message': 'Error creating post'})
            flash('Error creating post', 'error')
            return redirect(url_for('social.create_post'))
    
    # GET request - show create post form
    events = Event.query.filter(
        Event.date >= datetime.utcnow().date(),
        Event.is_active == True
    ).order_by(Event.date).limit(20).all()
    
    return render_template(mobile_template('social/create_post.html'), events=events)

@social_bp.route('/post/<int:post_id>')
@login_required
def post_details(post_id):
    """View single post with all comments"""
    post = Post.query.get_or_404(post_id)
    
    # Check visibility permissions
    if not can_view_post(post, current_user):
        flash('You do not have permission to view this post', 'error')
        return redirect(url_for('social.social_feed'))
    
    # Track view
    track_post_view(post, current_user)
    
    # Get comments
    comments = post.comments.filter_by(is_active=True, parent_id=None).order_by(
        PostComment.created_at.asc()
    ).all()
    
    return render_template(mobile_template('social/post_details.html'), 
                         post=post, 
                         comments=comments)

@social_bp.route('/api/post/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like(post_id):
    """Toggle like on a post"""
    post = Post.query.get_or_404(post_id)
    
    if not can_view_post(post, current_user):
        return jsonify({'success': False, 'message': 'Permission denied'})
    
    user_type = current_user.__class__.__name__.lower()
    existing_like = PostLike.query.filter_by(
        post_id=post_id,
        user_id=current_user.id,
        user_type=user_type
    ).first()
    
    try:
        if existing_like:
            # Unlike
            db.session.delete(existing_like)
            post.likes_count = max(0, post.likes_count - 1)
            liked = False
        else:
            # Like
            new_like = PostLike(
                post_id=post_id,
                user_id=current_user.id,
                user_type=user_type
            )
            db.session.add(new_like)
            post.likes_count += 1
            liked = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'liked': liked,
            'likes_count': post.likes_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error updating like'})

@social_bp.route('/api/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """Add comment to a post"""
    post = Post.query.get_or_404(post_id)
    
    if not can_view_post(post, current_user):
        return jsonify({'success': False, 'message': 'Permission denied'})
    
    content = request.json.get('content', '').strip()
    parent_id = request.json.get('parent_id', type=int)
    
    if not content:
        return jsonify({'success': False, 'message': 'Comment content is required'})
    
    try:
        comment = PostComment(
            post_id=post_id,
            content=content,
            author_id=current_user.id,
            author_type=current_user.__class__.__name__.lower(),
            parent_id=parent_id
        )
        
        db.session.add(comment)
        post.comments_count += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'comment': comment.to_dict(),
            'comments_count': post.comments_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error adding comment'})

@social_bp.route('/api/post/<int:post_id>/share', methods=['POST'])
@login_required
def share_post(post_id):
    """Share a post"""
    post = Post.query.get_or_404(post_id)
    
    if not can_view_post(post, current_user):
        return jsonify({'success': False, 'message': 'Permission denied'})
    
    share_type = request.json.get('share_type', 'share')
    user_type = current_user.__class__.__name__.lower()
    
    # Check if already shared
    existing_share = PostShare.query.filter_by(
        post_id=post_id,
        user_id=current_user.id,
        user_type=user_type
    ).first()
    
    if existing_share:
        return jsonify({'success': False, 'message': 'Already shared this post'})
    
    try:
        share = PostShare(
            post_id=post_id,
            user_id=current_user.id,
            user_type=user_type,
            share_type=share_type
        )
        
        db.session.add(share)
        post.shares_count += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'shares_count': post.shares_count,
            'message': 'Post shared successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error sharing post'})

@social_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Edit a post"""
    post = Post.query.get_or_404(post_id)
    
    if not post.can_edit(current_user):
        flash('You do not have permission to edit this post', 'error')
        return redirect(url_for('social.post_details', post_id=post_id))
    
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        visibility = request.form.get('visibility', post.visibility)
        
        if not content:
            flash('Post content is required', 'error')
            return redirect(url_for('social.edit_post', post_id=post_id))
        
        try:
            post.content = content
            post.visibility = visibility
            post.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Post updated successfully!', 'success')
            return redirect(url_for('social.post_details', post_id=post_id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating post', 'error')
    
    return render_template(mobile_template('social/edit_post.html'), post=post)

@social_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Delete a post"""
    post = Post.query.get_or_404(post_id)
    
    if not post.can_delete(current_user):
        return jsonify({'success': False, 'message': 'Permission denied'})
    
    try:
        # Delete associated media files
        if post.media_url:
            MediaHandler.delete_file(post.media_url)
        if post.media_thumbnail:
            MediaHandler.delete_file(post.media_thumbnail)
        
        # Mark as inactive instead of deleting to preserve data integrity
        post.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Post deleted successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error deleting post'})

@social_bp.route('/api/posts/recent')
def get_recent_posts():
    """API endpoint for recent posts"""
    limit = request.args.get('limit', 10, type=int)
    filter_type = request.args.get('filter', 'all')
    
    query = Post.query.filter_by(is_active=True)
    
    if filter_type == 'events':
        query = query.filter(Post.event_id.isnot(None))
    elif filter_type == 'department' and current_user.is_authenticated and hasattr(current_user, 'department'):
        query = query.join(Post.author).filter(
            db.or_(
                Post.visibility == 'public',
                db.and_(
                    Post.visibility == 'department',
                    Post.author.department == current_user.department
                )
            )
        )
    
    posts = query.order_by(Post.is_pinned.desc(), Post.created_at.desc()).limit(limit).all()
    
    return jsonify({
        'success': True,
        'posts': [post.to_dict() for post in posts]
    })

# Helper functions
def can_view_post(post, user):
    """Check if user can view the post"""
    if not post.is_active:
        return False
    
    if post.visibility == 'public':
        return True
    
    if not user.is_authenticated:
        return False
    
    if post.visibility == 'private':
        return (user.id == post.author_id and 
                user.__class__.__name__.lower() == post.author_type)
    
    if post.visibility == 'department':
        if hasattr(user, 'department') and hasattr(post.author, 'department'):
            return user.department == post.author.department
    
    return user.is_admin if hasattr(user, 'is_admin') else False

def track_post_view(post, user):
    """Track post view for analytics"""
    try:
        # Check if user already viewed this post recently (within last hour)
        from datetime import timedelta
        recent_view = PostView.query.filter_by(
            post_id=post.id,
            user_id=user.id if user.is_authenticated else None,
            user_type=user.__class__.__name__.lower() if user.is_authenticated else None
        ).filter(
            PostView.viewed_at >= datetime.utcnow() - timedelta(hours=1)
        ).first()
        
        if not recent_view:
            view = PostView(
                post_id=post.id,
                user_id=user.id if user.is_authenticated else None,
                user_type=user.__class__.__name__.lower() if user.is_authenticated else None,
                ip_address=request.remote_addr
            )
            
            db.session.add(view)
            post.views_count += 1
            db.session.commit()
            
    except Exception as e:
        # Don't let view tracking errors break the main functionality
        db.session.rollback()
