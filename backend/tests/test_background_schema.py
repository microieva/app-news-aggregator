import sqlite3
import os
import sys

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_schema():
    """Quick test without pytest"""
    db_path = "content_aggregator.db"  # Adjust if your DB has different name
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        print(f"📁 Current directory: {os.getcwd()}")
        print(f"📁 Files in current directory: {os.listdir('.')}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all columns - SQLite PRAGMA returns 6 columns, not 5
        cursor.execute("PRAGMA table_info(summaries)")
        columns = cursor.fetchall()
        
        print("📊 Current columns in 'summaries' table:")
        column_names = []
        for col in columns:
            # SQLite PRAGMA table_info returns: cid, name, type, notnull, dflt_value, pk
            cid, name, type_, not_null, default_value, pk = col
            column_names.append(name)
            nullable = "NULL" if not not_null else "NOT NULL"
            print(f"  - {name} ({type_}) - {nullable}")
        
        # Check required columns
        required_columns = ['task_id', 'status', 'started_at', 'completed_at']
        print(f"\n🔍 Checking required columns:")
        
        all_exist = True
        for col in required_columns:
            exists = col in column_names
            status = "✅ EXISTS" if exists else "❌ MISSING"
            print(f"  - {col}: {status}")
            if not exists:
                all_exist = False
        
        # Check indexes
        print(f"\n📈 Checking indexes:")
        cursor.execute("PRAGMA index_list(summaries)")
        indexes = cursor.fetchall()
        index_names = [idx[1] for idx in indexes]  # idx[1] is the index name
        
        print("Found indexes:")
        for idx in indexes:
            seq, name, unique = idx[0], idx[1], idx[2]
            print(f"  - {name} (unique: {bool(unique)})")
        
        required_indexes = ['ix_summaries_task_id', 'ix_summaries_status']
        all_indexes_exist = True
        for idx in required_indexes:
            exists = idx in index_names
            status = "✅ EXISTS" if exists else "❌ MISSING"
            print(f"  - {idx}: {status}")
            if not exists:
                all_indexes_exist = False
        
        # Test data insertion
        print(f"\n🧪 Testing data insertion:")
        try:
            # First, check if we have any articles to reference
            cursor.execute("SELECT id FROM articles LIMIT 1")
            article_result = cursor.fetchone()
            
            if article_result:
                article_id = article_result[0]
                print(f"  Using existing article ID: {article_id}")
            else:
                # Create a test article if none exists
                print("  No articles found, creating test article...")
                cursor.execute("INSERT INTO topics (name, description) VALUES (?, ?)", 
                             ("Test Topic", "Test Description"))
                topic_id = cursor.lastrowid
                
                cursor.execute("""
                    INSERT INTO articles 
                    (title, url, content, source, topic_id) 
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    "Test Article", 
                    "https://example.com/test", 
                    "Test content for schema validation",
                    "test",
                    topic_id
                ))
                article_id = cursor.lastrowid
                conn.commit()
                print(f"  Created test article with ID: {article_id}")
            
            # Now test inserting a summary
            cursor.execute("""
                INSERT INTO summaries 
                (article_id, content, provider, model_name, quality_level, 
                 word_count, char_count, processing_time_ms, is_successful,
                 task_id, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article_id,
                'Test summary content for schema validation',
                'test-provider',
                'test-model',
                'standard',
                10,
                50,
                100,
                1,  # True
                'test-task-uuid-12345',
                'pending'
            ))
            conn.commit()
            print("  ✅ Can insert data with new columns")
            
            # Verify we can read it back
            cursor.execute(
                "SELECT task_id, status FROM summaries WHERE task_id = ?",
                ('test-task-uuid-12345',)
            )
            row = cursor.fetchone()
            
            if row:
                print(f"  ✅ Can read back data: task_id='{row[0]}', status='{row[1]}'")
            else:
                print("  ❌ Failed to read back inserted data")
                
        except Exception as e:
            print(f"  ❌ Failed to insert data: {e}")
        
        # Final result
        if all_exist and all_indexes_exist:
            print(f"\n🎉 SUCCESS: All background processing schema requirements are met!")
            return True
        else:
            print(f"\n💥 FAILURE: Some schema requirements are missing!")
            return False
            
    except Exception as e:
        print(f"💥 Error during schema test: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = test_schema()
    sys.exit(0 if success else 1)