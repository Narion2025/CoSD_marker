#!/usr/bin/env python3
"""
TXT Chat Analyzer - Direkte Analyse von Text-Dateien
===================================================
Analysiert Chat-Verläufe direkt aus TXT-Dateien ohne Vorverarbeitung.
Erkennt automatisch verschiedene Chat-Formate und wendet Marker an.

Unterstützte Formate:
- "Sprecher: Text"
- "**Sprecher**\nText" (Markdown)
- Einfache Text-Blöcke
- WhatsApp-Export Format
- Discord-Export Format

Autor: Ben Perro & Team
"""

import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import yaml
import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

class TxtChatAnalyzer:
    def __init__(self):
        self.marker_patterns = self._load_marker_patterns()
        self.chat_formats = [
            self._parse_colon_format,
            self._parse_markdown_format,
            self._parse_whatsapp_format,
            self._parse_discord_format,
            self._parse_simple_blocks
        ]
    
    def _load_marker_patterns(self):
        """Lädt Marker-Patterns - erweiterte Version für TXT-Analyse"""
        return {
            # Emotionale & Verhaltens-Marker
            'Widersprüche_Logikbrüche': [
                'aber gleichzeitig', 'widerspricht sich', 'das stimmt nicht', 
                'gegenteil', 'jedoch', 'allerdings', 'andererseits'
            ],
            'Unausgesprochene_Vorannahmen': [
                'natürlich', 'selbstverständlich', 'ist doch klar', 
                'offensichtlich', 'wie bekannt', 'alle wissen'
            ],
            'Abrupte_Themenwechsel': [
                'apropos', 'übrigens', 'mal was anderes', 'zurück zum thema',
                'nebenbei', 'ach ja', 'bevor ich vergesse'
            ],
            'Meta_Kommunikation': [
                'ich schweife ab', 'anders gesagt', 'um das klarzustellen',
                'wie ich das meine', 'gespräch', 'dialog', 'kommunikation'
            ],
            'Selbstkorrektur': [
                'korrektur', 'ich korrigiere', 'anders formuliert', 
                'was ich meinte', 'besser gesagt', 'ich formuliere neu'
            ],
            'Selbsterkenntnis': [
                'aha', 'jetzt verstehe ich', 'mir wird klar', 'überrascht mich',
                'erkenne ich', 'fällt mir auf', 'realisiere ich'
            ],
            
            # Spiral Dynamics
            'SD_Beige_Survival': [
                'grundbedürfnisse', 'überleben', 'sicherheit', 'instinkt',
                'hunger', 'durst', 'müde', 'erschöpft'
            ],
            'SD_Purpur_Stamm': [
                'tradition', 'stamm', 'ritual', 'zugehörigkeit',
                'familie', 'herkunft', 'ahnen', 'erbe'
            ],
            'SD_Rot_Ego': [
                'macht', 'durchsetzen', 'dominanz', 'ich will',
                'erobern', 'gewinnen', 'stark', 'schwach'
            ],
            'SD_Blau_Ordnung': [
                'ordnung', 'regeln', 'pflicht', 'struktur', 'autorität',
                'gesetz', 'richtig', 'falsch', 'disziplin'
            ],
            'SD_Orange_Leistung': [
                'ziel', 'erfolg', 'leistung', 'effizienz', 'strategie',
                'optimieren', 'bessern', 'konkurrenz', 'wettbewerb'
            ],
            'SD_Grün_Gemeinschaft': [
                'empathie', 'verständnis', 'gemeinschaft', 'gefühle', 'harmonie',
                'teilen', 'unterstützen', 'zusammen', 'verbunden'
            ],
            'SD_Gelb_System': [
                'system', 'komplex', 'flexibel', 'meta', 'kontext',
                'dynamik', 'emergent', 'anpassung', 'evolution'
            ],
            'SD_Türkis_Ganzheit': [
                'ganzheit', 'spirituell', 'verbunden', 'universum',
                'bewusstsein', 'transzendenz', 'einheit', 'kosmos'
            ],
            
            # Emotionale Intensität
            'Hohe_Positive_Emotion': [
                'fantastisch', 'wunderbar', 'großartig', 'begeistert',
                'liebe', 'freue mich', 'glücklich', 'perfekt'
            ],
            'Hohe_Negative_Emotion': [
                'furchtbar', 'schrecklich', 'hasse', 'wütend',
                'verzweifelt', 'katastrophe', 'horror', 'panik'
            ],
            'Gemäßigte_Emotion': [
                'okay', 'in ordnung', 'gut', 'schlecht',
                'angenehm', 'unangenehm', 'zufrieden', 'unzufrieden'
            ]
        }
    
    def analyze_txt_file(self, file_path):
        """Hauptanalyse-Funktion für TXT-Dateien"""
        try:
            # Datei einlesen
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Chat-Format erkennen und parsen
            parsed_chat = self._parse_chat_content(content)
            
            if not parsed_chat:
                return None, "Kein erkennbares Chat-Format gefunden"
            
            # DataFrame erstellen
            df = pd.DataFrame(parsed_chat)
            
            # Marker anwenden
            df = self._apply_all_markers(df)
            
            # Drift-Events erkennen
            drift_events = self._detect_drift_events(df)
            
            # Report generieren
            report = self._generate_comprehensive_report(df, drift_events, file_path)
            
            return df, report, drift_events
            
        except Exception as e:
            return None, f"Fehler bei der Analyse: {str(e)}", []
    
    def _parse_chat_content(self, content):
        """Versucht verschiedene Chat-Formate zu erkennen"""
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        for format_parser in self.chat_formats:
            try:
                result = format_parser(lines)
                if result and len(result) > 0:
                    return result
            except:
                continue
        
        # Fallback: Jede Zeile als separaten Eintrag behandeln
        return [{'line': i+1, 'speaker': 'Unknown', 'text': line} 
                for i, line in enumerate(lines)]
    
    def _parse_colon_format(self, lines):
        """Parst Format: 'Sprecher: Text'"""
        parsed = []
        for i, line in enumerate(lines):
            if ':' in line and not line.startswith('http'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    speaker = self._normalize_speaker_name(parts[0].strip())
                    text = parts[1].strip()
                    parsed.append({
                        'line': i + 1,
                        'speaker': speaker,
                        'text': text,
                        'timestamp': None
                    })
        return parsed if len(parsed) > len(lines) * 0.3 else None  # Mindestens 30% erkannt
    
    def _parse_markdown_format(self, lines):
        """Parst Markdown-Format mit **Sprecher** oder ## Sprecher"""
        parsed = []
        current_speaker = "Unknown"
        
        for i, line in enumerate(lines):
            if line.startswith('**') and line.endswith('**'):
                current_speaker = self._normalize_speaker_name(line.replace('**', ''))
            elif line.startswith('#'):
                current_speaker = self._normalize_speaker_name(line.replace('#', '').strip())
            elif line and not line.startswith('*') and not line.startswith('#'):
                parsed.append({
                    'line': len(parsed) + 1,
                    'speaker': current_speaker,
                    'text': line,
                    'timestamp': None
                })
        
        return parsed if len(parsed) > 0 else None
    
    def _parse_whatsapp_format(self, lines):
        """Parst WhatsApp-Export Format: [Datum, Zeit] Sprecher: Text"""
        parsed = []
        whatsapp_pattern = r'\[(\d{2}\.\d{2}\.\d{2,4},\s\d{2}:\d{2}:\d{2})\]\s(.+?):\s(.+)'
        
        for i, line in enumerate(lines):
            match = re.match(whatsapp_pattern, line)
            if match:
                timestamp_str = match.group(1)
                speaker = self._normalize_speaker_name(match.group(2))
                text = match.group(3)
                
                parsed.append({
                    'line': i + 1,
                    'speaker': speaker,
                    'text': text,
                    'timestamp': timestamp_str
                })
        
        return parsed if len(parsed) > len(lines) * 0.3 else None
    
    def _parse_discord_format(self, lines):
        """Parst Discord-Export ähnliche Formate"""
        parsed = []
        # Vereinfachte Discord-Pattern-Erkennung
        for i, line in enumerate(lines):
            # Discord hat oft Zeitstempel am Anfang
            if re.match(r'^\d{2}:\d{2}', line):
                parts = line.split(None, 2)  # Split bei Whitespace, max 3 Teile
                if len(parts) >= 3:
                    speaker = self._normalize_speaker_name(parts[1])
                    text = parts[2]
                    parsed.append({
                        'line': i + 1,
                        'speaker': speaker,
                        'text': text,
                        'timestamp': parts[0]
                    })
        
        return parsed if len(parsed) > 0 else None
    
    def _parse_simple_blocks(self, lines):
        """Parst einfache Text-Blöcke (Fallback)"""
        parsed = []
        current_speaker = "Unknown"
        
        # Versuche Sprecher durch häufige Muster zu erkennen
        speaker_indicators = ['ich:', 'user:', 'ai:', 'bot:', 'system:', 'narion:', 'claude:', 'gpt:']
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Prüfe auf Sprecher-Indikatoren
            for indicator in speaker_indicators:
                if line_lower.startswith(indicator):
                    current_speaker = self._normalize_speaker_name(indicator.replace(':', ''))
                    line = line[len(indicator):].strip()
                    break
            
            if line:  # Nicht-leere Zeile
                parsed.append({
                    'line': i + 1,
                    'speaker': current_speaker,
                    'text': line,
                    'timestamp': None
                })
        
        return parsed if len(parsed) > 0 else None
    
    def _normalize_speaker_name(self, speaker):
        """Normalisiert Sprecher-Namen"""
        speaker = speaker.lower().strip()
        
        mappings = {
            'chatgpt': 'AI', 'gpt': 'AI', 'claude': 'AI', 'narion': 'AI',
            'bot': 'AI', 'assistant': 'AI', 'ki': 'AI',
            'ich': 'User', 'user': 'User', 'ben': 'User', 'human': 'User',
            'you': 'User', 'du': 'User', 'nutzer': 'User'
        }
        
        return mappings.get(speaker, speaker.title())
    
    def _apply_all_markers(self, df):
        """Wendet alle Marker-Patterns auf den DataFrame an"""
        # Initialisiere Marker-Spalten
        for marker_name in self.marker_patterns:
            df[marker_name] = 0
        
        # Analysiere jeden Text
        for idx, row in df.iterrows():
            text = str(row['text']).lower()
            
            for marker_name, patterns in self.marker_patterns.items():
                count = 0
                for pattern in patterns:
                    count += len(re.findall(r'\b' + re.escape(pattern.lower()) + r'\b', text))
                df.at[idx, marker_name] = count
        
        # Emotionale Spikes basierend auf Textmerkmalen
        df['Emotionale_Intensivierung'] = df.apply(self._detect_emotional_spike, axis=1)
        
        return df
    
    def _detect_emotional_spike(self, row):
        """Erkennt emotionale Spikes anhand von Textmerkmalen"""
        text = str(row['text'])
        
        # Zähle Ausrufezeichen, Großbuchstaben, etc.
        exclamation_count = text.count('!')
        caps_words = len([word for word in text.split() if word.isupper() and len(word) > 2])
        repeated_chars = len(re.findall(r'(.)\1{2,}', text))  # aaa, bbb, etc.
        
        # Emotional intensive Wörter
        intense_words = ['sehr', 'extrem', 'wahnsinnig', 'unglaublich', 'total', 'komplett']
        intense_count = sum(1 for word in intense_words if word in text.lower())
        
        # Score berechnen
        spike_score = exclamation_count + caps_words + repeated_chars + intense_count
        
        return min(spike_score, 5)  # Max 5
    
    def _detect_drift_events(self, df):
        """Erkennt Drift-Events in den analysierten Daten"""
        drift_events = []
        
        # Marker-Spalten identifizieren
        marker_cols = [col for col in df.columns if col not in ['line', 'speaker', 'text', 'timestamp']]
        
        for idx, row in df.iterrows():
            # Hohe Marker-Aktivität
            total_markers = sum(row[col] for col in marker_cols if col != 'Emotionale_Intensivierung')
            
            if total_markers > 3:  # Schwellenwert
                active_markers = {col: row[col] for col in marker_cols if row[col] > 0}
                
                # Bestimme Drift-Typ
                drift_type = self._classify_drift_type(active_markers)
                
                drift_events.append({
                    'event_id': len(drift_events) + 1,
                    'line': idx + 1,
                    'speaker': row['speaker'],
                    'type': drift_type,
                    'intensity': total_markers,
                    'active_markers': active_markers,
                    'text_excerpt': row['text'][:100] + "..." if len(row['text']) > 100 else row['text'],
                    'description': self._generate_drift_description(drift_type, active_markers)
                })
        
        return drift_events
    
    def _classify_drift_type(self, active_markers):
        """Klassifiziert den Typ des Drift-Events"""
        # Spiral Dynamics Drift
        sd_markers = [k for k in active_markers.keys() if k.startswith('SD_')]
        if len(sd_markers) > 1:
            return "Spiral Dynamics Transition"
        
        # Emotionaler Drift
        emotion_markers = [k for k in active_markers.keys() if 'Emotion' in k]
        if emotion_markers:
            return "Emotionaler Drift"
        
        # Meta-Kommunikation
        meta_markers = [k for k in active_markers.keys() if 'Meta' in k or 'Kommunikation' in k]
        if meta_markers:
            return "Meta-Kommunikative Verdichtung"
        
        return "Allgemeine Marker-Verdichtung"
    
    def _generate_drift_description(self, drift_type, active_markers):
        """Generiert eine beschreibende Erklärung für das Drift-Event"""
        marker_descriptions = []
        for marker, count in active_markers.items():
            readable_name = marker.replace('_', ' ').replace('SD ', 'Spiral Dynamics: ')
            marker_descriptions.append(f"{readable_name} ({count}x)")
        
        if drift_type == "Spiral Dynamics Transition":
            return f"Wechsel zwischen Werteebenen erkannt. Aktive Ebenen: {', '.join(marker_descriptions[:3])}"
        elif drift_type == "Emotionaler Drift":
            return f"Emotionale Intensitätsveränderung mit {len(active_markers)} Signalen: {', '.join(marker_descriptions[:2])}"
        elif drift_type == "Meta-Kommunikative Verdichtung":
            return f"Reflexive Kommunikation über den Dialog mit {len(active_markers)} Meta-Elementen"
        else:
            return f"Semantische Verdichtung mit {len(active_markers)} gleichzeitigen Markern"
    
    def _generate_comprehensive_report(self, df, drift_events, file_path):
        """Generiert einen umfassenden, lesbaren Analysebericht"""
        report = []
        report.append("=" * 80)
        report.append("COMPREHENSIVE TXT CHAT ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Analysierte Datei: {Path(file_path).name}")
        report.append(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        report.append("")
        
        # Basis-Statistiken
        report.append("📊 BASIS-STATISTIKEN")
        report.append("-" * 40)
        report.append(f"Gesamtzahl Nachrichten: {len(df)}")
        
        speaker_counts = df['speaker'].value_counts()
        report.append(f"Sprecher erkannt: {', '.join(speaker_counts.index.tolist())}")
        for speaker, count in speaker_counts.items():
            report.append(f"  - {speaker}: {count} Nachrichten ({count/len(df)*100:.1f}%)")
        
        # Marker-Aktivität
        marker_cols = [col for col in df.columns if col not in ['line', 'speaker', 'text', 'timestamp']]
        total_marker_activity = df[marker_cols].sum().sum()
        report.append(f"Gesamte Marker-Aktivität: {total_marker_activity}")
        report.append("")
        
        # Top aktive Marker
        report.append("🎯 TOP AKTIVE MARKER")
        report.append("-" * 40)
        marker_totals = df[marker_cols].sum().sort_values(ascending=False)
        top_markers = marker_totals[marker_totals > 0].head(10)
        
        for marker, total in top_markers.items():
            readable_name = marker.replace('_', ' ')
            report.append(f"  {readable_name}: {int(total)} Treffer")
        report.append("")
        
        # Drift-Events Detail
        if drift_events:
            report.append("🌊 DRIFT-EVENTS ANALYSE")
            report.append("-" * 40)
            report.append(f"Erkannte Drift-Events: {len(drift_events)}")
            report.append("")
            
            # Gruppiere Events nach Typ
            event_types = {}
            for event in drift_events:
                event_type = event['type']
                if event_type not in event_types:
                    event_types[event_type] = []
                event_types[event_type].append(event)
            
            for event_type, events in event_types.items():
                report.append(f"📍 {event_type.upper()} ({len(events)} Events)")
                report.append("-" * 30)
                
                for event in events[:3]:  # Zeige max. 3 Events pro Typ
                    report.append(f"Event #{event['event_id']} - Zeile {event['line']} ({event['speaker']})")
                    report.append(f"  Beschreibung: {event['description']}")
                    report.append(f"  Intensität: {event['intensity']}")
                    report.append(f"  Text: \"{event['text_excerpt']}\"")
                    report.append("")
                
                if len(events) > 3:
                    report.append(f"  ... und {len(events) - 3} weitere Events dieses Typs")
                    report.append("")
        else:
            report.append("🌊 DRIFT-EVENTS ANALYSE")
            report.append("-" * 40)
            report.append("Keine signifikanten Drift-Events erkannt.")
            report.append("Das deutet auf ein gleichmäßiges, kohärentes Gespräch hin.")
            report.append("")
        
        # Kommunikations-Muster
        report.append("💬 KOMMUNIKATIONS-MUSTER")
        report.append("-" * 40)
        
        # Durchschnittliche Nachrichtenlänge
        avg_length = df['text'].str.len().mean()
        report.append(f"Durchschnittliche Nachrichtenlänge: {avg_length:.1f} Zeichen")
        
        # Spiral Dynamics Verteilung
        sd_cols = [col for col in marker_cols if col.startswith('SD_')]
        if sd_cols:
            sd_activity = df[sd_cols].sum()
            dominant_sd = sd_activity.idxmax() if sd_activity.sum() > 0 else "Keine"
            if dominant_sd != "Keine":
                report.append(f"Dominante Werteebene: {dominant_sd.replace('SD_', '').replace('_', ' ')}")
        
        # Emotionale Trends
        if 'Emotionale_Intensivierung' in df.columns:
            avg_emotion = df['Emotionale_Intensivierung'].mean()
            max_emotion = df['Emotionale_Intensivierung'].max()
            report.append(f"Durchschnittliche emotionale Intensität: {avg_emotion:.1f}/5")
            report.append(f"Maximale emotionale Intensität: {max_emotion}/5")
        
        report.append("")
        
        # Empfehlungen
        report.append("💡 ANALYSE-EMPFEHLUNGEN")
        report.append("-" * 40)
        
        if len(drift_events) > len(df) * 0.1:  # Mehr als 10% Drift-Events
            report.append("• Hohe Drift-Aktivität erkannt - das Gespräch zeigt starke semantische Dynamik")
            report.append("• Empfehlung: Prüfen Sie kritische Übergangspunkte auf Kommunikationsstörungen")
        elif len(drift_events) == 0:
            report.append("• Sehr stabile Kommunikation ohne erkennbare Drifts")
            report.append("• Empfehlung: Gespräch zeigt hohe Kohärenz und Fokus")
        else:
            report.append("• Moderate Drift-Aktivität - normales Gesprächsmuster")
            report.append("• Empfehlung: Einzelne Events genauer analysieren für Optimierungspotential")
        
        if total_marker_activity > len(df) * 2:
            report.append("• Hohe Marker-Dichte deutet auf komplexe, nuancierte Kommunikation hin")
        
        report.append("")
        report.append("=" * 80)
        report.append("Ende des Analyseberichts")
        report.append("=" * 80)
        
        return "\n".join(report)

class TxtAnalysisGUI:
    def __init__(self, root):
        self.root = root
        self.analyzer = TxtChatAnalyzer()
        self.current_df = None
        self.current_report = ""
        self.current_events = []
        
        self.setup_gui()
    
    def setup_gui(self):
        self.root.title("TXT Chat Drift Analyzer")
        self.root.geometry("1000x700")
        
        # Hauptframe
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Datei-Bereich
        file_frame = ttk.LabelFrame(main_frame, text="TXT-Datei Analyse", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(file_frame, text="Unterstützte Formate:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W)
        format_text = "• Sprecher: Text\n• **Sprecher** (Markdown)\n• WhatsApp Export\n• Einfache Textblöcke"
        ttk.Label(file_frame, text=format_text, font=('Arial', 9)).grid(row=1, column=0, sticky=tk.W, pady=(5, 10))
        
        ttk.Button(file_frame, text="TXT-Datei laden & analysieren", 
                  command=self.load_and_analyze, style='Accent.TButton').grid(row=2, column=0, pady=5)
        
        self.status_label = ttk.Label(file_frame, text="Keine Datei geladen", foreground='gray')
        self.status_label.grid(row=3, column=0, pady=5)
        
        # Ergebnis-Notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Tab 1: Übersicht
        self.overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_frame, text="📊 Übersicht")
        
        # Tab 2: Vollständiger Report
        self.report_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.report_frame, text="📄 Vollständiger Report")
        
        # Tab 3: Drift-Events
        self.events_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.events_frame, text="🌊 Drift-Events")
        
        # Tab 4: Daten-Export
        self.export_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.export_frame, text="💾 Export")
        
        # Responsive Design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Style
        style = ttk.Style()
        style.configure('Accent.TButton', background='#0078d4', foreground='white')
    
    def load_and_analyze(self):
        file_path = filedialog.askopenfilename(
            title="TXT Chat-Datei auswählen",
            filetypes=[
                ("Text files", "*.txt"),
                ("Markdown files", "*.md"), 
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        self.status_label.config(text="Analysiere Datei...", foreground='blue')
        self.root.update()
        
        try:
            result = self.analyzer.analyze_txt_file(file_path)
            
            if result[0] is None:  # Fehler aufgetreten
                messagebox.showerror("Analyse-Fehler", result[1])
                self.status_label.config(text="Analyse fehlgeschlagen", foreground='red')
                return
            
            self.current_df, self.current_report, self.current_events = result
            
            # GUI aktualisieren
            self.update_overview()
            self.update_report()
            self.update_events()
            self.update_export()
            
            # Status
            file_name = Path(file_path).name
            self.status_label.config(
                text=f"✅ {file_name} analysiert - {len(self.current_df)} Nachrichten, {len(self.current_events)} Drift-Events",
                foreground='green'
            )
            
            messagebox.showinfo("Analyse abgeschlossen", 
                               f"TXT-Datei erfolgreich analysiert!\n\n"
                               f"📝 Nachrichten: {len(self.current_df)}\n"
                               f"🎯 Erkannte Marker: {len([col for col in self.current_df.columns if col not in ['line', 'speaker', 'text', 'timestamp']])}\n"
                               f"🌊 Drift-Events: {len(self.current_events)}")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Unerwarteter Fehler:\n{str(e)}")
            self.status_label.config(text="Analyse fehlgeschlagen", foreground='red')
    
    def update_overview(self):
        # Lösche alte Inhalte
        for widget in self.overview_frame.winfo_children():
            widget.destroy()
        
        if self.current_df is None:
            ttk.Label(self.overview_frame, text="Keine Daten geladen", 
                     font=('Arial', 12)).pack(pady=20)
            return
        
        # Scrollbarer Bereich
        canvas = tk.Canvas(self.overview_frame)
        scrollbar = ttk.Scrollbar(self.overview_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Basis-Info
        info_frame = ttk.LabelFrame(scrollable_frame, text="📊 Basis-Statistiken", padding="10")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        stats_text = f"""Gesamte Nachrichten: {len(self.current_df)}
Erkannte Sprecher: {len(self.current_df['speaker'].unique())}
Drift-Events: {len(self.current_events)}
Durchschnittliche Nachrichtenlänge: {self.current_df['text'].str.len().mean():.1f} Zeichen"""
        
        ttk.Label(info_frame, text=stats_text, font=('Arial', 11)).pack(anchor="w")
        
        # Top Marker
        marker_cols = [col for col in self.current_df.columns if col not in ['line', 'speaker', 'text', 'timestamp']]
        if marker_cols:
            marker_frame = ttk.LabelFrame(scrollable_frame, text="🎯 Aktivste Marker", padding="10")
            marker_frame.pack(fill="x", padx=10, pady=5)
            
            marker_totals = self.current_df[marker_cols].sum().sort_values(ascending=False)
            top_5 = marker_totals[marker_totals > 0].head(5)
            
            for marker, total in top_5.items():
                readable_name = marker.replace('_', ' ')
                ttk.Label(marker_frame, text=f"• {readable_name}: {int(total)} Treffer", 
                         font=('Arial', 10)).pack(anchor="w")
        
        # Sprecher-Verteilung
        speaker_frame = ttk.LabelFrame(scrollable_frame, text="👥 Sprecher-Verteilung", padding="10")
        speaker_frame.pack(fill="x", padx=10, pady=5)
        
        speaker_counts = self.current_df['speaker'].value_counts()
        for speaker, count in speaker_counts.items():
            percentage = count / len(self.current_df) * 100
            ttk.Label(speaker_frame, text=f"• {speaker}: {count} Nachrichten ({percentage:.1f}%)", 
                     font=('Arial', 10)).pack(anchor="w")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def update_report(self):
        # Lösche alte Inhalte
        for widget in self.report_frame.winfo_children():
            widget.destroy()
        
        if not self.current_report:
            ttk.Label(self.report_frame, text="Kein Report verfügbar", 
                     font=('Arial', 12)).pack(pady=20)
            return
        
        # Scrollbarer Text
        text_widget = scrolledtext.ScrolledText(self.report_frame, wrap=tk.WORD, 
                                              font=('Courier', 10), padx=10, pady=10)
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, self.current_report)
        text_widget.config(state=tk.DISABLED)
    
    def update_events(self):
        # Lösche alte Inhalte
        for widget in self.events_frame.winfo_children():
            widget.destroy()
        
        if not self.current_events:
            ttk.Label(self.events_frame, text="Keine Drift-Events erkannt", 
                     font=('Arial', 12)).pack(pady=20)
            return
        
        # Scrollbarer Bereich für Events
        canvas = tk.Canvas(self.events_frame)
        scrollbar = ttk.Scrollbar(self.events_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Events darstellen
        for event in self.current_events:
            event_frame = ttk.LabelFrame(scrollable_frame, 
                                       text=f"Event #{event['event_id']} - {event['type']}", 
                                       padding="10")
            event_frame.pack(fill="x", padx=10, pady=5)
            
            # Event-Info
            info_text = f"Zeile {event['line']} • {event['speaker']} • Intensität: {event['intensity']}"
            ttk.Label(event_frame, text=info_text, font=('Arial', 10, 'bold')).pack(anchor="w")
            
            # Beschreibung
            ttk.Label(event_frame, text=event['description'], 
                     font=('Arial', 10), wraplength=700).pack(anchor="w", pady=(5, 0))
            
            # Text-Ausschnitt
            text_frame = ttk.Frame(event_frame)
            text_frame.pack(fill="x", pady=(5, 0))
            ttk.Label(text_frame, text="Text:", font=('Arial', 9, 'bold')).pack(anchor="w")
            ttk.Label(text_frame, text=f'"{event["text_excerpt"]}"', 
                     font=('Arial', 9, 'italic'), wraplength=700, 
                     foreground='gray').pack(anchor="w")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def update_export(self):
        # Lösche alte Inhalte
        for widget in self.export_frame.winfo_children():
            widget.destroy()
        
        if self.current_df is None:
            ttk.Label(self.export_frame, text="Keine Daten zum Exportieren", 
                     font=('Arial', 12)).pack(pady=20)
            return
        
        export_frame = ttk.LabelFrame(self.export_frame, text="📤 Export-Optionen", padding="20")
        export_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ttk.Label(export_frame, text="Verfügbare Export-Formate:", 
                 font=('Arial', 12, 'bold')).pack(anchor="w", pady=(0, 10))
        
        # Export-Buttons
        ttk.Button(export_frame, text="📄 Report als TXT speichern", 
                  command=self.export_report_txt).pack(fill="x", pady=5)
        
        ttk.Button(export_frame, text="📊 Daten als CSV speichern", 
                  command=self.export_data_csv).pack(fill="x", pady=5)
        
        ttk.Button(export_frame, text="🌊 Drift-Events als JSON speichern", 
                  command=self.export_events_json).pack(fill="x", pady=5)
        
        ttk.Button(export_frame, text="📈 Visualisierung erstellen", 
                  command=self.create_visualization).pack(fill="x", pady=5)
    
    def export_report_txt(self):
        if not self.current_report:
            messagebox.showwarning("Warnung", "Kein Report zum Exportieren vorhanden.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Report speichern",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.current_report)
                messagebox.showinfo("Export erfolgreich", f"Report gespeichert:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export-Fehler", f"Fehler beim Speichern:\n{str(e)}")
    
    def export_data_csv(self):
        if self.current_df is None:
            messagebox.showwarning("Warnung", "Keine Daten zum Exportieren vorhanden.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Daten als CSV speichern",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.current_df.to_csv(file_path, index=False, encoding='utf-8')
                messagebox.showinfo("Export erfolgreich", f"Daten gespeichert:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export-Fehler", f"Fehler beim Speichern:\n{str(e)}")
    
    def export_events_json(self):
        if not self.current_events:
            messagebox.showwarning("Warnung", "Keine Events zum Exportieren vorhanden.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Drift-Events als JSON speichern",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_events, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Export erfolgreich", f"Events gespeichert:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export-Fehler", f"Fehler beim Speichern:\n{str(e)}")
    
    def create_visualization(self):
        if self.current_df is None:
            messagebox.showwarning("Warnung", "Keine Daten für Visualisierung vorhanden.")
            return
        
        try:
            # Einfache Visualisierung erstellen
            fig, axes = plt.subplots(2, 2, figsize=(12, 8))
            fig.suptitle('TXT Chat Analyse - Visualisierung', fontsize=14, fontweight='bold')
            
            # Plot 1: Drift-Events über Zeit
            if self.current_events:
                event_lines = [event['line'] for event in self.current_events]
                event_types = [event['type'] for event in self.current_events]
                
                ax1 = axes[0, 0]
                type_colors = {'Emotionaler Drift': 'red', 'Spiral Dynamics Transition': 'blue', 
                              'Meta-Kommunikative Verdichtung': 'green', 'Allgemeine Marker-Verdichtung': 'orange'}
                
                for i, (line, event_type) in enumerate(zip(event_lines, event_types)):
                    color = type_colors.get(event_type, 'gray')
                    ax1.scatter(line, i, c=color, s=100, alpha=0.7)
                
                ax1.set_xlabel('Nachricht (Zeile)')
                ax1.set_ylabel('Event Index')
                ax1.set_title('Drift-Events im Verlauf')
                ax1.grid(True, alpha=0.3)
            
            # Plot 2: Sprecher-Verteilung
            ax2 = axes[0, 1]
            speaker_counts = self.current_df['speaker'].value_counts()
            ax2.pie(speaker_counts.values, labels=speaker_counts.index, autopct='%1.1f%%')
            ax2.set_title('Sprecher-Verteilung')
            
            # Plot 3: Top Marker
            ax3 = axes[1, 0]
            marker_cols = [col for col in self.current_df.columns if col not in ['line', 'speaker', 'text', 'timestamp']]
            if marker_cols:
                marker_totals = self.current_df[marker_cols].sum().sort_values(ascending=False).head(8)
                bars = ax3.bar(range(len(marker_totals)), marker_totals.values)
                ax3.set_xticks(range(len(marker_totals)))
                ax3.set_xticklabels([name.replace('_', '\n') for name in marker_totals.index], 
                                   rotation=45, ha='right', fontsize=8)
                ax3.set_title('Top Marker-Aktivität')
                ax3.set_ylabel('Anzahl Treffer')
            
            # Plot 4: Nachrichtenlängen
            ax4 = axes[1, 1]
            msg_lengths = self.current_df['text'].str.len()
            ax4.hist(msg_lengths, bins=20, alpha=0.7, edgecolor='black')
            ax4.set_xlabel('Nachrichtenlänge (Zeichen)')
            ax4.set_ylabel('Häufigkeit')
            ax4.set_title('Verteilung Nachrichtenlängen')
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            messagebox.showerror("Visualisierung-Fehler", f"Fehler beim Erstellen der Visualisierung:\n{str(e)}")

def main():
    root = tk.Tk()
    app = TxtAnalysisGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()