#!/usr/bin/env python3
"""
Script de surveillance pour le rechargement automatique pendant le développement
"""

import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class AppReloader(FileSystemEventHandler):
    """Gestionnaire d'événements pour le rechargement de l'application"""
    
    def __init__(self):
        self.process = None
        self.start_app()
    
    def start_app(self):
        """Démarrer l'application"""
        if self.process:
            self.process.terminate()
            self.process.wait()
        
        print("\n🚀 Démarrage de l'application...")
        self.process = subprocess.Popen([sys.executable, "gui.py"])
    
    def on_modified(self, event):
        """Gérer les modifications de fichiers"""
        if event.src_path.endswith('.py'):
            print(f"\n📝 Modification détectée: {event.src_path}")
            self.start_app()

def main():
    """Point d'entrée principal"""
    print("👀 Surveillance des modifications de fichiers activée")
    print("Appuyez sur Ctrl+C pour arrêter")
    
    event_handler = AppReloader()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    
    observer.join()

if __name__ == "__main__":
    main() 