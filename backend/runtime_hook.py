import sys
import os

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

os.environ['APP_PATH'] = application_path

if getattr(sys, 'frozen', False):
    skills_dir = os.path.join(application_path, 'skills')
    subagents_dir = os.path.join(application_path, 'subagents')
    
    if os.path.exists(skills_dir):
        os.environ['SKILLS_DIR'] = skills_dir
    if os.path.exists(subagents_dir):
        os.environ['SUBAGENTS_DIR'] = subagents_dir
