#!/usr/bin/env python3
"""
Script pour démarrer le service RO-Service
"""

import subprocess
import sys
import os

def start_ro_service():
    """Démarre le service RO-Service"""
    try:
        # Changer vers le répertoire RO-Service
        os.chdir('RO-Service')
        
        print("🚀 Démarrage du service RO-Service...")
        print("📍 URL: http://localhost:4321")
        print("📋 Endpoints disponibles:")
        print("   - GET  /test")
        print("   - POST /calculate")
        print("\n⏹️  Pour arrêter le service, appuyez sur Ctrl+C")
        print("-" * 50)
        
        # Démarrer le service
        subprocess.run([sys.executable, 'run.py'])
        
    except KeyboardInterrupt:
        print("\n🛑 Service arrêté par l'utilisateur")
    except FileNotFoundError:
        print("❌ Erreur: Le répertoire RO-Service n'existe pas")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")

if __name__ == "__main__":
    start_ro_service() 