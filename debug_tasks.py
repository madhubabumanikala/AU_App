#!/usr/bin/env python3
"""
Debug Task Display Issue
Quick test script to check task creation and retrieval
"""

def test_task_creation_and_display():
    print("Testing Task Creation and Display...")
    
    try:
        from app import create_app
        from extensions import db
        from models.task import Task
        from models.user import Student, Admin
        from datetime import datetime, date
        
        app = create_app()
        
        with app.app_context():
            # Create tables if they don't exist
            db.create_all()
            
            # Test 1: Check if we can create a task manually
            print("1. Testing manual task creation...")
            test_task = Task(
                title="Test Task",
                description="Test task description",
                date=date.today(),
                user_id=1,
                user_type="student",
                priority="medium",
                color="#007bff"
            )
            
            db.session.add(test_task)
            db.session.commit()
            print(f"   ✅ Task created with ID: {test_task.id}")
            
            # Test 2: Query tasks back
            print("2. Testing task retrieval...")
            tasks = Task.query.filter_by(user_id=1, user_type="student", is_active=True).all()
            print(f"   Found {len(tasks)} tasks for user_id=1, user_type=student")
            
            for task in tasks:
                print(f"   - Task {task.id}: {task.title} on {task.date}")
            
            # Test 3: Check task properties
            if tasks:
                task = tasks[0]
                print("3. Testing task properties...")
                print(f"   - Title: {task.title}")
                print(f"   - Date: {task.date}")
                print(f"   - Time: {task.time}")
                print(f"   - Display Time: {task.display_time}")
                print(f"   - Priority: {task.priority}")
                print(f"   - Color: {task.color or task.priority_color}")
                print(f"   - Is Active: {task.is_active}")
                print(f"   - User ID: {task.user_id}")
                print(f"   - User Type: {task.user_type}")
                
                # Test to_dict method
                print("4. Testing to_dict method...")
                task_dict = task.to_dict()
                print(f"   ✅ to_dict works: {task_dict.get('title', 'ERROR')}")
            
            # Test 4: Check date filtering (like calendar does)
            print("5. Testing date filtering...")
            today = date.today()
            start_of_month = today.replace(day=1)
            if today.month == 12:
                end_of_month = date(today.year + 1, 1, 1)
            else:
                end_of_month = date(today.year, today.month + 1, 1)
            
            monthly_tasks = Task.query.filter(
                Task.date >= start_of_month,
                Task.date < end_of_month,
                Task.user_id == 1,
                Task.user_type == "student",
                Task.is_active == True
            ).all()
            
            print(f"   Monthly tasks ({start_of_month} to {end_of_month}): {len(monthly_tasks)}")
            
            # Cleanup
            for task in tasks:
                db.session.delete(task)
            db.session.commit()
            print("   ✅ Cleanup completed")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_calendar_route_simulation():
    print("\nTesting Calendar Route Logic...")
    
    try:
        from app import create_app
        from models.task import Task
        from datetime import datetime
        
        app = create_app()
        
        with app.app_context():
            # Simulate calendar route logic
            year = datetime.now().year
            month = datetime.now().month
            
            # Get date range (same as calendar route)
            start_date = datetime(year, month, 1).date()
            if month == 12:
                end_date = datetime(year + 1, 1, 1).date()
            else:
                end_date = datetime(year, month + 1, 1).date()
            
            print(f"Date range: {start_date} to {end_date}")
            
            # Query tasks (same as calendar route)
            tasks = Task.query.filter(
                Task.date >= start_date,
                Task.date < end_date,
                Task.user_id == 1,  # Assuming user ID 1
                Task.user_type == "student",
                Task.is_active == True
            ).all()
            
            print(f"Found {len(tasks)} tasks in date range")
            
            return True
            
    except Exception as e:
        print(f"❌ Error in calendar simulation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("TASK DISPLAY DEBUG TEST")
    print("=" * 60)
    
    success1 = test_task_creation_and_display()
    success2 = test_calendar_route_simulation()
    
    print("\n" + "=" * 60)
    print("DEBUG RESULTS")
    print("=" * 60)
    
    if success1 and success2:
        print("✅ Task creation and retrieval works - issue likely in template")
        print("\nCheck:")
        print("- Calendar template task display logic")
        print("- JavaScript console for errors")
        print("- Browser network tab for failed API calls")
    else:
        print("❌ Issues found in task system")
        print("- Fix database/model issues first")
        print("- Check Flask app configuration")
