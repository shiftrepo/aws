from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt
import sqlite3
import json
from datetime import datetime, timedelta
import os
import sys
import logging

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app,
     origins=["*"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=True)

# Configure logging with console handler
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = app.logger
logger.setLevel(logging.DEBUG)

# Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
jwt = JWTManager(app)

DATABASE_PATH = os.getenv('DATABASE_PATH', '/app/data/scheduler.db')

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    """Check password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def is_admin_user(username):
    """Check if user is admin"""
    return username == 'admin'

# API Routes

@app.route('/api/register', methods=['POST'])
def register():
    """User registration with detailed logging"""
    logger.info(f"🔥 REGISTRATION: Request started from {request.remote_addr}")

    # Log request headers
    logger.info(f"🔥 REGISTRATION: Headers - {dict(request.headers)}")

    # Get and validate JSON data
    data = request.get_json()
    logger.info(f"🔥 REGISTRATION: Received data - {data}")

    if data is None:
        logger.error("❌ REGISTRATION: No JSON data received")
        return jsonify({"error": "No JSON data provided"}), 400

    required_fields = ['username', 'password', 'start_time', 'end_time']
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        logger.error(f"❌ REGISTRATION: Missing fields - {missing_fields}")
        return jsonify({"error": f"Missing required fields: {missing_fields}"}), 400

    logger.info(f"✅ REGISTRATION: All fields present for user '{data['username']}'")

    conn = get_db_connection()
    logger.info("✅ REGISTRATION: Database connection established")

    # Check if user already exists
    try:
        existing_user = conn.execute(
            'SELECT id FROM users WHERE username = ?', (data['username'],)
        ).fetchone()
        logger.info(f"✅ REGISTRATION: User existence check completed")

        if existing_user:
            conn.close()
            logger.warning(f"❌ REGISTRATION: Username '{data['username']}' already exists")
            return jsonify({"error": "Username already exists"}), 400

        # Create new user (simple password storage)
        logger.info(f"🔄 REGISTRATION: Storing user '{data['username']}' with simple password")

        logger.info(f"🔄 REGISTRATION: Inserting user '{data['username']}' into database")
        conn.execute('''
            INSERT INTO users (username, password_hash, start_time, end_time, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['username'], data['password'], data['start_time'],
              data['end_time'], datetime.now().isoformat()))
        conn.commit()
        conn.close()

        logger.info(f"🎉 REGISTRATION: User '{data['username']}' registered successfully!")
        return jsonify({"message": "User registered successfully"}), 201

    except sqlite3.Error as e:
        conn.close()
        logger.error(f"💥 REGISTRATION: Database error - {str(e)}")
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500
    except Exception as e:
        conn.close()
        logger.error(f"💥 REGISTRATION: Unexpected error - {str(e)}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Simple user login - accepts any valid username/password combination"""
    data = request.get_json()

    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password required"}), 400

    conn = get_db_connection()
    user = conn.execute(
        'SELECT id, username, password_hash FROM users WHERE username = ?',
        (data['username'],)
    ).fetchone()
    conn.close()

    # Simple authentication - if user exists and password matches, allow login
    if user and data['password'] == user['password_hash']:
        access_token = create_access_token(
            identity=str(user['id']),
            additional_claims={"username": user['username']}
        )
        logger.info(f"✅ LOGIN SUCCESS: User '{user['username']}' logged in successfully")
        return jsonify({
            "access_token": access_token,
            "user": {
                "id": user['id'],
                "username": user['username']
            }
        })

    logger.warning(f"❌ LOGIN FAILED: Invalid credentials for '{data.get('username', 'unknown')}'")
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/availability', methods=['POST'])
@jwt_required()
def save_availability():
    """Save user availability"""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data.get('availability'):
        return jsonify({"error": "Availability data required"}), 400

    conn = get_db_connection()

    # Delete existing availability for this user
    conn.execute('DELETE FROM availability WHERE user_id = ?', (user_id,))

    # Save new availability
    for day, times in data['availability'].items():
        for time_slot in times:
            conn.execute('''
                INSERT INTO availability (user_id, day_of_week, start_time, end_time, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, day, time_slot['start'], time_slot['end'],
                  datetime.now().isoformat()))

    conn.commit()
    conn.close()

    return jsonify({"message": "Availability saved successfully"})

@app.route('/api/availability')
@jwt_required()
def get_availability():
    """Get user availability"""
    user_id = int(get_jwt_identity())

    conn = get_db_connection()
    availability = conn.execute('''
        SELECT day_of_week, start_time, end_time
        FROM availability
        WHERE user_id = ?
        ORDER BY day_of_week, start_time
    ''', (user_id,)).fetchall()
    conn.close()

    # Group by day
    result = {}
    for slot in availability:
        day = slot['day_of_week']
        if day not in result:
            result[day] = []
        result[day].append({
            'start': slot['start_time'],
            'end': slot['end_time']
        })

    return jsonify(result)

@app.route('/api/availability/all')
@jwt_required()
def get_all_availability():
    """Get all users' availability with detailed error handling"""
    try:
        logger.info("🔥 AVAILABILITY/ALL: Request started")
        current_user_id = get_jwt_identity()
        logger.info(f"🔥 AVAILABILITY/ALL: JWT user ID: {current_user_id}")

        conn = get_db_connection()
        logger.info("✅ AVAILABILITY/ALL: Database connection established")

        # Get all users with their availability (exclude admin)
        query = '''
            SELECT u.id, u.username, u.start_time, u.end_time,
                   a.day_of_week, a.start_time as avail_start, a.end_time as avail_end
            FROM users u
            LEFT JOIN availability a ON u.id = a.user_id
            WHERE u.username != 'admin'
            ORDER BY u.username, a.day_of_week, a.start_time
        '''

        rows = conn.execute(query).fetchall()
        logger.info(f"✅ AVAILABILITY/ALL: Query returned {len(rows)} rows")
        conn.close()

        # Group by user
        users = {}
        for row in rows:
            user_id = row['id']
            if user_id not in users:
                users[user_id] = {
                    'id': user_id,
                    'username': row['username'],
                    'work_hours': {
                        'start': row['start_time'],
                        'end': row['end_time']
                    },
                    'availability': {}
                }

            if row['day_of_week']:
                day = row['day_of_week']
                if day not in users[user_id]['availability']:
                    users[user_id]['availability'][day] = []

                users[user_id]['availability'][day].append({
                    'start': row['avail_start'],
                    'end': row['avail_end']
                })

        result = list(users.values())
        logger.info(f"🎉 AVAILABILITY/ALL: Returning {len(result)} users")
        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ AVAILABILITY/ALL: Error occurred: {str(e)}")
        logger.error(f"❌ AVAILABILITY/ALL: Error type: {type(e).__name__}")
        return jsonify({"error": f"Failed to get availability: {str(e)}"}), 500

@app.route('/api/grid-schedule')
@jwt_required()
def get_grid_schedule():
    """
    シンプルな固定グリッドスケジュール
    7:00-19:00を30分刻みでSQLデータを正確にマッピング
    """
    conn = get_db_connection()

    # 全ユーザーの情報を取得（adminを除外）
    users_query = '''
        SELECT id, username FROM users WHERE username != 'admin' ORDER BY username
    '''
    all_users = {row['id']: row['username'] for row in conn.execute(users_query).fetchall()}

    # 全ユーザーのavailabilityを取得（adminを除外）
    query = '''
        SELECT u.id, u.username, a.day_of_week, a.start_time, a.end_time
        FROM users u
        LEFT JOIN availability a ON u.id = a.user_id
        WHERE u.username != 'admin'
        ORDER BY u.username, a.day_of_week, a.start_time
    '''

    rows = conn.execute(query).fetchall()
    conn.close()

    # グリッドロジックをimport
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from grid_logic import create_time_grid, time_to_grid_index, check_user_availability_in_slot

    # 固定グリッド作成
    time_grid = create_time_grid()

    # ユーザーごとのavailabilityを整理
    user_availability = {}
    for row in rows:
        user_id = row['id']
        username = row['username']

        if user_id not in user_availability:
            user_availability[user_id] = {'username': username, 'days': {}}

        if row['day_of_week']:
            day = row['day_of_week']
            if day not in user_availability[user_id]['days']:
                user_availability[user_id]['days'][day] = []

            user_availability[user_id]['days'][day].append({
                'start': row['start_time'],
                'end': row['end_time']
            })

    # 各曜日の各グリッドスロットでの参加者を計算
    DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']

    result = {}
    for day in DAYS_OF_WEEK:
        day_grid = []

        for grid_slot in time_grid:
            available_users = []

            # 各ユーザーがこのスロットで利用可能かチェック
            for user_id, user_data in user_availability.items():
                if check_user_availability_in_slot(user_data['days'], day, grid_slot):
                    available_users.append(user_data['username'])

            # 参加者がいる場合のみ記録
            if available_users:
                day_grid.append({
                    'grid_index': grid_slot['index'],
                    'start': grid_slot['start'],
                    'end': grid_slot['end'],
                    'participant_count': len(available_users),
                    'available_users': sorted(available_users),
                    'unavailable_users': [username for uid, username in all_users.items()
                                        if username not in available_users],
                    'availability_percentage': round((len(available_users) / len(all_users)) * 100, 1)
                })

        if day_grid:
            result[day] = day_grid

    return jsonify({
        'grid_schedule': result,
        'total_users': len(all_users),
        'time_grid_info': {
            'start_time': '07:00',
            'end_time': '19:00',
            'slot_duration': 30,  # minutes
            'total_slots': len(time_grid)
        },
        'grid_mapping': time_grid  # デバッグ用
    })

@app.route('/api/test/database')
def test_database_connection():
    """データベース接続とテーブル存在確認用テストエンドポイント"""
    try:
        conn = get_db_connection()

        # テーブル存在確認
        tables_check = {}

        # usersテーブル確認
        try:
            result = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()
            tables_check['users'] = {
                'exists': True,
                'count': result['count'] if result else 0
            }
        except Exception as e:
            tables_check['users'] = {
                'exists': False,
                'error': str(e)
            }

        # availabilityテーブル確認
        try:
            result = conn.execute("SELECT COUNT(*) as count FROM availability").fetchone()
            tables_check['availability'] = {
                'exists': True,
                'count': result['count'] if result else 0
            }
        except Exception as e:
            tables_check['availability'] = {
                'exists': False,
                'error': str(e)
            }

        # データベースパス確認
        db_path = os.getenv('DATABASE_PATH', '/app/data/scheduler.db')
        db_exists = os.path.exists(db_path)

        conn.close()

        return jsonify({
            "success": True,
            "database_path": db_path,
            "database_exists": db_exists,
            "tables": tables_check,
            "version": "v2.1.4"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "database_path": os.getenv('DATABASE_PATH', '/app/data/scheduler.db'),
            "version": "v2.1.4"
        }), 500

@app.route('/api/test/llm-analysis')
def test_llm_analysis():
    """LLM分析機能テスト用エンドポイント（認証不要）"""
    try:
        # データベース接続テスト
        conn = get_db_connection()

        # 基本的なデータ取得テスト
        users_query = 'SELECT id, username FROM users ORDER BY username'
        users = conn.execute(users_query).fetchall()

        if not users:
            return jsonify({
                "success": False,
                "error": "No users found in database",
                "version": "v2.1.4"
            }), 400

        # meeting_candidates.pyの直接テスト
        from meeting_candidates import MeetingCandidateAnalyzer

        analyzer = MeetingCandidateAnalyzer()

        # 簡単な分析テスト
        candidates = analyzer.analyze_meeting_candidates()

        return jsonify({
            "success": True,
            "users_count": len(users),
            "candidates_count": len(candidates) if candidates else 0,
            "sample_candidates": candidates[:2] if candidates else [],
            "analyzer_db_path": analyzer.db_path,
            "llm_available": analyzer.llm_available,
            "version": "v2.1.4"
        })

    except Exception as e:
        import traceback
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "version": "v2.1.4"
        }), 500

@app.route('/api/llm-analysis')
@jwt_required()
def run_llm_analysis():
    """LLMを使用した会議時間候補分析"""
    try:
        logger.info("🤖 LLM分析を開始...")

        # meeting_candidates.pyを直接importして分析実行
        from meeting_candidates import MeetingCandidateAnalyzer

        # 環境変数から正しいデータベースパスを設定
        analyzer = MeetingCandidateAnalyzer()

        candidates, all_users = analyzer.analyze_meeting_candidates()
        # LLMを使用した高度な分析を実行
        top_candidates = analyzer.analyze_with_llm(candidates, all_users)

        # 結果を整理
        analysis_result = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'total_candidates': len(candidates),
            'total_users': len(all_users),
            'top_candidates': top_candidates[:4],  # 上位4つ
            'statistics': {
                'total_meeting_slots': len(candidates),
                'max_participation_rate': max(c['availability_percentage'] for c in candidates) if candidates else 0,
                'avg_participation_rate': sum(c['availability_percentage'] for c in candidates) / len(candidates) if candidates else 0,
                'users_with_availability': len(set(c['available_users'][0] for c in candidates if c['available_users'])) if candidates else 0
            }
        }

        logger.info(f"✅ LLM分析完了: {len(top_candidates)}個の候補を生成")
        return jsonify(analysis_result)

    except Exception as e:
        logger.error(f"❌ LLM分析エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"分析中にエラーが発生しました: {str(e)}"}), 500

# Admin Data Management endpoints
@app.route('/api/admin/export', methods=['GET'])
@jwt_required()
def export_all_data():
    """Export all users and schedules to JSON (admin only)"""
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    current_user = conn.execute(
        'SELECT username FROM users WHERE id = ?',
        (current_user_id,)
    ).fetchone()

    if not current_user or not is_admin_user(current_user['username']):
        conn.close()
        return jsonify({"error": "Admin access required"}), 403

    try:
        # Export users (with plain text passwords - as requested)
        users_query = '''
            SELECT id, username, start_time, end_time, created_at
            FROM users
            WHERE username != 'admin'
            ORDER BY id
        '''
        users_rows = conn.execute(users_query).fetchall()

        users_export = []
        for user in users_rows:
            # For export, use default password (as requested - plain text)
            users_export.append({
                "id": user['id'],
                "username": user['username'],
                "password": "admin123",  # Plain text default password
                "start_time": user['start_time'],
                "end_time": user['end_time'],
                "created_at": user['created_at']
            })

        # Export availability
        availability_query = '''
            SELECT a.id, a.user_id, u.username, a.day_of_week, a.start_time, a.end_time, a.created_at
            FROM availability a
            JOIN users u ON a.user_id = u.id
            WHERE u.username != 'admin'
            ORDER BY a.user_id, a.day_of_week, a.start_time
        '''
        availability_rows = conn.execute(availability_query).fetchall()

        availability_export = []
        for avail in availability_rows:
            availability_export.append({
                "id": avail['id'],
                "user_id": avail['user_id'],
                "username": avail['username'],
                "day_of_week": avail['day_of_week'],
                "start_time": avail['start_time'],
                "end_time": avail['end_time'],
                "created_at": avail['created_at']
            })

        conn.close()

        export_data = {
            "export_info": {
                "timestamp": datetime.now().isoformat(),
                "version": "v2.1.24",
                "exported_by": current_user['username']
            },
            "users": users_export,
            "availability": availability_export,
            "statistics": {
                "total_users": len(users_export),
                "total_availability_records": len(availability_export)
            }
        }

        logger.info(f"📤 Data exported by admin: {len(users_export)} users, {len(availability_export)} availability records")
        return jsonify(export_data)

    except Exception as e:
        conn.close()
        logger.error(f"💥 Export error: {str(e)}")
        return jsonify({"error": f"Export failed: {str(e)}"}), 500

@app.route('/api/admin/import', methods=['POST'])
@jwt_required()
def import_all_data():
    """Import users and schedules from JSON (admin only)"""
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    current_user = conn.execute(
        'SELECT username FROM users WHERE id = ?',
        (current_user_id,)
    ).fetchone()

    if not current_user or not is_admin_user(current_user['username']):
        conn.close()
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    if 'users' not in data:
        return jsonify({"error": "Missing 'users' data in JSON"}), 400

    try:
        imported_users = 0
        imported_availability = 0
        errors = []

        # Import users
        for user_data in data['users']:
            try:
                # Check required fields
                required_fields = ['username', 'password', 'start_time', 'end_time']
                if not all(field in user_data for field in required_fields):
                    errors.append(f"User missing required fields: {user_data.get('username', 'unknown')}")
                    continue

                # Check if user already exists
                existing_user = conn.execute(
                    'SELECT id FROM users WHERE username = ?', (user_data['username'],)
                ).fetchone()

                if existing_user:
                    errors.append(f"User '{user_data['username']}' already exists - skipped")
                    continue

                # Simple password storage (matching our simplified auth)
                conn.execute('''
                    INSERT INTO users (username, password_hash, start_time, end_time, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    user_data['username'],
                    user_data['password'],
                    user_data['start_time'],
                    user_data['end_time'],
                    user_data.get('created_at', datetime.now().isoformat())
                ))
                imported_users += 1

            except Exception as e:
                errors.append(f"Failed to import user '{user_data.get('username', 'unknown')}': {str(e)}")

        # Import availability if provided
        if 'availability' in data:
            for avail_data in data['availability']:
                try:
                    # Get user ID by username
                    user_row = conn.execute(
                        'SELECT id FROM users WHERE username = ?', (avail_data['username'],)
                    ).fetchone()

                    if not user_row:
                        errors.append(f"User '{avail_data['username']}' not found for availability import")
                        continue

                    user_id = user_row['id']

                    conn.execute('''
                        INSERT INTO availability (user_id, day_of_week, start_time, end_time, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        user_id,
                        avail_data['day_of_week'],
                        avail_data['start_time'],
                        avail_data['end_time'],
                        avail_data.get('created_at', datetime.now().isoformat())
                    ))
                    imported_availability += 1

                except Exception as e:
                    errors.append(f"Failed to import availability for '{avail_data.get('username', 'unknown')}': {str(e)}")

        conn.commit()
        conn.close()

        result = {
            "message": "Import completed",
            "imported_users": imported_users,
            "imported_availability": imported_availability,
            "errors": errors
        }

        logger.info(f"📥 Data imported by admin: {imported_users} users, {imported_availability} availability records")
        return jsonify(result)

    except Exception as e:
        conn.close()
        logger.error(f"💥 Import error: {str(e)}")
        return jsonify({"error": f"Import failed: {str(e)}"}), 500

@app.route('/api/admin/delete-all', methods=['DELETE'])
@jwt_required()
def delete_all_data():
    """Delete all users and schedules (admin only)"""
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    current_user = conn.execute(
        'SELECT username FROM users WHERE id = ?',
        (current_user_id,)
    ).fetchone()

    if not current_user or not is_admin_user(current_user['username']):
        conn.close()
        return jsonify({"error": "Admin access required"}), 403

    try:
        # Count records before deletion
        users_count = conn.execute('SELECT COUNT(*) as count FROM users WHERE username != "admin"').fetchone()['count']
        availability_count = conn.execute('''
            SELECT COUNT(*) as count FROM availability a
            JOIN users u ON a.user_id = u.id
            WHERE u.username != "admin"
        ''').fetchone()['count']

        # Delete all availability for non-admin users
        conn.execute('''
            DELETE FROM availability
            WHERE user_id IN (SELECT id FROM users WHERE username != "admin")
        ''')

        # Delete all non-admin users
        conn.execute('DELETE FROM users WHERE username != "admin"')

        conn.commit()
        conn.close()

        logger.info(f"🗑️ All data deleted by admin: {users_count} users, {availability_count} availability records")
        return jsonify({
            "message": "All user data deleted successfully",
            "deleted_users": users_count,
            "deleted_availability": availability_count
        })

    except Exception as e:
        conn.close()
        logger.error(f"💥 Delete all error: {str(e)}")
        return jsonify({"error": f"Delete operation failed: {str(e)}"}), 500

# Admin only endpoints
@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Get all users (admin only)"""
    # Get current user from JWT
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    current_user = conn.execute(
        'SELECT username FROM users WHERE id = ?',
        (current_user_id,)
    ).fetchone()

    if not current_user or not is_admin_user(current_user['username']):
        conn.close()
        return jsonify({"error": "Admin access required"}), 403

    # Get all users except admin
    users = conn.execute('''
        SELECT id, username, start_time, end_time, created_at
        FROM users
        WHERE username != 'admin'
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()

    users_list = []
    for user in users:
        users_list.append({
            "id": user['id'],
            "username": user['username'],
            "start_time": user['start_time'],
            "end_time": user['end_time'],
            "created_at": user['created_at']
        })

    return jsonify({"users": users_list})

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete user (admin only)"""
    # Get current user from JWT
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    current_user = conn.execute(
        'SELECT username FROM users WHERE id = ?',
        (current_user_id,)
    ).fetchone()

    if not current_user or not is_admin_user(current_user['username']):
        conn.close()
        return jsonify({"error": "Admin access required"}), 403

    # Check if user exists and is not admin
    target_user = conn.execute(
        'SELECT id, username FROM users WHERE id = ?',
        (user_id,)
    ).fetchone()

    if not target_user:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    if target_user['username'] == 'admin':
        conn.close()
        return jsonify({"error": "Cannot delete admin user"}), 403

    try:
        # Delete user's availability and meetings (CASCADE should handle this)
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()

        logger.info(f"🗑️ Admin {current_user['username']} deleted user {target_user['username']} (ID: {user_id})")
        return jsonify({"message": f"User '{target_user['username']}' deleted successfully"})

    except sqlite3.Error as e:
        conn.close()
        logger.error(f"💥 Delete user error: {str(e)}")
        return jsonify({"error": f"Failed to delete user: {str(e)}"}), 500

@app.route('/api/meeting-compatibility')
@jwt_required()
def get_meeting_compatibility():
    """Enhanced meeting compatibility analysis - shows 2+ person overlaps with participant details"""
    conn = get_db_connection()

    # Get all users with their availability and names
    query = '''
        SELECT u.id, u.username, a.day_of_week, a.start_time, a.end_time
        FROM users u
        LEFT JOIN availability a ON u.id = a.user_id
        ORDER BY u.username, a.day_of_week, a.start_time
    '''

    rows = conn.execute(query).fetchall()

    # Get all users for reference
    all_users_query = 'SELECT id, username FROM users ORDER BY username'
    all_users = {row['id']: row['username'] for row in conn.execute(all_users_query).fetchall()}

    conn.close()

    # Group availability by day
    days = {}
    user_availability = {}

    for row in rows:
        user_id = row['id']
        username = row['username']

        # Track all users
        if user_id not in user_availability:
            user_availability[user_id] = {'username': username, 'days': {}}

        # Only process if they have availability
        if row['day_of_week']:
            day = row['day_of_week']
            if day not in days:
                days[day] = []

            days[day].append({
                'start': row['start_time'],
                'end': row['end_time'],
                'user_id': user_id,
                'username': username
            })

            if day not in user_availability[user_id]['days']:
                user_availability[user_id]['days'][day] = []
            user_availability[user_id]['days'][day].append({
                'start': row['start_time'],
                'end': row['end_time']
            })

    # Analyze meeting compatibility for each day
    meeting_slots = {}

    for day, day_slots in days.items():
        if not day_slots:
            continue

        # Create time intervals with user tracking
        intervals = []
        for slot in day_slots:
            intervals.append((slot['start'], 'start', slot['user_id'], slot['username']))
            intervals.append((slot['end'], 'end', slot['user_id'], slot['username']))

        intervals.sort()

        # Find overlapping periods with participant tracking
        active_users = {}  # user_id: username
        meeting_periods = []
        last_time = None

        for time_str, event_type, user_id, username in intervals:
            # Check if we have a valid time period with 1+ people (FIXED: was >= 2)
            if last_time and len(active_users) >= 1 and last_time != time_str:
                # Create list of available and unavailable users
                available_users = list(active_users.values())
                unavailable_users = [username for uid, username in all_users.items()
                                   if uid not in active_users]

                meeting_periods.append({
                    'start': last_time,
                    'end': time_str,
                    'participant_count': len(active_users),
                    'available_users': available_users,
                    'unavailable_users': unavailable_users,
                    'availability_percentage': round((len(active_users) / len(all_users)) * 100, 1)
                })

            if event_type == 'start':
                active_users[user_id] = username
            else:
                active_users.pop(user_id, None)

            last_time = time_str

        if meeting_periods:
            meeting_slots[day] = meeting_periods

    # Separate by participant count: single (1), partial (2+ but not all), full (all users)
    single_slots = {}
    partial_slots = {}
    full_slots = {}

    for day, day_periods in meeting_slots.items():
        single_periods = []
        partial_periods = []
        full_periods = []

        for period in day_periods:
            if period['participant_count'] == 1:
                single_periods.append(period)
            elif period['participant_count'] == len(all_users):
                full_periods.append(period)
            else:
                partial_periods.append(period)

        if single_periods:
            single_slots[day] = single_periods
        if partial_periods:
            partial_slots[day] = partial_periods
        if full_periods:
            full_slots[day] = full_periods

    return jsonify({
        'meeting_slots': meeting_slots,  # All meeting slots (now includes 1-person slots)
        'single_availability': single_slots,  # 1 person only (NEW - includes ken's 08:30!)
        'partial_availability': partial_slots,  # 2+ people but not all
        'full_availability': full_slots,  # All people available
        'total_users': len(all_users),
        'users_with_availability': len([u for u in user_availability.values() if u['days']]),
        'analysis_summary': {
            'days_with_meetings': len(meeting_slots),
            'total_meeting_slots': sum(len(slots) for slots in meeting_slots.values()),
            'single_meeting_days': len(single_slots),
            'single_meeting_slots': sum(len(slots) for slots in single_slots.values()),
            'partial_meeting_days': len(partial_slots),
            'partial_meeting_slots': sum(len(slots) for slots in partial_slots.values()),
            'full_meeting_days': len(full_slots),
            'full_meeting_slots': sum(len(slots) for slots in full_slots.values())
        }
    })

# Serve frontend
@app.route('/')
def serve_frontend():
    return send_from_directory('../frontend', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)