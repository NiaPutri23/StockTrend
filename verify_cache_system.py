#!/usr/bin/env python3
"""
Verification script for StockTrend Dashboard cache system
Run this to verify all components are installed and working
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version (3.11+ required)"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print(f"  ✅ Python {version.major}.{version.minor} (OK)")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor} (Need 3.11+)")
        return False

def check_packages():
    """Check required packages"""
    print("\n🔍 Checking packages...")
    
    packages = {
        'streamlit': '1.28.0',
        'pandas': '2.0.0',
        'numpy': '1.24.0',
        'yfinance': '0.2.32',
        'plotly': '5.0.0',
        'schedule': '1.2.0',
    }
    
    all_ok = True
    for package, min_version in packages.items():
        try:
            mod = __import__(package)
            version = getattr(mod, '__version__', 'unknown')
            print(f"  ✅ {package:<15} {version}")
        except ImportError:
            print(f"  ❌ {package:<15} NOT INSTALLED")
            all_ok = False
    
    return all_ok

def check_project_structure():
    """Check project directory structure"""
    print("\n🔍 Checking project structure...")
    
    required_dirs = [
        'src',
        'data',
    ]
    
    required_files = [
        'app.py',
        'requirements.txt',
        'src/cache_manager.py',
        'src/scheduler.py',
        'src/cache_ui.py',
        'src/data.py',
        'src/screener.py',
        'src/utils.py',
        'src/__init__.py',
    ]
    
    base_path = Path(__file__).parent
    
    all_ok = True
    
    # Check directories
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        if dir_path.exists():
            print(f"  ✅ Directory: {dir_name}/")
        else:
            print(f"  ❌ Directory: {dir_name}/ (NOT FOUND)")
            all_ok = False
    
    # Check files
    for file_name in required_files:
        file_path = base_path / file_name
        if file_path.exists():
            size_kb = file_path.stat().st_size / 1024
            print(f"  ✅ File: {file_name:<30} ({size_kb:.1f} KB)")
        else:
            print(f"  ❌ File: {file_name:<30} (NOT FOUND)")
            all_ok = False
    
    return all_ok

def check_imports():
    """Check if modules can be imported"""
    print("\n🔍 Checking module imports...")
    
    sys.path.insert(0, str(Path(__file__).parent))
    
    modules_to_check = [
        ('src.cache_manager', 'Cache Manager'),
        ('src.scheduler', 'Scheduler'),
        ('src.cache_ui', 'Cache UI'),
        ('src.data', 'Data Module'),
        ('src.screener', 'Screener Module'),
        ('src.utils', 'Utils Module'),
    ]
    
    all_ok = True
    for module_name, display_name in modules_to_check:
        try:
            __import__(module_name)
            print(f"  ✅ {display_name:<20} ({module_name})")
        except ImportError as e:
            print(f"  ❌ {display_name:<20} (Error: {str(e)[:40]}...)")
            all_ok = False
        except Exception as e:
            print(f"  ⚠️ {display_name:<20} (Warning: {str(e)[:40]}...)")
            # Continue anyway - might be just missing schedule package
    
    return all_ok

def check_database():
    """Check if cache database can be created"""
    print("\n🔍 Checking database functionality...")
    
    try:
        from src.cache_manager import get_cache_manager
        
        cache = get_cache_manager()
        print(f"  ✅ Cache manager initialized")
        
        # Check if database file exists or can be created
        db_path = cache.db_path
        print(f"  ✅ Database path: {db_path}")
        
        # Try to get status
        try:
            status = cache.get_cache_status()
            print(f"  ✅ Database accessible")
            print(f"    - Tickers cached: {status['tickers_cached']}")
            print(f"    - Total records: {status['total_records']}")
            print(f"    - Database size: {status['db_size_mb']} MB")
        except Exception as e:
            print(f"  ⚠️ Database status check failed: {str(e)}")
        
        return True
    except Exception as e:
        print(f"  ❌ Cache manager error: {str(e)}")
        return False

def check_scheduler():
    """Check if scheduler can be initialized"""
    print("\n🔍 Checking scheduler functionality...")
    
    try:
        from src.scheduler import get_scheduler
        
        scheduler = get_scheduler()
        print(f"  ✅ Scheduler initialized")
        print(f"  ✅ Scheduler status: {'🟢 Running' if scheduler.is_running else '🔴 Stopped'}")
        
        # Check if BEI stocks are loaded
        from src.scheduler import ALL_BEI_TICKERS
        print(f"  ✅ BEI stocks loaded: {len(ALL_BEI_TICKERS)} tickers")
        
        return True
    except Exception as e:
        print(f"  ❌ Scheduler error: {str(e)}")
        return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("📊 StockTrend Dashboard - Cache System Verification")
    print("=" * 60)
    
    results = {
        'Python Version': check_python_version(),
        'Project Structure': check_project_structure(),
        'Packages': check_packages(),
        'Module Imports': check_imports(),
        'Database': check_database(),
        'Scheduler': check_scheduler(),
    }
    
    print("\n" + "=" * 60)
    print("📋 Verification Summary")
    print("=" * 60)
    
    all_ok = True
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:<25} {status}")
        if not result:
            all_ok = False
    
    print("=" * 60)
    
    if all_ok:
        print("\n🎉 All checks passed! Ready to use cache system.\n")
        print("Next steps:")
        print("1. Run: streamlit run app.py")
        print("2. Go to Cache Management page")
        print("3. Cache a sector to test")
        print("4. Use Dashboard to see speed improvement!")
        return 0
    else:
        print("\n⚠️ Some checks failed. See details above.\n")
        print("Common fixes:")
        print("1. Install missing packages: pip install schedule")
        print("2. Create data/ directory: mkdir data")
        print("3. Restart Python: Close all terminals and restart")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
