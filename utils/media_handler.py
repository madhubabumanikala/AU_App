"""
Media Upload and Handling Utility
"""
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
import mimetypes
from flask import current_app
import magic

class MediaHandler:
    """Handle media uploads, processing, and validation"""
    
    # Allowed file extensions
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'}
    ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'rtf'}
    ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'aac', 'm4a'}
    
    # File size limits (in bytes)
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_DOCUMENT_SIZE = 20 * 1024 * 1024  # 20MB
    MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50MB
    
    # Thumbnail settings
    THUMBNAIL_SIZE = (400, 400)
    THUMBNAIL_QUALITY = 85
    
    @classmethod
    def get_file_type(cls, filename):
        """Determine file type based on extension"""
        if not filename:
            return None
            
        extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if extension in cls.ALLOWED_IMAGE_EXTENSIONS:
            return 'image'
        elif extension in cls.ALLOWED_VIDEO_EXTENSIONS:
            return 'video'
        elif extension in cls.ALLOWED_DOCUMENT_EXTENSIONS:
            return 'document'
        elif extension in cls.ALLOWED_AUDIO_EXTENSIONS:
            return 'audio'
        
        return None
    
    @classmethod
    def is_allowed_file(cls, filename):
        """Check if file extension is allowed"""
        file_type = cls.get_file_type(filename)
        return file_type is not None
    
    @classmethod
    def validate_file_size(cls, file, file_type):
        """Validate file size based on type"""
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        
        max_sizes = {
            'image': cls.MAX_IMAGE_SIZE,
            'video': cls.MAX_VIDEO_SIZE,
            'document': cls.MAX_DOCUMENT_SIZE,
            'audio': cls.MAX_AUDIO_SIZE
        }
        
        max_size = max_sizes.get(file_type, cls.MAX_DOCUMENT_SIZE)
        return size <= max_size, size
    
    @classmethod
    def generate_unique_filename(cls, filename):
        """Generate unique filename while preserving extension"""
        if not filename:
            return None
            
        extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        unique_name = str(uuid.uuid4())
        
        if extension:
            return f"{unique_name}.{extension}"
        return unique_name
    
    @classmethod
    def create_upload_path(cls, file_type, user_type='general'):
        """Create upload directory path"""
        base_path = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
        
        # Organize by type and date
        from datetime import datetime
        today = datetime.now()
        year_month = today.strftime('%Y/%m')
        
        upload_path = os.path.join(base_path, 'social', file_type, user_type, year_month)
        os.makedirs(upload_path, exist_ok=True)
        
        return upload_path
    
    @classmethod
    def save_file(cls, file, filename, file_type, user_type='general'):
        """Save uploaded file to appropriate directory"""
        if not file or not filename:
            return None, "No file provided"
        
        # Validate file
        if not cls.is_allowed_file(filename):
            return None, f"File type not allowed. Allowed types: {', '.join(cls.get_allowed_extensions())}"
        
        # Validate file size
        is_valid_size, file_size = cls.validate_file_size(file, file_type)
        if not is_valid_size:
            return None, f"File too large. Maximum size for {file_type}: {cls.get_max_size_mb(file_type)}MB"
        
        try:
            # Generate unique filename
            secure_name = secure_filename(filename)
            unique_filename = cls.generate_unique_filename(secure_name)
            
            # Create upload path
            upload_path = cls.create_upload_path(file_type, user_type)
            file_path = os.path.join(upload_path, unique_filename)
            
            # Save file
            file.save(file_path)
            
            # Generate relative URL for database storage
            relative_path = file_path.replace(current_app.config.get('UPLOAD_FOLDER', 'static/uploads'), '').lstrip('/')
            file_url = f"/static/uploads/{relative_path}"
            
            result = {
                'filename': unique_filename,
                'original_filename': filename,
                'file_path': file_path,
                'file_url': file_url,
                'file_type': file_type,
                'file_size': file_size,
                'mime_type': mimetypes.guess_type(filename)[0]
            }
            
            # Generate thumbnail for images and videos
            if file_type in ['image', 'video']:
                thumbnail_url = cls.create_thumbnail(file_path, file_type)
                result['thumbnail_url'] = thumbnail_url
            
            return result, None
            
        except Exception as e:
            return None, f"Error saving file: {str(e)}"
    
    @classmethod
    def create_thumbnail(cls, file_path, file_type):
        """Create thumbnail for image or video"""
        try:
            if file_type == 'image':
                return cls._create_image_thumbnail(file_path)
            elif file_type == 'video':
                return cls._create_video_thumbnail(file_path)
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return None
    
    @classmethod
    def _create_image_thumbnail(cls, image_path):
        """Create thumbnail for image"""
        try:
            # Create thumbnail directory
            thumb_dir = os.path.join(os.path.dirname(image_path), 'thumbnails')
            os.makedirs(thumb_dir, exist_ok=True)
            
            # Generate thumbnail filename
            filename = os.path.basename(image_path)
            thumb_filename = f"thumb_{filename}"
            thumb_path = os.path.join(thumb_dir, thumb_filename)
            
            # Create thumbnail
            with Image.open(image_path) as img:
                # Auto-rotate based on EXIF data
                img = ImageOps.exif_transpose(img)
                
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = rgb_img
                
                # Create thumbnail
                img.thumbnail(cls.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                img.save(thumb_path, 'JPEG', quality=cls.THUMBNAIL_QUALITY)
            
            # Return relative URL
            relative_path = thumb_path.replace(current_app.config.get('UPLOAD_FOLDER', 'static/uploads'), '').lstrip('/')
            return f"/static/uploads/{relative_path}"
            
        except Exception as e:
            print(f"Error creating image thumbnail: {e}")
            return None
    
    @classmethod
    def _create_video_thumbnail(cls, video_path):
        """Create thumbnail for video (requires ffmpeg)"""
        try:
            import subprocess
            
            # Create thumbnail directory
            thumb_dir = os.path.join(os.path.dirname(video_path), 'thumbnails')
            os.makedirs(thumb_dir, exist_ok=True)
            
            # Generate thumbnail filename
            filename = os.path.splitext(os.path.basename(video_path))[0]
            thumb_filename = f"thumb_{filename}.jpg"
            thumb_path = os.path.join(thumb_dir, thumb_filename)
            
            # Use ffmpeg to extract frame at 1 second
            cmd = [
                'ffmpeg', '-i', video_path, '-ss', '00:00:01.000',
                '-vframes', '1', '-s', f'{cls.THUMBNAIL_SIZE[0]}x{cls.THUMBNAIL_SIZE[1]}',
                '-f', 'image2', thumb_path, '-y'
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            
            # Return relative URL
            relative_path = thumb_path.replace(current_app.config.get('UPLOAD_FOLDER', 'static/uploads'), '').lstrip('/')
            return f"/static/uploads/{relative_path}"
            
        except Exception as e:
            print(f"Error creating video thumbnail: {e}")
            # Return default video icon
            return "/static/images/video-icon.png"
    
    @classmethod
    def delete_file(cls, file_url):
        """Delete file and its thumbnail"""
        try:
            if not file_url:
                return True
            
            # Convert URL to file path
            base_path = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
            file_path = file_url.replace('/static/uploads/', '').lstrip('/')
            full_path = os.path.join(base_path, file_path)
            
            # Delete main file
            if os.path.exists(full_path):
                os.remove(full_path)
            
            # Delete thumbnail if exists
            thumb_dir = os.path.join(os.path.dirname(full_path), 'thumbnails')
            filename = os.path.basename(full_path)
            thumb_filename = f"thumb_{filename}"
            thumb_path = os.path.join(thumb_dir, thumb_filename)
            
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
            
            return True
            
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    @classmethod
    def get_allowed_extensions(cls):
        """Get all allowed extensions"""
        return (cls.ALLOWED_IMAGE_EXTENSIONS | cls.ALLOWED_VIDEO_EXTENSIONS | 
                cls.ALLOWED_DOCUMENT_EXTENSIONS | cls.ALLOWED_AUDIO_EXTENSIONS)
    
    @classmethod
    def get_max_size_mb(cls, file_type):
        """Get max file size in MB for file type"""
        max_sizes = {
            'image': cls.MAX_IMAGE_SIZE / (1024 * 1024),
            'video': cls.MAX_VIDEO_SIZE / (1024 * 1024),
            'document': cls.MAX_DOCUMENT_SIZE / (1024 * 1024),
            'audio': cls.MAX_AUDIO_SIZE / (1024 * 1024)
        }
        return max_sizes.get(file_type, 20)
    
    @classmethod
    def get_file_info(cls, file_path):
        """Get file information"""
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            mime_type = mimetypes.guess_type(file_path)[0]
            
            return {
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'mime_type': mime_type,
                'extension': os.path.splitext(file_path)[1].lower()
            }
        except:
            return None
