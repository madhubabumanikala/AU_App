#!/usr/bin/env python3
"""
Test Post Creation Functionality
Debug script to test post creation without the web interface
"""

def test_post_creation():
    print("Testing Post Creation...")
    
    try:
        # Import Flask app and models
        from app import create_app
        from extensions import db
        from models.social import Post
        from models.user import Student, Admin
        
        app = create_app()
        
        with app.app_context():
            # Create tables if they don't exist
            db.create_all()
            
            # Test 1: Check if Post model can be instantiated
            print("1. Testing Post model instantiation...")
            test_post = Post(
                content="Test post content",
                author_id=1,
                author_type="student",
                visibility="public"
            )
            print("   ✅ Post model created successfully")
            
            # Test 2: Try to add to database
            print("2. Testing database operations...")
            db.session.add(test_post)
            db.session.commit()
            print("   ✅ Post saved to database successfully")
            
            # Test 3: Query the post back
            print("3. Testing post retrieval...")
            retrieved_post = Post.query.filter_by(content="Test post content").first()
            if retrieved_post:
                print(f"   ✅ Post retrieved: ID {retrieved_post.id}")
            else:
                print("   ❌ Failed to retrieve post")
                return False
            
            # Test 4: Check author property
            print("4. Testing author property...")
            try:
                author = retrieved_post.author
                print(f"   ✅ Author property accessible: {author}")
            except Exception as e:
                print(f"   ⚠️ Author property issue: {e}")
            
            # Clean up
            db.session.delete(retrieved_post)
            db.session.commit()
            print("   ✅ Cleanup completed")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_models():
    print("\nTesting User Models...")
    
    try:
        from app import create_app
        from extensions import db
        from models.user import Student, Admin
        
        app = create_app()
        
        with app.app_context():
            # Test Student model
            print("1. Testing Student model...")
            test_student = Student(
                email="test@student.com",
                student_id="TEST123",
                first_name="Test",
                last_name="Student",
                department="Computer Science",
                year=2
            )
            test_student.set_password("testpass")
            
            db.session.add(test_student)
            db.session.commit()
            
            student_id = test_student.id
            print(f"   ✅ Student created with ID: {student_id}")
            
            # Test Admin model
            print("2. Testing Admin model...")
            test_admin = Admin(
                email="test@admin.com",
                username="testadmin",
                first_name="Test",
                last_name="Admin"
            )
            test_admin.set_password("testpass")
            
            db.session.add(test_admin)
            db.session.commit()
            
            admin_id = test_admin.id
            print(f"   ✅ Admin created with ID: {admin_id}")
            
            # Test Post with real users
            print("3. Testing Post with real user...")
            from models.social import Post
            
            test_post = Post(
                content="Test post with real student",
                author_id=student_id,
                author_type="student",
                visibility="public"
            )
            
            db.session.add(test_post)
            db.session.commit()
            
            # Test author property
            author = test_post.author
            if author:
                print(f"   ✅ Post author retrieved: {author.first_name} {author.last_name}")
            else:
                print("   ❌ Post author is None")
            
            # Cleanup
            db.session.delete(test_post)
            db.session.delete(test_student)
            db.session.delete(test_admin)
            db.session.commit()
            
            return True
            
    except Exception as e:
        print(f"❌ Error testing user models: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("POST CREATION DEBUG TEST")
    print("=" * 50)
    
    success1 = test_post_creation()
    success2 = test_user_models()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    
    if success1 and success2:
        print("✅ All tests passed - Post creation should work!")
    else:
        print("❌ Some tests failed - Issues need to be resolved")
        
    print("\nNext steps:")
    print("- If tests pass, check web form submission")
    print("- If tests fail, fix database model issues")
    print("- Check Flask route debugging")
