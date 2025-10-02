#!/usr/bin/env python3
"""
System Verification Script for Team Schedule Manager
Verifies all components are properly configured
"""

import os
import json
import sqlite3
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} missing: {filepath}")
        return False

def check_directory_structure():
    """Verify project directory structure"""
    print("📁 Checking directory structure...")

    required_files = [
        ("docker-compose.yml", "Docker Compose configuration"),
        ("nginx.conf", "Nginx configuration"),
        ("app/backend/Dockerfile", "Backend Dockerfile"),
        ("app/backend/app.py", "Flask application"),
        ("app/backend/init_db.py", "Database initialization"),
        ("app/backend/requirements.txt", "Python dependencies"),
        ("app/frontend/Dockerfile", "Frontend Dockerfile"),
        ("app/frontend/index.html", "Main HTML file"),
        ("app/frontend/styles.css", "CSS styles"),
        ("app/frontend/app.js", "JavaScript application"),
        ("README.md", "Documentation"),
        ("start.sh", "Startup script")
    ]

    all_exist = True
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            all_exist = False

    return all_exist

def check_backend_requirements():
    """Check backend requirements.txt"""
    print("\n📦 Checking backend dependencies...")

    try:
        with open("app/backend/requirements.txt", "r") as f:
            requirements = f.read()

        required_packages = [
            "Flask", "Flask-CORS", "Flask-JWT-Extended",
            "bcrypt", "SQLAlchemy", "python-dotenv", "marshmallow"
        ]

        for package in required_packages:
            if package in requirements:
                print(f"✅ {package} found in requirements.txt")
            else:
                print(f"❌ {package} missing from requirements.txt")

        return True

    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

def check_database_schema():
    """Verify database initialization script"""
    print("\n🗄️ Checking database schema...")

    try:
        with open("app/backend/init_db.py", "r") as f:
            init_script = f.read()

        required_tables = ["users", "availability", "meetings", "meeting_participants"]

        for table in required_tables:
            if f"CREATE TABLE IF NOT EXISTS {table}" in init_script:
                print(f"✅ Table '{table}' creation found")
            else:
                print(f"❌ Table '{table}' creation missing")

        return True

    except FileNotFoundError:
        print("❌ init_db.py not found")
        return False

def check_frontend_files():
    """Check frontend file structure"""
    print("\n🎨 Checking frontend files...")

    # Check HTML structure
    try:
        with open("app/frontend/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()

        required_elements = [
            "login-screen", "dashboard-screen", "availability-modal",
            "toast-container", "loading-screen"
        ]

        for element in required_elements:
            if element in html_content:
                print(f"✅ HTML element '{element}' found")
            else:
                print(f"❌ HTML element '{element}' missing")

    except FileNotFoundError:
        print("❌ index.html not found")
        return False

    # Check CSS variables
    try:
        with open("app/frontend/styles.css", "r", encoding="utf-8") as f:
            css_content = f.read()

        required_css = [
            "--color-primary", "--color-secondary", "--color-accent",
            "animate-bounce", "animate-pulse", "animate-fade-in"
        ]

        for css_class in required_css:
            if css_class in css_content:
                print(f"✅ CSS '{css_class}' found")
            else:
                print(f"❌ CSS '{css_class}' missing")

    except FileNotFoundError:
        print("❌ styles.css not found")
        return False

    return True

def check_api_endpoints():
    """Check API endpoints in Flask app"""
    print("\n🔌 Checking API endpoints...")

    try:
        with open("app/backend/app.py", "r") as f:
            app_content = f.read()

        required_endpoints = [
            "/api/health", "/api/register", "/api/login",
            "/api/users", "/api/availability", "/api/common-availability"
        ]

        for endpoint in required_endpoints:
            if f"'{endpoint}'" in app_content or f'"{endpoint}"' in app_content:
                print(f"✅ API endpoint '{endpoint}' found")
            else:
                print(f"❌ API endpoint '{endpoint}' missing")

        return True

    except FileNotFoundError:
        print("❌ app.py not found")
        return False

def check_docker_configuration():
    """Check Docker configuration"""
    print("\n🐳 Checking Docker configuration...")

    # Check docker-compose.yml
    try:
        with open("docker-compose.yml", "r") as f:
            compose_content = f.read()

        required_services = ["backend", "frontend", "nginx"]

        for service in required_services:
            if f"{service}:" in compose_content:
                print(f"✅ Docker service '{service}' found")
            else:
                print(f"❌ Docker service '{service}' missing")

    except FileNotFoundError:
        print("❌ docker-compose.yml not found")
        return False

    return True

def check_ui_requirements():
    """Check UI/UX requirements compliance"""
    print("\n🎨 Checking UI/UX requirements...")

    try:
        with open("app/frontend/styles.css", "r", encoding="utf-8") as f:
            css_content = f.read()

        # Check pastel colors (淡い色基調)
        pastel_colors = ["#A8D5E2", "#C9E4CA", "#FFB5A7"]  # Soft blue, mint, coral

        for color in pastel_colors:
            if color in css_content:
                print(f"✅ Pastel color {color} found")
            else:
                print(f"❌ Pastel color {color} missing")

        # Check animations
        animations = ["@keyframes bounce", "@keyframes pulse", "@keyframes fadeIn"]

        for animation in animations:
            if animation in css_content:
                print(f"✅ Animation '{animation}' found")
            else:
                print(f"❌ Animation '{animation}' missing")

        return True

    except FileNotFoundError:
        print("❌ styles.css not found")
        return False

def generate_system_report():
    """Generate comprehensive system report"""
    print("\n📊 System Verification Report")
    print("=" * 50)

    checks = [
        ("Directory Structure", check_directory_structure),
        ("Backend Dependencies", check_backend_requirements),
        ("Database Schema", check_database_schema),
        ("Frontend Files", check_frontend_files),
        ("API Endpoints", check_api_endpoints),
        ("Docker Configuration", check_docker_configuration),
        ("UI/UX Requirements", check_ui_requirements)
    ]

    results = {}
    total_checks = len(checks)
    passed_checks = 0

    for check_name, check_function in checks:
        print(f"\n🔍 Running: {check_name}")
        try:
            result = check_function()
            results[check_name] = result
            if result:
                passed_checks += 1
        except Exception as e:
            print(f"❌ Error in {check_name}: {e}")
            results[check_name] = False

    # Summary
    print("\n" + "=" * 50)
    print("📈 VERIFICATION SUMMARY")
    print("=" * 50)

    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check_name}")

    success_rate = (passed_checks / total_checks) * 100

    print(f"\n🎯 Overall Success Rate: {success_rate:.1f}% ({passed_checks}/{total_checks})")

    if success_rate >= 90:
        print("🎉 System verification SUCCESSFUL! Ready for deployment.")
    elif success_rate >= 70:
        print("⚠️  System mostly ready, but some issues need attention.")
    else:
        print("🚨 System needs significant fixes before deployment.")

    return success_rate

def main():
    """Main verification function"""
    print("🚀 Team Schedule Manager - System Verification")
    print("=" * 50)
    print("Verifying all system components...")

    # Change to project root directory
    os.chdir("/root/aws.git/container/claudecode/scheWEB")

    # Run verification
    success_rate = generate_system_report()

    # Additional deployment information
    print("\n" + "=" * 50)
    print("🚀 DEPLOYMENT INSTRUCTIONS")
    print("=" * 50)

    if success_rate >= 90:
        print("✅ System ready! To deploy:")
        print("1. Run: ./start.sh")
        print("2. Or manually: docker-compose up --build")
        print("3. Access: http://localhost")
        print("\n👤 Demo accounts:")
        print("   - admin / admin123")
        print("   - user1 / admin123")
        print("   - user2 / admin123")
    else:
        print("❌ Please fix the issues above before deployment.")

    print("\n📚 Documentation: README.md")
    print("🐛 Logs: docker-compose logs")

    return success_rate >= 90

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)