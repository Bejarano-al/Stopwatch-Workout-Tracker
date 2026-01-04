import tkinter as tk
import time
import threading
import json
import os
from datetime import datetime
from tkinter import messagebox, simpledialog

class WorkoutTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Workout Timer")
        self.root.geometry("500x650")
        
        # Timer variables
        self.main_running = False
        self.main_seconds = 0
        self.exercise_running = False
        self.exercise_seconds = 0
        self.rest_running = False
        self.rest_seconds = 0
        
        # Data storage
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(script_dir, "workout_data.json")
        self.archive_folder = os.path.join(script_dir, "archive")
        self.reports_folder = os.path.join(script_dir, "reports")
        self.setup_folders()
        
        # Create menu bar
        self.create_menu()
        
        # Main timer display (big font)
        self.main_timer_label = tk.Label(root, text="00:00", font=("Arial", 48), fg="blue")
        self.main_timer_label.pack(pady=20)
        
        # Main timer controls frame
        control_frame = tk.Frame(root)
        control_frame.pack(pady=10)
        
        self.start_button = tk.Button(control_frame, text="Start Workout", width=15, command=self.start_main_timer)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.pause_button = tk.Button(control_frame, text="Pause", width=15, command=self.pause_main_timer, state="disabled")
        self.pause_button.grid(row=0, column=1, padx=5)
        
        self.reset_button = tk.Button(control_frame, text="Reset", width=15, command=self.reset_all)
        self.reset_button.grid(row=0, column=2, padx=5)
        
        # Save workout button
        self.save_button = tk.Button(root, text="Save This Workout", width=20, 
                                     command=self.save_workout, state="disabled", bg="lightblue")
        self.save_button.pack(pady=10)
        
        # Separator
        separator = tk.Frame(root, height=2, bg="gray")
        separator.pack(fill="x", pady=20)
        
        # Workout section label
        workout_label = tk.Label(root, text="Workout Tracking:", font=("Arial", 12))
        workout_label.pack()
        
        # Exercise section
        exercise_frame = tk.Frame(root)
        exercise_frame.pack(pady=10)
        
        # Exercise button
        self.exercise_button = tk.Button(exercise_frame, text="Exercising", width=15, height=2, 
                                         command=self.start_exercise, state="disabled", bg="lightgreen")
        self.exercise_button.grid(row=0, column=0, padx=10)
        
        # Exercise timer display (same size as button)
        self.exercise_display = tk.Label(exercise_frame, text="00:00", width=15, height=2, 
                                         font=("Arial", 16), relief="sunken", bg="green", fg="white")
        self.exercise_display.grid(row=0, column=1, padx=10)
        
        # Rest section
        rest_frame = tk.Frame(root)
        rest_frame.pack(pady=10)
        
        # Rest button
        self.rest_button = tk.Button(rest_frame, text="Resting", width=15, height=2, 
                                     command=self.start_rest, state="disabled", bg="lightcoral")
        self.rest_button.grid(row=0, column=0, padx=10)
        
        # Rest timer display
        self.rest_display = tk.Label(rest_frame, text="00:00", width=15, height=2, 
                                     font=("Arial", 16), relief="sunken", bg="red", fg="white")
        self.rest_display.grid(row=0, column=1, padx=10)
        
        # Notes section
        notes_frame = tk.Frame(root)
        notes_frame.pack(pady=10)
        
        tk.Label(notes_frame, text="Workout Notes:").pack()
        self.notes_entry = tk.Text(notes_frame, height=3, width=40)
        self.notes_entry.pack()
        
        # Status display
        self.status_label = tk.Label(root, text="Status: Ready", font=("Arial", 10))
        self.status_label.pack(pady=10)
        
        # Report button (Monthly reset)
        self.report_button = tk.Button(root, text="Generate Monthly Report", width=25, 
                                       command=self.generate_monthly_report, bg="orange")
        self.report_button.pack(pady=10)
        
        # Display total workouts this month
        self.summary_label = tk.Label(root, text="", font=("Arial", 10))
        self.summary_label.pack(pady=5)
        self.update_summary()
        
        # Timer threads
        self.main_timer_thread = None
        self.exercise_timer_thread = None
        self.rest_timer_thread = None
        
        # Track start time
        self.workout_start_time = None
    
    def setup_folders(self):
        """Create necessary folders if they don't exist"""
        if not os.path.exists(self.archive_folder):
            os.makedirs(self.archive_folder)
        if not os.path.exists(self.reports_folder):
            os.makedirs(self.reports_folder)
    
    def create_menu(self):
        """Create menu bar with options"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="View Current Data", command=self.view_current_data)
        file_menu.add_command(label="View Reports", command=self.view_reports)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Quick Save Workout", command=self.quick_save_workout)
        tools_menu.add_command(label="Generate Test Report", command=self.generate_test_report)
    
    def update_main_timer(self):
        """Update main timer display"""
        while self.main_running:
            time.sleep(1)
            self.main_seconds += 1
            mins, secs = divmod(self.main_seconds, 60)
            self.main_timer_label.config(text=f"{mins:02d}:{secs:02d}")
    
    def update_exercise_timer(self):
        """Update exercise timer display"""
        while self.exercise_running:
            time.sleep(1)
            self.exercise_seconds += 1
            mins, secs = divmod(self.exercise_seconds, 60)
            self.exercise_display.config(text=f"{mins:02d}:{secs:02d}")
    
    def update_rest_timer(self):
        """Update rest timer display"""
        while self.rest_running:
            time.sleep(1)
            self.rest_seconds += 1
            mins, secs = divmod(self.rest_seconds, 60)
            self.rest_display.config(text=f"{mins:02d}:{secs:02d}")
    
    def start_main_timer(self):
        """Start the main timer"""
        if not self.main_running:
            self.main_running = True
            self.workout_start_time = datetime.now()
            
            # Start main timer thread
            self.main_timer_thread = threading.Thread(target=self.update_main_timer, daemon=True)
            self.main_timer_thread.start()
            
            # Enable exercise/rest buttons and save button
            self.exercise_button.config(state="normal")
            self.rest_button.config(state="normal")
            self.save_button.config(state="normal")
            self.start_button.config(state="disabled")
            self.pause_button.config(state="normal")
            self.status_label.config(text="Status: Workout Started")
    
    def pause_main_timer(self):
        """Pause the main timer"""
        if self.main_running:
            self.main_running = False
            
            # Also pause exercise/rest timers
            if self.exercise_running:
                self.exercise_running = False
            if self.rest_running:
                self.rest_running = False
            
            # Update button states
            self.start_button.config(state="normal")
            self.pause_button.config(state="disabled")
            self.exercise_button.config(state="disabled")
            self.rest_button.config(state="disabled")
            self.status_label.config(text="Status: Paused")
    
    def reset_all(self):
        """Reset all timers"""
        self.main_running = False
        self.exercise_running = False
        self.rest_running = False
        
        # Reset all times
        self.main_seconds = 0
        self.exercise_seconds = 0
        self.rest_seconds = 0
        self.workout_start_time = None
        
        # Reset all displays
        self.main_timer_label.config(text="00:00")
        self.exercise_display.config(text="00:00")
        self.rest_display.config(text="00:00")
        
        # Reset button states
        self.exercise_button.config(state="disabled")
        self.rest_button.config(state="disabled")
        self.save_button.config(state="disabled")
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled")
        self.status_label.config(text="Status: Reset")
        
        # Clear notes
        self.notes_entry.delete("1.0", tk.END)
    
    def start_exercise(self):
        """Start exercise timer"""
        if self.main_running and not self.exercise_running:
            # Stop rest timer if running
            if self.rest_running:
                self.rest_running = False
            
            # Start exercise timer
            self.exercise_running = True
            self.exercise_timer_thread = threading.Thread(target=self.update_exercise_timer, daemon=True)
            self.exercise_timer_thread.start()
            
            # Update button states
            self.exercise_button.config(state="disabled")
            self.rest_button.config(state="normal")
            self.status_label.config(text="Status: Exercising")
    
    def start_rest(self):
        """Start rest timer"""
        if self.main_running and not self.rest_running:
            # Stop exercise timer if running
            if self.exercise_running:
                self.exercise_running = False
            
            # Start rest timer
            self.rest_running = True
            self.rest_timer_thread = threading.Thread(target=self.update_rest_timer, daemon=True)
            self.rest_timer_thread.start()
            
            # Update button states
            self.exercise_button.config(state="normal")
            self.rest_button.config(state="disabled")
            self.status_label.config(text="Status: Resting")
    
    def save_workout(self):
        """Save current workout to JSON file"""
        if not self.workout_start_time:
            messagebox.showerror("Error", "No workout to save!")
            return
        
        # Calculate workout duration in hours
        total_seconds = self.main_seconds
        total_hours = total_seconds / 3600.0
        
        # Calculate exercise time
        exercise_hours = self.exercise_seconds / 3600.0
        
        # Get notes
        notes = self.notes_entry.get("1.0", tk.END).strip()
        
        # Create workout data
        workout_date = self.workout_start_time.date().isoformat()
        start_time = self.workout_start_time.strftime("%H:%M:%S")
        
        workout_data = {
            "date": workout_date,
            "start_time": start_time,
            "total_duration_hours": round(total_hours, 2),
            "exercise_duration_hours": round(exercise_hours, 2),
            "total_seconds": total_seconds,
            "exercise_seconds": self.exercise_seconds,
            "notes": notes,
            "saved_at": datetime.now().isoformat()
        }
        
        # Load existing data
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {"workouts": []}
        except json.JSONDecodeError:
            data = {"workouts": []}
        
        # Add new workout
        data["workouts"].append(workout_data)
        
        # Save to file
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)
        
        # Show success message
        messagebox.showinfo("Workout Saved", 
                           f"Workout saved!\n"
                           f"Date: {workout_date}\n"
                           f"Time: {start_time}\n"
                           f"Duration: {round(total_hours, 2)} hours\n"
                           f"Exercise time: {round(exercise_hours, 2)} hours")
        
        # Update summary
        self.update_summary()
        
        # Reset timers for next workout
        self.reset_all()
    
    def quick_save_workout(self):
        """Quick save without needing timers to be running"""
        if messagebox.askyesno("Quick Save", "Save a workout manually?"):
            notes = simpledialog.askstring("Notes", "Enter workout notes:")
            if notes is None:
                notes = ""
            
            # Create workout data
            now = datetime.now()
            workout_data = {
                "date": now.date().isoformat(),
                "start_time": now.strftime("%H:%M:%S"),
                "total_duration_hours": 0,
                "exercise_duration_hours": 0,
                "total_seconds": 0,
                "exercise_seconds": 0,
                "notes": notes,
                "saved_at": now.isoformat(),
                "manual_save": True
            }
            
            # Load existing data
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = {"workouts": []}
            except json.JSONDecodeError:
                data = {"workouts": []}
            
            # Add new workout
            data["workouts"].append(workout_data)
            
            # Save to file
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=4)
            
            messagebox.showinfo("Saved", "Workout manually saved!")
            self.update_summary()
    
    def generate_monthly_report(self):
        """Generate monthly report and reset data"""
        if not os.path.exists(self.data_file):
            messagebox.showwarning("No Data", "No workout data found to generate report!")
            return
        
        try:
            # Load current data
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            if "workouts" not in data or len(data["workouts"]) == 0:
                messagebox.showwarning("No Data", "No workouts found to generate report!")
                return
            
            # Get current month and year for report name
            now = datetime.now()
            report_month = now.strftime("%B_%Y")
            
            # Create report content
            report_content = self.create_report_content(data, report_month)
            
            # Save report to file
            report_filename = f"workout_report_{report_month}.txt"
            report_path = os.path.join(self.reports_folder, report_filename)
            
            with open(report_path, 'w') as f:
                f.write(report_content)
            
            # Archive current data
            archive_filename = f"workout_data_{report_month}.json"
            archive_path = os.path.join(self.archive_folder, archive_filename)
            
            # Add metadata to archived data
            data["archived_at"] = now.isoformat()
            data["report_generated"] = True
            
            with open(archive_path, 'w') as f:
                json.dump(data, f, indent=4)
            
            # Clear current data file
            with open(self.data_file, 'w') as f:
                json.dump({"workouts": [], "last_report": report_month}, f, indent=4)
            
            # Show success message
            messagebox.showinfo("Report Generated", 
                              f"Monthly report created!\n\n"
                              f"Report saved to: {report_path}\n"
                              f"Data archived to: {archive_path}\n\n"
                              f"Data has been reset for next month.")
            
            # Update summary
            self.update_summary()
            
            # Show report preview
            self.show_report_preview(report_content)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def create_report_content(self, data, report_month):
        """Create formatted report content"""
        now = datetime.now()
        workouts = data.get("workouts", [])
        
        # Sort workouts by date
        workouts.sort(key=lambda x: x.get("date", ""))
        
        # Calculate statistics
        total_hours = sum(w.get("total_duration_hours", 0) for w in workouts)
        exercise_hours = sum(w.get("exercise_duration_hours", 0) for w in workouts)
        total_workouts = len(workouts)
        
        # Create report header
        report = "=" * 60 + "\n"
        report += f"MONTHLY WORKOUT REPORT - {report_month.replace('_', ' ')}\n"
        report += f"Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "=" * 60 + "\n\n"
        
        # Add summary statistics
        report += "SUMMARY STATISTICS:\n"
        report += "-" * 30 + "\n"
        report += f"Total workouts this month: {total_workouts}\n"
        report += f"Total time trained: {total_hours:.2f} hours\n"
        report += f"Total exercise time: {exercise_hours:.2f} hours\n"
        if total_workouts > 0:
            report += f"Average per workout: {total_hours/total_workouts:.2f} hours\n"
        report += "\n"
        
        # Add detailed workout list
        report += "DETAILED WORKOUT LOG:\n"
        report += "-" * 60 + "\n"
        
        for i, workout in enumerate(workouts, 1):
            date_str = workout.get("date", "Unknown")
            start_time = workout.get("start_time", "Unknown")
            duration = workout.get("total_duration_hours", 0)
            exercise = workout.get("exercise_duration_hours", 0)
            notes = workout.get("notes", "")
            manual = workout.get("manual_save", False)
            
            report += f"\n{i}. {date_str} at {start_time}\n"
            report += f"   Total duration: {duration:.2f} hours\n"
            report += f"   Exercise time: {exercise:.2f} hours\n"
            if manual:
                report += f"   [MANUAL ENTRY]\n"
            if notes:
                report += f"   Notes: {notes}\n"
        
        report += "\n" + "=" * 60 + "\n"
        report += "End of Report\n"
        report += "=" * 60
        
        return report
    
    def show_report_preview(self, report_content):
        """Show a preview of the generated report"""
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Report Preview")
        preview_window.geometry("600x500")
        
        tk.Label(preview_window, text="Monthly Report Preview", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        text_frame = tk.Frame(preview_window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        text_widget = tk.Text(text_frame, wrap="word", yscrollcommand=scrollbar.set)
        text_widget.pack(side="left", fill="both", expand=True)
        text_widget.insert("1.0", report_content)
        text_widget.config(state="disabled")
        
        scrollbar.config(command=text_widget.yview)
        
        tk.Button(preview_window, text="Close", 
                 command=preview_window.destroy).pack(pady=10)
    
    def update_summary(self):
        """Update the summary label with current month's data"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                workouts = data.get("workouts", [])
                total_workouts = len(workouts)
                
                if total_workouts > 0:
                    total_hours = sum(w.get("total_duration_hours", 0) for w in workouts)
                    month = datetime.now().strftime("%B")
                    
                    self.summary_label.config(
                        text=f"This month ({month}): {total_workouts} workouts, {total_hours:.1f} total hours",
                        fg="green"
                    )
                else:
                    self.summary_label.config(
                        text="No workouts saved this month yet",
                        fg="gray"
                    )
            else:
                self.summary_label.config(
                    text="No data file found. Start your first workout!",
                    fg="gray"
                )
        except:
            self.summary_label.config(text="Error loading data", fg="red")
    
    def view_current_data(self):
        """View current workout data"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                # Create a simple display
                display_text = "Current Workout Data:\n" + "="*40 + "\n\n"
                
                if "workouts" in data and len(data["workouts"]) > 0:
                    for i, workout in enumerate(data["workouts"], 1):
                        display_text += f"{i}. {workout['date']} at {workout['start_time']}\n"
                        display_text += f"   Duration: {workout['total_duration_hours']:.2f} hours\n"
                        if workout.get('notes'):
                            display_text += f"   Notes: {workout['notes']}\n"
                        display_text += "\n"
                    
                    total = len(data["workouts"])
                    display_text += f"Total workouts: {total}\n"
                else:
                    display_text += "No workouts saved yet.\n"
                
                # Show in messagebox
                messagebox.showinfo("Current Data", display_text)
            else:
                messagebox.showinfo("Current Data", "No workout data file found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
    
    def view_reports(self):
        """View existing reports"""
        try:
            reports = os.listdir(self.reports_folder)
            if reports:
                reports_list = "\n".join(reports)
                messagebox.showinfo("Available Reports", 
                                  f"Reports found:\n\n{reports_list}\n\n"
                                  f"Reports are saved in the '{self.reports_folder}' folder.")
            else:
                messagebox.showinfo("Available Reports", 
                                  f"No reports found yet.\n"
                                  f"Generate a monthly report first!")
        except:
            messagebox.showinfo("Available Reports", 
                              f"No reports found yet.\n"
                              f"Generate a monthly report first!")
    
    def generate_test_report(self):
        """Generate a test report with sample data (for testing)"""
        if messagebox.askyesno("Test Report", 
                              "Generate a test report with sample data?\n"
                              "This will not affect your real data."):
            
            # Create sample data
            sample_data = {
                "workouts": [
                    {
                        "date": "2024-01-15",
                        "start_time": "18:30:00",
                        "total_duration_hours": 1.5,
                        "exercise_duration_hours": 1.2,
                        "notes": "Cardio day"
                    },
                    {
                        "date": "2024-01-18",
                        "start_time": "19:15:00",
                        "total_duration_hours": 2.0,
                        "exercise_duration_hours": 1.8,
                        "notes": "Strength training"
                    },
                    {
                        "date": "2024-01-22",
                        "start_time": "17:45:00",
                        "total_duration_hours": 1.75,
                        "exercise_duration_hours": 1.5,
                        "notes": "Mixed workout"
                    }
                ]
            }
            
            # Create test report
            report_month = "Test_Report"
            report_content = self.create_report_content(sample_data, report_month)
            
            # Save test report
            report_path = os.path.join(self.reports_folder, f"TEST_report.txt")
            with open(report_path, 'w') as f:
                f.write(report_content)
            
            messagebox.showinfo("Test Report", 
                              f"Test report created at:\n{report_path}\n\n"
                              "This was just a test - your real data is unchanged.")

# Create and run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = WorkoutTimer(root)
    root.mainloop()