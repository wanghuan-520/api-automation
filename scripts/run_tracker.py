import sys
import time
from pathlib import Path
from utils.project_tracker import ProjectTracker

def main():
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    
    # 创建追踪器实例
    tracker = ProjectTracker(str(project_root))
    
    try:
        # 开始监控
        tracker.start_monitoring()
        print(f"Project tracker started. Monitoring {project_root}")
        print("Press Ctrl+C to stop...")
        
        # 保持程序运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping project tracker...")
        tracker.stop_monitoring()
        
        # 生成并保存报告
        tracker.save_report()
        print("Report generated and saved to reports/project_status.yaml")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        tracker.stop_monitoring()
        sys.exit(1)

if __name__ == "__main__":
    main() 