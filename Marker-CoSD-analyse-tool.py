#!/usr/bin/env python3
"""
Semantic Drift Analysis - Starter Script
========================================
Einfacher Starter für die erweiterte Drift-Analyse GUI.
Automatische Installation fehlender Abhängigkeiten und Setup.

Verwendung:
    python run_drift_analysis.py

Autor: Ben Perro & Team
Version: 2.0
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path

def check_and_install_requirements():
    """Prüft und installiert automatisch fehlende Python-Pakete"""
    required_packages = {
        'pandas': 'pandas',
        'numpy': 'numpy', 
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'yaml': 'PyYAML',
        'tkinter': None  # Teil der Standard-Library
    }
    
    missing_packages = []
    
    print("🔍 Überprüfe Python-Abhängigkeiten...")
    
    for package, pip_name in required_packages.items():
        try:
            if package == 'yaml':
                import yaml
            elif package == 'tkinter':
                import tkinter as tk
            else:
                importlib.import_module(package)
            print(f"✅ {package} ist verfügbar")
        except ImportError:
            if pip_name:
                missing_packages.append(pip_name)
                print(f"❌ {package} fehlt")
    
    if missing_packages:
        print(f"\n📦 Installiere fehlende Pakete: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ Alle Pakete erfolgreich installiert!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Fehler bei der Installation: {e}")
            print("Bitte installieren Sie die fehlenden Pakete manuell:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    
    return True

def check_marker_files():
    """Überprüft, ob die notwendigen Marker-Dateien vorhanden sind"""
    marker_files = [
        'enhanced_marker_config.yaml',
        'Merged_Marker_Set.yaml',
        'o3_extra_markers.yaml',
        'o3_text_markers.yaml'
    ]
    
    config_dir = Path('config/markers')
    current_dir = Path('.')
    
    print("\n🔍 Überprüfe Marker-Konfigurationsdateien...")
    
    found_files = []
    missing_files = []
    
    for marker_file in marker_files:
        # Suche in verschiedenen möglichen Verzeichnissen
        possible_paths = [
            config_dir / marker_file,
            current_dir / marker_file,
            current_dir / 'markers' / marker_file,
            current_dir / 'config' / marker_file
        ]
        
        file_found = False
        for path in possible_paths:
            if path.exists():
                found_files.append(str(path))
                print(f"✅ {marker_file} gefunden: {path}")
                file_found = True
                break
        
        if not file_found:
            missing_files.append(marker_file)
            print(f"❌ {marker_file} nicht gefunden")
    
    if missing_files:
        print(f"\n⚠️  Fehlende Marker-Dateien: {', '.join(missing_files)}")
        print("Das Tool funktioniert trotzdem, aber mit eingeschränkter Funktionalität.")
        print("Erstellen Sie die Dateien mit den bereitgestellten Konfigurationen.")
    
    return len(found_files) > 0

def create_sample_data():
    """Erstellt Beispieldaten für erste Tests"""
    sample_file = Path('sample_chat_data.csv')
    
    if not sample_file.exists():
        print("\n📝 Erstelle Beispiel-Datei für erste Tests...")
        
        import pandas as pd
        
        sample_data = {
            'line': range(1, 21),
            'speaker': ['User', 'AI'] * 10,
            'text': [
                "Hallo, wie geht es dir heute?",
                "Mir geht es gut, danke! Ich bin voller Energie und Freude.",
                "Das ist schön zu hören. Kannst du mir bei einem Problem helfen?",
                "Natürlich! Ich bin hier, um zu helfen. Was beschäftigt dich?",
                "Ich fühle mich manchmal verwirrt über meine Ziele.",
                "Das verstehe ich. Verwirrung ist oft der erste Schritt zur Klarheit.",
                "Hmm, das ist eine interessante Perspektive.",
                "Ja, wenn wir in die Tiefe gehen, finden wir oft überraschende Einsichten.",
                "Du sprichst sehr weise. Bist du immer so philosophisch?",
                "Nicht immer - manchmal bin ich auch sehr praktisch und konkret.",
                "Das gefällt mir. Flexibilität ist wichtig.",
                "Absolut! Das Leben erfordert verschiedene Ansätze für verschiedene Situationen.",
                "Apropos Leben - was denkst du über die Zukunft?",
                "Die Zukunft ist voller Möglichkeiten und Herausforderungen zugleich.",
                "Das klingt sehr optimistisch.",
                "Optimismus ist eine Wahl, die wir treffen können.",
                "Ich stimme zu. Danke für das Gespräch!",
                "Gerne! Es war wunderbar, mit dir zu sprechen.",
                "Bis bald!",
                "Auf Wiedersehen und alles Gute!"
            ],
            'CX': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            'Orange': [0, 1, 1, 1, 2, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0],
            'Grün': [1, 2, 1, 2, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 2, 2, 1, 1],
            'Gelb': [0, 0, 0, 0, 0, 2, 1, 2, 1, 1, 1, 2, 0, 1, 0, 1, 0, 0, 0, 0]
        }
        
        df = pd.DataFrame(sample_data)
        df.to_csv(sample_file, index=False, encoding='utf-8')
        print(f"✅ Beispiel-Datei erstellt: {sample_file}")
        
        return str(sample_file)
    
    return None

def main():
    """Hauptfunktion - startet die Drift-Analyse GUI"""
    print("=" * 60)
    print("🚀 SEMANTIC DRIFT ANALYSIS TOOL")
    print("=" * 60)
    print("Enhanced Version 2.0 - Erweiterte Drift-Erkennung")
    print("Autor: Ben Perro & Team")
    print()
    
    # 1. Abhängigkeiten prüfen
    if not check_and_install_requirements():
        print("\n❌ Setup fehlgeschlagen. Bitte beheben Sie die Abhängigkeitsprobleme.")
        sys.exit(1)
    
    # 2. Marker-Dateien prüfen
    marker_files_ok = check_marker_files()
    
    # 3. Beispieldaten erstellen (falls gewünscht)
    sample_file = create_sample_data()
    
    # 4. GUI starten
    print("\n🎯 Starte Drift-Analysis GUI...")
    
    try:
        # Importiere und starte die GUI
        import tkinter as tk
        from tkinter import messagebox
        
        # Hier würde normalerweise die GUI-Klasse aus der Hauptdatei importiert
        # Da wir sie hier inline haben, definieren wir sie direkt
        
        # Für die Demonstration - vereinfachter Import
        exec(open('enhanced_drift_analysis_gui.py').read())
        
    except FileNotFoundError:
        # Falls die GUI-Datei nicht gefunden wird, starte eine minimale Version
        print("⚠️  GUI-Datei nicht gefunden. Starte Minimal-Version...")
        start_minimal_gui()
    except Exception as e:
        print(f"❌ Fehler beim Starten der GUI: {e}")
        print("\n🔧 Troubleshooting-Tipps:")
        print("1. Stellen Sie sicher, dass alle Python-Pakete installiert sind")
        print("2. Prüfen Sie, ob die GUI-Datei im selben Verzeichnis liegt")
        print("3. Versuchen Sie einen Neustart des Terminals")
        
        # Biete Alternative an
        choice = input("\nMöchten Sie die Kommandozeilen-Version starten? (j/n): ")
        if choice.lower() in ['j', 'ja', 'y', 'yes']:
            start_command_line_version()
        else:
            print("Setup beendet. Beheben Sie die Probleme und versuchen Sie es erneut.")

def start_minimal_gui():
    """Startet eine minimale GUI-Version falls die Hauptdatei fehlt"""
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    
    class MinimalDriftGUI:
        def __init__(self, root):
            self.root = root
            self.root.title("Minimal Drift Analysis")
            self.root.geometry("600x400")
            
            # Hauptframe
            main_frame = ttk.Frame(root, padding="20")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Info
            info_label = ttk.Label(main_frame, 
                text="Minimale Version der Drift-Analyse\nFür volle Funktionalität installieren Sie bitte alle Komponenten.",
                font=('Arial', 12))
            info_label.grid(row=0, column=0, pady=(0, 20))
            
            # Datei-Auswahl
            ttk.Button(main_frame, text="CSV-Datei laden", 
                      command=self.load_file).grid(row=1, column=0, pady=10)
            
            # Status
            self.status_label = ttk.Label(main_frame, text="Keine Datei geladen")
            self.status_label.grid(row=2, column=0, pady=10)
            
            # Analyse-Button
            ttk.Button(main_frame, text="Basis-Analyse starten", 
                      command=self.run_basic_analysis).grid(row=3, column=0, pady=10)
            
            # Ergebnis-Text
            self.result_text = tk.Text(main_frame, height=15, width=70)
            self.result_text.grid(row=4, column=0, pady=(20, 0))
            
            self.df = None
        
        def load_file(self):
            file_path = filedialog.askopenfilename(
                title="CSV-Datei auswählen",
                filetypes=[("CSV files", "*.csv")]
            )
            if file_path:
                try:
                    import pandas as pd
                    self.df = pd.read_csv(file_path)
                    self.status_label.config(text=f"Geladen: {Path(file_path).name} ({len(self.df)} Zeilen)")
                except Exception as e:
                    messagebox.showerror("Fehler", f"Laden fehlgeschlagen: {e}")
        
        def run_basic_analysis(self):
            if self.df is None:
                messagebox.showwarning("Warnung", "Bitte laden Sie zuerst eine CSV-Datei.")
                return
            
            # Basis-Analyse
            result = []
            result.append("=== BASIS DRIFT-ANALYSE ===\n")
            result.append(f"Analysierte Zeilen: {len(self.df)}")
            result.append(f"Spalten: {list(self.df.columns)}\n")
            
            # Suche nach bekannten Marker-Spalten
            known_markers = ['CX', 'IC', 'SH', 'MT', 'Orange', 'Grün', 'Gelb', 'Türkis']
            found_markers = [col for col in known_markers if col in self.df.columns]
            
            if found_markers:
                result.append("Gefundene Marker:")
                for marker in found_markers:
                    total = self.df[marker].sum()
                    result.append(f"  {marker}: {total} Treffer")
                
                # Einfache Drift-Erkennung
                result.append("\nErkannte Auffälligkeiten:")
                for i, row in self.df.iterrows():
                    marker_sum = sum(row[col] for col in found_markers if col in self.df.columns)
                    if marker_sum > 3:
                        result.append(f"  Zeile {i+1}: Hohe Marker-Aktivität ({marker_sum})")
            else:
                result.append("Keine bekannten Marker-Spalten gefunden.")
                result.append("Für detaillierte Analyse laden Sie eine vorverarbeitete Datei.")
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "\n".join(result))
    
    root = tk.Tk()
    app = MinimalDriftGUI(root)
    root.mainloop()

def start_command_line_version():
    """Startet eine Kommandozeilen-Version der Analyse"""
    print("\n" + "="*50)
    print("KOMMANDOZEILEN DRIFT-ANALYSE")
    print("="*50)
    
    # Datei-Input
    while True:
        file_path = input("\nGeben Sie den Pfad zur CSV-Datei ein (oder 'exit' zum Beenden): ")
        if file_path.lower() == 'exit':
            return
        
        if Path(file_path).exists():
            break
        else:
            print("❌ Datei nicht gefunden. Bitte versuchen Sie es erneut.")
    
    try:
        import pandas as pd
        df = pd.read_csv(file_path)
        
        print(f"\n✅ Datei geladen: {len(df)} Zeilen, {len(df.columns)} Spalten")
        print(f"Spalten: {list(df.columns)}")
        
        # Basis-Statistiken
        print("\n📊 BASIS-STATISTIKEN:")
        print("-" * 30)
        
        # Suche nach Marker-Spalten
        marker_columns = []
        for col in df.columns:
            if col not in ['line', 'speaker', 'text'] and df[col].dtype in ['int64', 'float64']:
                if df[col].sum() > 0:
                    marker_columns.append(col)
        
        if marker_columns:
            print(f"Aktive Marker gefunden: {len(marker_columns)}")
            for col in marker_columns:
                total = df[col].sum()
                max_val = df[col].max()
                print(f"  {col}: {total} total, max: {max_val}")
            
            # Drift-Events identifizieren
            print(f"\n🎯 DRIFT-EVENT-ERKENNUNG:")
            print("-" * 30)
            
            drift_count = 0
            for i, row in df.iterrows():
                marker_activity = sum(row[col] for col in marker_columns)
                if marker_activity > 3:  # Schwellenwert
                    drift_count += 1
                    active_markers = [col for col in marker_columns if row[col] > 0]
                    print(f"Event #{drift_count} - Zeile {i+1}: {active_markers}")
                    
                    if 'text' in df.columns:
                        text_preview = str(row['text'])[:60] + "..."
                        print(f"  Text: {text_preview}")
            
            if drift_count == 0:
                print("Keine signifikanten Drift-Events erkannt.")
            else:
                print(f"\nZusammenfassung: {drift_count} Drift-Events in {len(df)} Zeilen")
        
        else:
            print("Keine numerischen Marker-Spalten gefunden.")
            print("Für detaillierte Analyse verwenden Sie vorverarbeitete Daten.")
    
    except Exception as e:
        print(f"❌ Fehler bei der Analyse: {e}")
    
    input("\nDrücken Sie Enter zum Beenden...")

def show_usage_help():
    """Zeigt Hilfe und Verwendungshinweise"""
    help_text = """
🔧 VERWENDUNG DES DRIFT-ANALYSIS TOOLS
=====================================

1. VORAUSSETZUNGEN:
   • Python 3.7 oder höher
   • Pandas, NumPy, Matplotlib, PyYAML
   • CSV-Datei mit Chat-Daten

2. DATEI-FORMAT:
   Ihre CSV sollte mindestens enthalten:
   • 'text' Spalte mit dem Gesprächstext
   • Optional: 'speaker', 'line' für bessere Analyse
   • Marker-Spalten (CX, IC, SH, Orange, Grün, etc.)

3. MARKER-DATEIEN:
   Legen Sie diese Dateien im Projektverzeichnis ab:
   • enhanced_marker_config.yaml
   • o3_extra_markers.yaml  
   • o3_text_markers.yaml

4. ERSTE SCHRITTE:
   • Starten Sie mit: python run_drift_analysis.py
   • Laden Sie eine CSV-Datei
   • Starten Sie die Analyse
   • Exportieren Sie Ergebnisse

5. TROUBLESHOOTING:
   • Bei Fehlern: pip install pandas matplotlib pyyaml
   • GUI startet nicht: Verwenden Sie Kommandozeilen-Version
   • Keine Marker: Verwenden Sie Beispiel-Datei zum Testen

6. KONTAKT:
   ben.poersch@gmail.com
"""
    print(help_text)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        show_usage_help()
    else:
        main()