#!/usr/bin/env python3
"""
Enhanced Semantic Drift Analysis GUI
===================================
Erweiterte Version mit detaillierten Drift-Beschreibungen und verbesserter Visualisierung.
Analysiert Chat-Logs auf semantische Drift-Events mit präzisen, verständlichen Erklärungen.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yaml
import json
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Styling für bessere Lesbarkeit
plt.rcParams.update({
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'figure.titlesize': 16
})

class EnhancedDriftAnalyzer:
    def __init__(self):
        self.marker_descriptions = {
            # Emotion & Valenz Marker
            'CX': 'Widersprüche & Logikbrüche',
            'IC': 'Unausgesprochene Vorannahmen',
            'SH': 'Abrupte Themenwechsel',
            'MT': 'Meta-Kommunikation über den Dialog',
            'EM_UP': 'Emotionale Intensivierung',
            'EM_DOWN': 'Emotionale Beruhigung',
            'RM': 'Selbstkorrektur & Klarstellung',
            'SI': 'Plötzliche Selbsterkenntnis',
            
            # Spiral Dynamics Beschreibungen
            'Beige': 'Grundbedürfnisse & Survival',
            'Purpur': 'Stammeszugehörigkeit & Rituale',
            'Rot': 'Ego-Durchsetzung & Dominanz',
            'Blau': 'Ordnung & traditionelle Strukturen',
            'Orange': 'Zielerreichung & Leistung',
            'Grün': 'Gemeinschaft & Empathie',
            'Gelb': 'Systemisches Denken & Flexibilität',
            'Türkis': 'Holistische Verbundenheit',
            
            # Archetypen
            'Pippi_Langstrumpf': 'Kindliche Kreativität & Regellosigkeit',
            'Tyler_Durden': 'Destruktive Klarheit & Systemkritik',
            'Jean_Luc_Picard': 'Würdevolle Führung & Diplomatie',
            'Clarissa_Pinkola_Estes': 'Intuitive Weisheit & Mythenverständnis',
            
            # Meta-Semantik
            'self_ref': 'Selbstbezogene Aussagen',
            'meta_comm': 'Dialog über den Dialog',
            'intent': 'Explizite Absichtserklärungen',
            'recall': 'Bezug auf frühere Gespräche',
            'persona_switch': 'Rollenwechsel zwischen Archetypen'
        }
        
        self.spiral_dynamics_relationships = {
            'Beige→Purpur': 'Entwicklung von Überlebensmodus zu sozialer Bindung',
            'Purpur→Rot': 'Von Gruppenloyalität zu individueller Macht',
            'Rot→Blau': 'Von Chaos zu Ordnung und Struktur',
            'Blau→Orange': 'Von starren Regeln zu strategischem Denken',
            'Orange→Grün': 'Von Leistung zu zwischenmenschlicher Harmonie',
            'Grün→Gelb': 'Von emotionaler zu systemischer Betrachtung',
            'Gelb→Türkis': 'Von analytischem zu holistischem Bewusstsein'
        }
        
    def load_marker_data(self, file_path):
        """Lädt Marker-Daten aus YAML oder JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix == '.yaml' or file_path.suffix == '.yml':
                    return yaml.safe_load(f)
                else:
                    return json.load(f)
        except Exception as e:
            print(f"Fehler beim Laden der Marker-Datei: {e}")
            return {}
    
    def detect_drift_events(self, df):
        """Erweiterte Drift-Erkennung mit detaillierter Analyse"""
        drift_events = []
        
        # Emotional Spike Detection
        emotion_cols = [col for col in df.columns if any(emo in col.lower() for emo in ['freude', 'wut', 'angst', 'trauer'])]
        if emotion_cols:
            for i in range(1, len(df)):
                emotion_change = abs(df[emotion_cols].iloc[i].sum() - df[emotion_cols].iloc[i-1].sum())
                if emotion_change > 2:  # Schwellenwert für emotionalen Drift
                    drift_events.append({
                        'event_id': len(drift_events) + 1,
                        'line': i,
                        'type': 'Emotionaler Drift',
                        'intensity': emotion_change,
                        'details': self._analyze_emotional_drift(df, i, emotion_cols)
                    })
        
        # Spiral Dynamics Transitions
        sd_cols = ['Beige', 'Purpur', 'Rot', 'Blau', 'Orange', 'Grün', 'Gelb', 'Türkis']
        available_sd_cols = [col for col in sd_cols if col in df.columns]
        
        if available_sd_cols:
            for i in range(1, len(df)):
                prev_dominant = df[available_sd_cols].iloc[i-1].idxmax()
                curr_dominant = df[available_sd_cols].iloc[i].idxmax()
                
                if prev_dominant != curr_dominant and df[available_sd_cols].iloc[i][curr_dominant] > 1:
                    transition = f"{prev_dominant}→{curr_dominant}"
                    drift_events.append({
                        'event_id': len(drift_events) + 1,
                        'line': i,
                        'type': 'Spiral Dynamics Transition',
                        'transition': transition,
                        'details': self._analyze_sd_transition(df, i, prev_dominant, curr_dominant)
                    })
        
        # Meta-Kommunikations-Spikes
        meta_markers = ['CX', 'IC', 'SH', 'MT', 'RM', 'SI']
        available_meta = [col for col in meta_markers if col in df.columns]
        
        if available_meta:
            for i in range(len(df)):
                meta_activity = df[available_meta].iloc[i].sum()
                if meta_activity >= 3:  # Hohe Meta-Aktivität
                    drift_events.append({
                        'event_id': len(drift_events) + 1,
                        'line': i,
                        'type': 'Meta-Kommunikative Verdichtung',
                        'intensity': meta_activity,
                        'details': self._analyze_meta_spike(df, i, available_meta)
                    })
        
        return drift_events
    
    def _analyze_emotional_drift(self, df, line, emotion_cols):
        """Detaillierte Analyse eines emotionalen Drifts"""
        current_emotions = df[emotion_cols].iloc[line]
        prev_emotions = df[emotion_cols].iloc[line-1] if line > 0 else current_emotions
        
        dominant_current = current_emotions.idxmax()
        dominant_prev = prev_emotions.idxmax()
        
        intensity_change = current_emotions[dominant_current] - prev_emotions.get(dominant_current, 0)
        
        description = f"Emotionaler Übergang von '{self.marker_descriptions.get(dominant_prev, dominant_prev)}' zu '{self.marker_descriptions.get(dominant_current, dominant_current)}'"
        
        if intensity_change > 0:
            description += f" mit einer Intensivierung um {intensity_change:.1f} Punkte"
        else:
            description += f" mit einer Abschwächung um {abs(intensity_change):.1f} Punkte"
        
        return {
            'description': description,
            'dominant_emotion_before': dominant_prev,
            'dominant_emotion_after': dominant_current,
            'intensity_change': intensity_change,
            'text_excerpt': df.iloc[line].get('text', '')[:100] + "..."
        }
    
    def _analyze_sd_transition(self, df, line, prev_level, curr_level):
        """Detaillierte Analyse einer Spiral Dynamics Transition"""
        transition_key = f"{prev_level}→{curr_level}"
        transition_meaning = self.spiral_dynamics_relationships.get(
            transition_key, 
            f"Wertewandel von {self.marker_descriptions.get(prev_level, prev_level)} zu {self.marker_descriptions.get(curr_level, curr_level)}"
        )
        
        # Kontext-Analyse: Welche anderen Marker sind aktiv?
        active_markers = []
        for col in df.columns:
            if col not in ['line', 'speaker', 'text'] and df.iloc[line][col] > 0:
                marker_desc = self.marker_descriptions.get(col, col)
                active_markers.append(f"{marker_desc} ({df.iloc[line][col]})")
        
        return {
            'description': f"Werteebenen-Transition: {transition_meaning}",
            'previous_level': prev_level,
            'current_level': curr_level,
            'transition_meaning': transition_meaning,
            'concurrent_markers': active_markers,
            'text_excerpt': df.iloc[line].get('text', '')[:150] + "..."
        }
    
    def _analyze_meta_spike(self, df, line, meta_markers):
        """Detaillierte Analyse einer Meta-Kommunikations-Verdichtung"""
        active_meta = {}
        for marker in meta_markers:
            if df.iloc[line][marker] > 0:
                active_meta[marker] = df.iloc[line][marker]
        
        # Erstelle eine interpretative Beschreibung
        descriptions = [f"{self.marker_descriptions.get(marker, marker)} ({count}x)" 
                       for marker, count in active_meta.items()]
        
        description = f"Komplexe Meta-Kommunikation mit {len(active_meta)} gleichzeitigen Signalen: " + ", ".join(descriptions)
        
        return {
            'description': description,
            'active_markers': active_meta,
            'total_intensity': sum(active_meta.values()),
            'text_excerpt': df.iloc[line].get('text', '')[:150] + "..."
        }
    
    def generate_drift_report(self, df, drift_events):
        """Generiert einen detaillierten, lesbaren Drift-Report"""
        report = []
        report.append("=" * 80)
        report.append("DETAILLIERTER SEMANTISCHER DRIFT-ANALYSEBERICHT")
        report.append("=" * 80)
        report.append("")
        
        if not drift_events:
            report.append("Keine signifikanten Drift-Events erkannt.")
            return "\n".join(report)
        
        report.append(f"Anzahl erkannter Drift-Events: {len(drift_events)}")
        report.append(f"Analysierte Gesprächszeilen: {len(df)}")
        report.append("")
        
        for event in drift_events:
            report.append("-" * 60)
            report.append(f"DRIFT-EVENT #{event['event_id']}")
            report.append("-" * 60)
            report.append(f"Position: Zeile {event['line']}")
            report.append(f"Typ: {event['type']}")
            report.append("")
            
            if 'details' in event:
                details = event['details']
                report.append("BESCHREIBUNG:")
                report.append(f"  {details['description']}")
                report.append("")
                
                if 'text_excerpt' in details:
                    report.append("TEXTAUSSCHNITT:")
                    report.append(f"  \"{details['text_excerpt']}\"")
                    report.append("")
                
                # Spezifische Details je nach Event-Typ
                if event['type'] == 'Emotionaler Drift':
                    report.append("EMOTIONALE ANALYSE:")
                    report.append(f"  Vorherige Emotion: {details.get('dominant_emotion_before', 'N/A')}")
                    report.append(f"  Aktuelle Emotion: {details.get('dominant_emotion_after', 'N/A')}")
                    report.append(f"  Intensitätsänderung: {details.get('intensity_change', 0):.1f}")
                    
                elif event['type'] == 'Spiral Dynamics Transition':
                    report.append("WERTEEBENEN-ANALYSE:")
                    report.append(f"  Von: {details.get('previous_level', 'N/A')} ({self.marker_descriptions.get(details.get('previous_level', ''), 'N/A')})")
                    report.append(f"  Nach: {details.get('current_level', 'N/A')} ({self.marker_descriptions.get(details.get('current_level', ''), 'N/A')})")
                    report.append(f"  Bedeutung: {details.get('transition_meaning', 'N/A')}")
                    
                    if details.get('concurrent_markers'):
                        report.append("  Begleitende Marker:")
                        for marker in details['concurrent_markers'][:5]:  # Zeige max. 5
                            report.append(f"    - {marker}")
                
                elif event['type'] == 'Meta-Kommunikative Verdichtung':
                    report.append("META-ANALYSE:")
                    report.append(f"  Gesamtintensität: {details.get('total_intensity', 0)}")
                    if details.get('active_markers'):
                        report.append("  Aktive Meta-Marker:")
                        for marker, count in details['active_markers'].items():
                            report.append(f"    - {self.marker_descriptions.get(marker, marker)}: {count}x")
            
            report.append("")
        
        # Zusammenfassung
        report.append("=" * 60)
        report.append("ZUSAMMENFASSUNG")
        report.append("=" * 60)
        
        event_types = {}
        for event in drift_events:
            event_type = event['type']
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        report.append("Verteilung der Drift-Typen:")
        for event_type, count in event_types.items():
            report.append(f"  - {event_type}: {count}x")
        
        return "\n".join(report)

class DriftAnalysisGUI:
    def __init__(self, root):
        self.root = root
        self.analyzer = EnhancedDriftAnalyzer()
        self.df = None
        self.drift_events = []
        
        self.setup_gui()
    
    def setup_gui(self):
        self.root.title("Enhanced Semantic Drift Analysis Tool")
        self.root.geometry("1200x800")
        
        # Hauptframe
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Datei-Auswahl
        file_frame = ttk.LabelFrame(main_frame, text="Datei-Auswahl", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(file_frame, text="CSV-Datei laden", command=self.load_csv).grid(row=0, column=0, padx=(0, 10))
        self.file_label = ttk.Label(file_frame, text="Keine Datei geladen")
        self.file_label.grid(row=0, column=1)
        
        # Analyse-Optionen
        options_frame = ttk.LabelFrame(main_frame, text="Analyse-Optionen", padding="10")
        options_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(options_frame, text="Drift-Analyse starten", command=self.run_analysis).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(options_frame, text="Detaillierte Visualisierung", command=self.create_detailed_plots).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(options_frame, text="Report exportieren", command=self.export_report).grid(row=0, column=2)
        
        # Ergebnisse-Notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Tab 1: Drift-Events Übersicht
        self.events_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.events_frame, text="Drift-Events Übersicht")
        
        # Tab 2: Detaillierter Report
        self.report_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.report_frame, text="Detaillierter Report")
        
        # Tab 3: Visualisierungen
        self.viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.viz_frame, text="Visualisierungen")
        
        # Responsive Design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
    
    def load_csv(self):
        file_path = filedialog.askopenfilename(
            title="CSV-Datei für Drift-Analyse auswählen",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                self.file_label.config(text=f"Geladen: {Path(file_path).name}")
                messagebox.showinfo("Erfolg", f"Datei erfolgreich geladen!\nZeilen: {len(self.df)}, Spalten: {len(self.df.columns)}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden der Datei:\n{str(e)}")
    
    def run_analysis(self):
        if self.df is None:
            messagebox.showwarning("Warnung", "Bitte laden Sie zuerst eine CSV-Datei.")
            return
        
        try:
            # Drift-Analyse durchführen
            self.drift_events = self.analyzer.detect_drift_events(self.df)
            
            # Events-Übersicht aktualisieren
            self.update_events_overview()
            
            # Report generieren
            report_text = self.analyzer.generate_drift_report(self.df, self.drift_events)
            self.update_report_tab(report_text)
            
            messagebox.showinfo("Analyse abgeschlossen", 
                               f"Drift-Analyse erfolgreich!\n{len(self.drift_events)} Events erkannt.")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Analyse:\n{str(e)}")
    
    def update_events_overview(self):
        # Lösche vorherige Inhalte
        for widget in self.events_frame.winfo_children():
            widget.destroy()
        
        if not self.drift_events:
            ttk.Label(self.events_frame, text="Keine Drift-Events erkannt.", 
                     font=('Arial', 12)).pack(pady=20)
            return
        
        # Scrollable Frame für Events
        canvas = tk.Canvas(self.events_frame)
        scrollbar = ttk.Scrollbar(self.events_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Events anzeigen
        for event in self.drift_events:
            event_frame = ttk.LabelFrame(scrollable_frame, text=f"Drift-Event #{event['event_id']}", padding="10")
            event_frame.pack(fill="x", padx=10, pady=5)
            
            # Event-Details
            details_text = f"Zeile: {event['line']} | Typ: {event['type']}"
            if 'intensity' in event:
                details_text += f" | Intensität: {event['intensity']:.1f}"
            
            ttk.Label(event_frame, text=details_text, font=('Arial', 11, 'bold')).pack(anchor="w")
            
            if 'details' in event and 'description' in event['details']:
                desc_label = ttk.Label(event_frame, text=event['details']['description'], 
                                     font=('Arial', 10), wraplength=800)
                desc_label.pack(anchor="w", pady=(5, 0))
            
            # Button für detaillierte Ansicht
            ttk.Button(event_frame, text="Detailansicht", 
                      command=lambda e=event: self.show_event_details(e)).pack(anchor="e", pady=(5, 0))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def update_report_tab(self, report_text):
        # Lösche vorherige Inhalte
        for widget in self.report_frame.winfo_children():
            widget.destroy()
        
        # Scrollbarer Textbereich
        text_widget = scrolledtext.ScrolledText(self.report_frame, wrap=tk.WORD, 
                                              font=('Courier', 11), padx=10, pady=10)
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, report_text)
        text_widget.config(state=tk.DISABLED)
    
    def show_event_details(self, event):
        """Zeigt detaillierte Event-Informationen in einem neuen Fenster"""
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Drift-Event #{event['event_id']} - Detailansicht")
        detail_window.geometry("800x600")
        
        # Scrollbarer Text
        text_widget = scrolledtext.ScrolledText(detail_window, wrap=tk.WORD, 
                                              font=('Arial', 11), padx=15, pady=15)
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Detaillierte Informationen zusammenstellen
        details_text = []
        details_text.append(f"DRIFT-EVENT #{event['event_id']}")
        details_text.append("=" * 50)
        details_text.append(f"Position: Zeile {event['line']}")
        details_text.append(f"Typ: {event['type']}")
        details_text.append("")
        
        if 'details' in event:
            details = event['details']
            details_text.append("BESCHREIBUNG:")
            details_text.append(details.get('description', 'Keine Beschreibung verfügbar'))
            details_text.append("")
            
            if 'text_excerpt' in details:
                details_text.append("TEXTAUSSCHNITT:")
                details_text.append(f'"{details["text_excerpt"]}"')
                details_text.append("")
            
            # Weitere spezifische Details hinzufügen
            for key, value in details.items():
                if key not in ['description', 'text_excerpt']:
                    details_text.append(f"{key.replace('_', ' ').title()}: {value}")
        
        text_widget.insert(tk.END, "\n".join(details_text))
        text_widget.config(state=tk.DISABLED)
    
    def create_detailed_plots(self):
        if self.df is None or not self.drift_events:
            messagebox.showwarning("Warnung", "Bitte führen Sie zuerst eine Analyse durch.")
            return
        
        # Lösche vorherige Plots
        for widget in self.viz_frame.winfo_children():
            widget.destroy()
        
        # Erstelle verschiedene Visualisierungen
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Detaillierte Drift-Analyse Visualisierung', fontsize=16, fontweight='bold')
        
        # Plot 1: Drift-Events über Zeit
        drift_lines = [event['line'] for event in self.drift_events]
        drift_types = [event['type'] for event in self.drift_events]
        
        ax1 = axes[0, 0]
        type_colors = {'Emotionaler Drift': 'red', 'Spiral Dynamics Transition': 'blue', 
                      'Meta-Kommunikative Verdichtung': 'green'}
        
        for drift_type in set(drift_types):
            type_lines = [line for line, dtype in zip(drift_lines, drift_types) if dtype == drift_type]
            ax1.scatter(type_lines, [drift_type] * len(type_lines), 
                       c=type_colors.get(drift_type, 'gray'), s=100, alpha=0.7)
        
        ax1.set_xlabel('Gesprächszeile')
        ax1.set_ylabel('Drift-Typ')
        ax1.set_title('Drift-Events über Gesprächsverlauf')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Emotional-Intensität über Zeit (falls vorhanden)
        emotion_cols = [col for col in self.df.columns if any(emo in col.lower() for emo in ['freude', 'wut', 'angst', 'trauer'])]
        if emotion_cols:
            ax2 = axes[0, 1]
            total_emotion = self.df[emotion_cols].sum(axis=1)
            ax2.plot(total_emotion.index, total_emotion.values, linewidth=2)
            ax2.set_xlabel('Gesprächszeile')
            ax2.set_ylabel('Emotionale Gesamtintensität')
            ax2.set_title('Emotionale Intensität im Verlauf')
            ax2.grid(True, alpha=0.3)
            
            # Markiere Drift-Events
            for event in self.drift_events:
                if event['type'] == 'Emotionaler Drift':
                    ax2.axvline(x=event['line'], color='red', linestyle='--', alpha=0.7)
        
        # Plot 3: Spiral Dynamics Verteilung
        sd_cols = ['Beige', 'Purpur', 'Rot', 'Blau', 'Orange', 'Grün', 'Gelb', 'Türkis']
        available_sd_cols = [col for col in sd_cols if col in self.df.columns]
        
        if available_sd_cols:
            ax3 = axes[1, 0]
            sd_totals = self.df[available_sd_cols].sum()
            colors = plt.cm.Set3(np.linspace(0, 1, len(available_sd_cols)))
            bars = ax3.bar(range(len(available_sd_cols)), sd_totals.values, color=colors)
            ax3.set_xticks(range(len(available_sd_cols)))
            ax3.set_xticklabels(available_sd_cols, rotation=45)
            ax3.set_ylabel('Gesamthäufigkeit')
            ax3.set_title('Spiral Dynamics Verteilung')
            
            # Beschriftung der Balken
            for bar, col in zip(bars, available_sd_cols):
                height = bar.get_height()
                if height > 0:
                    ax3.text(bar.get_x() + bar.get_width()/2., height,
                            f'{int(height)}', ha='center', va='bottom', fontsize=9)
        
        # Plot 4: Event-Typen Verteilung
        ax4 = axes[1, 1]
        event_counts = {}
        for event in self.drift_events:
            event_type = event['type']
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        if event_counts:
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
            wedges, texts, autotexts = ax4.pie(event_counts.values(), labels=event_counts.keys(), 
                                              autopct='%1.1f%%', startangle=90, colors=colors)
            ax4.set_title('Verteilung der Drift-Event-Typen')
            
            # Verbessere Lesbarkeit
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        
        plt.tight_layout()
        
        # Speichere Plot
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        canvas = FigureCanvasTkAgg(fig, self.viz_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def export_report(self):
        if not self.drift_events:
            messagebox.showwarning("Warnung", "Keine Analyseergebnisse zum Exportieren vorhanden.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Report speichern",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                report_text = self.analyzer.generate_drift_report(self.df, self.drift_events)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_text)
                messagebox.showinfo("Erfolg", f"Report erfolgreich gespeichert:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern:\n{str(e)}")

def main():
    """Hauptfunktion zum Starten der GUI"""
    root = tk.Tk()
    app = DriftAnalysisGUI(root)
    
    # Styling für bessere Optik
    style = ttk.Style()
    style.theme_use('clam')
    
    root.mainloop()

if __name__ == "__main__":
    main()