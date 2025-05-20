import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from datetime import datetime
from logging_utils.log_handler import TaskManager
from animations import grow_from_center, slide


def blend_colors(color1, color2, ratio=0.25):
    # Blend two hex colors (e.g. "#ff0000" and "#ffffff") by the given ratio
    c1 = [int(color1[i:i+2], 16) for i in (1, 3, 5)]
    c2 = [int(color2[i:i+2], 16) for i in (1, 3, 5)]
    blended = [int(c1[i] * (1 - ratio) + c2[i] * ratio) for i in range(3)]
    return f"#{blended[0]:02x}{blended[1]:02x}{blended[2]:02x}"


class TodoApp:
    # Remove "Edit" and "Delete" columns from columns and widths
    COLUMNS = ["#", "Task", "Priority", "Due", "Added"]
    COL_WIDTHS = [5, 40, 10, 14, 18]

    # Define task priorities and themes
    PRIORITIES = ["Low", "Medium", "High"]
    THEME = {
        "light": {  # Light theme
            "header_bg": "#cccccc",  # Light gray for headers
            "cell_bg": "#ffffff",  # White for cells
            "cell_fg": "#000000",  # Black text
            "done_fg": "#888888",  # Gray for completed tasks
            "overdue_bg": "#ffe0e0",  # Light red for overdue tasks
            "alt_row": "#f9f9f9",  # Slightly off-white for alternating rows
            "button_bg": "#f0f0f0",  # Light gray for buttons
            "button_fg": "#000000",  # Black button text
            "main_bg": "#ffffff"  # White for the main background
        },
        "dark": {  # Dark theme
            "header_bg": "#333333",  # Dark gray for headers
            "cell_bg": "#222222",  # Darker gray for cells
            "cell_fg": "#eeeeee",  # Light gray text
            "done_fg": "#888888",  # Gray for completed tasks
            "overdue_bg": "#662222",  # Dark red for overdue tasks
            "alt_row": "#2a2a2a",  # Slightly lighter gray for alternating rows
            "button_bg": "#444444",  # Dark gray for buttons
            "button_fg": "#eeeeee",  # Light gray button text
            "main_bg": "#181818"  # Very dark gray for the main background
        },
        "purple_green": {  # Purple and green theme
            "header_bg": "#4b0082",  # Purple
            "cell_bg": "#2e2b55",  # Dark purple
            "cell_fg": "#00ff00",  # Bright green for text
            "done_fg": "#888888",  # Gray for completed tasks
            "overdue_bg": "#662222",  # Dark red for overdue tasks
            "alt_row": "#3a335c",  # Slightly lighter purple for alternating rows
            "button_bg": "#5a2d82",  # Purple for buttons
            "button_fg": "#d4ffdd",  # Light green for button text
            "main_bg": "#1e1b3a"  # Very dark purple for the main background
        }
    }

    def __init__(self, root):
        # Initialize the TodoApp
        self.root = root
        self.manager = TaskManager()
        self.theme_mode = "purple_green"  # Default theme
        self.columns = self.COLUMNS
        self.col_widths = self.COL_WIDTHS
        self.datetime_format = "%Y-%m-%d %H:%M:%S"
        self.due_format = "%Y-%m-%d"
        self.style = ttk.Style()
        self.selected_row = 0  # Track selected row
        self._setup_ui()
        self.display_tasks()

        # Keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self.task_entry.focus_set())
        self.root.bind("<Control-Return>", lambda e: self.add_task())
        self.root.bind("<Control-z>", lambda e: self.undo_delete())
        self.root.bind("<Control-q>", lambda e: self.on_close())
        self.root.bind("<Control-t>", lambda e: self.toggle_theme())
        self.root.bind("<Up>", self.select_prev_row)
        self.root.bind("<Down>", self.select_next_row)
        self.root.bind("<Delete>", self.delete_selected_row)
        self.root.bind("<Control-space>", lambda e: self.toggle_selected_complete())  # Ctrl+Space to toggle completion
        self.root.bind("<Return>", lambda e: self.edit_selected_row())
        self.root.bind(
            "<Control-Left>",
            lambda e: slide(
                self.matrix_container,
                direction="left",
                on_finish=lambda: self.matrix_container.pack(expand=True, fill=tk.BOTH)
            )
        )
        self.root.bind(
            "<Control-Right>",
            lambda e: slide(
                self.matrix_container,
                direction="right",
                on_finish=lambda: self.matrix_container.pack(expand=True, fill=tk.BOTH)
            )
        )

    def _apply_theme(self):
        # Apply the current theme to the UI
        theme = self.THEME[self.theme_mode]
        self.root.configure(bg=theme["main_bg"])
        self.tasks_frame.configure(bg=theme["cell_bg"])
        self.canvas.configure(bg=theme["main_bg"])
        self.datetime_label.configure(bg=theme["main_bg"], fg=theme["cell_fg"])
        self.task_entry.configure(background=theme["cell_bg"], foreground=theme["cell_fg"])
        self.button_frame.configure(bg=theme["main_bg"])
        self.style.configure("TButton", background=theme["button_bg"], foreground=theme["button_fg"])
        self.style.configure("TEntry", fieldbackground=theme["cell_bg"], foreground=theme["cell_fg"])
        self.style.map("TButton", background=[("active", theme["header_bg"])])

    def _setup_ui(self):
        # Set up the user interface
        self.root.title("To-Do List")
        geometry = self.manager.load_window_cfg()
        self.root.geometry(geometry if geometry else "1000x600")

        self.main_container = tk.Frame(self.root, bg=self.THEME[self.theme_mode]["main_bg"])
        self.main_container.pack(expand=True, fill=tk.BOTH)

        # Datetime label
        self.datetime_label = tk.Label(self.main_container, text="", font=("Segoe UI", 12, "bold"),
                                       bg=self.THEME[self.theme_mode]["main_bg"],
                                       fg=self.THEME[self.theme_mode]["cell_fg"])
        self.datetime_label.pack(pady=10)
        self._update_datetime()

        # Task matrix with scrollbar
        self.matrix_container = tk.Frame(self.main_container, bg=self.THEME[self.theme_mode]["main_bg"])
        self.canvas = tk.Canvas(self.matrix_container, highlightthickness=0, bg=self.THEME[self.theme_mode]["main_bg"])
        self.scrollbar = ttk.Scrollbar(self.matrix_container, orient="vertical", command=self.canvas.yview)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tasks_frame = tk.Frame(self.canvas, bg=self.THEME[self.theme_mode]["cell_bg"])
        self.window_id = self.canvas.create_window((0, 0), window=self.tasks_frame, anchor="n")
        self.matrix_container.pack(expand=True, fill=tk.BOTH)

        # Now animate the container (after it has content)
        grow_from_center(
            self.matrix_container,
            duration=600,
            steps=60,
            on_finish=lambda: self.matrix_container.pack(expand=True, fill=tk.BOTH)
        )

        # Center the matrix
        def center_matrix(event=None):
            canvas_width = self.canvas.winfo_width()
            frame_width = self.tasks_frame.winfo_reqwidth()
            x = max((canvas_width - frame_width) // 2, 0)
            self.canvas.coords(self.window_id, x, 0)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.tasks_frame.bind("<Configure>", center_matrix)
        self.canvas.bind("<Configure>", center_matrix)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Input section
        self.button_frame = tk.Frame(self.main_container, bg=self.THEME[self.theme_mode]["main_bg"])
        self.button_frame.pack(pady=5)
        self.task_entry = ttk.Entry(self.button_frame, width=40)
        self.task_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Add Task (Ctrl+Enter)", command=self.add_task).pack(side=tk.LEFT, padx=5)
        # Removed Undo Delete, Close, and Theme toggle buttons

        self.task_entry.focus_set()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self._apply_theme()

        self.main_container.pack_forget()
        grow_from_center(
            self.main_container,
            duration=500,
            steps=20,
            on_finish=lambda: self.main_container.pack(expand=True, fill=tk.BOTH)
        )

    def _update_datetime(self):
        # Update the datetime label every second
        now = datetime.now().strftime(self.datetime_format)
        self.datetime_label.config(text=f"Current date and time: {now}")
        self.root.after(1000, self._update_datetime)

    def toggle_theme(self, event=None):
        # Toggle between themes
        if self.theme_mode == "light":
            self.theme_mode = "dark"
        elif self.theme_mode == "dark":
            self.theme_mode = "purple_green"
        else:
            self.theme_mode = "light"
        self._apply_theme()
        self.display_tasks()

    def add_task(self, event=None):
        # Add a new task
        desc = self.task_entry.get().strip()
        if not desc:
            return
        priority = "High"  # Default priority
        due_date = datetime.now().strftime(self.due_format)  # Default due date
        timestamp = datetime.now().strftime(self.datetime_format)
        self.manager.add_task(desc, timestamp, priority, due_date)
        self.task_entry.delete(0, tk.END)
        self.display_tasks()
        self.task_entry.focus_set()

    def undo_delete(self, event=None):
        # Undo the last deleted task
        self.manager.undo_delete()
        self.display_tasks()

    def edit_task(self, idx):
        # Edit an existing task
        task = self.manager.tasks[idx]
        task_count = len(self.manager.tasks)

        # Ask for new position
        new_pos = simpledialog.askinteger(
            "Edit Task Position", f"Enter new position for this task (1-{task_count}):",
            initialvalue=idx + 1, minvalue=1, maxvalue=task_count, parent=self.root
        )
        if new_pos is None:
            return

        # Ask for new description
        new_desc = simpledialog.askstring(
            "Edit Task", "Task description:", initialvalue=task["desc"], parent=self.root
        )
        if new_desc is None:
            return

        # Ask for new priority
        new_priority = simpledialog.askstring(
            "Edit Priority", f"Enter new priority ({', '.join(self.PRIORITIES)}):",
            initialvalue=task["priority"], parent=self.root
        )
        if new_priority is None or new_priority not in self.PRIORITIES:
            new_priority = task["priority"]

        # Ask for new due date
        new_due = simpledialog.askstring(
            "Edit Due Date", "Due date (YYYY-MM-DD):", initialvalue=task["due_date"], parent=self.root
        )
        if new_due is None:
            new_due = task["due_date"]
        else:
            try:
                datetime.strptime(new_due, self.due_format)
            except ValueError:
                messagebox.showerror("Invalid Date", "Due date must be YYYY-MM-DD")
                return

        # Update task fields
        self.manager.update_task(idx, desc=new_desc, priority=new_priority, due_date=new_due)

        # Move task if position changed
        if new_pos != idx + 1:
            task = self.manager.tasks.pop(idx)
            self.manager.tasks.insert(new_pos - 1, task)
            self.manager.save_tasks()
            self.selected_row = new_pos - 1
        else:
            self.selected_row = idx

        self.display_tasks()

    def toggle_complete(self, idx):
        # Toggle the completion status of a task
        self.manager.toggle_complete(idx)
        self.display_tasks()

    def confirm_delete(self, idx):
        # Confirm and delete a task
        if messagebox.askyesno("Delete Task", "Are you sure you want to delete this task?"):
            self.manager.delete_task(idx)
            self.display_tasks()

    def select_prev_row(self, event=None):
        # Select the previous row
        if self.manager.tasks:
            self.selected_row = max(0, self.selected_row - 1)
            self.display_tasks()

    def select_next_row(self, event=None):
        # Select the next row
        if self.manager.tasks:
            self.selected_row = min(len(self.manager.tasks) - 1, self.selected_row + 1)
            self.display_tasks()

    def edit_selected_row(self, event=None):
        # Edit the currently selected row
        if self.manager.tasks:
            self.edit_task(self.selected_row)

    def delete_selected_row(self, event=None):
        # Delete the currently selected row
        if self.manager.tasks:
            self.confirm_delete(self.selected_row)

    def toggle_selected_complete(self, event=None):
        # Toggle the completion status of the selected row
        if self.manager.tasks:
            self.toggle_complete(self.selected_row)

    def display_tasks(self):
        # Display all tasks in the matrix
        theme = self.THEME[self.theme_mode]
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()

        # Header
        for col_idx, col_name in enumerate(self.columns):
            tk.Label(
                self.tasks_frame, text=col_name, borderwidth=1, relief="solid",
                width=self.col_widths[col_idx], bg=theme["header_bg"], fg=theme["cell_fg"],
                font=("Segoe UI", 11, "bold"), pady=4
            ).grid(row=0, column=col_idx, sticky="nsew", padx=2, pady=2)

        now = datetime.now()
        for idx, task in enumerate(self.manager.tasks):
            desc = task.get("desc", "")
            timestamp = task.get("timestamp", "")
            completed = task.get("completed", False)
            priority = task.get("priority", "Medium")
            due_date = task.get("due_date", "")
            try:
                due_dt = datetime.strptime(due_date, self.due_format)
                overdue = not completed and due_dt < now
            except Exception:
                overdue = False

            fg = theme["done_fg"] if completed else theme["cell_fg"]
            row_bg = theme["alt_row"] if idx % 2 == 0 else theme["cell_bg"]
            bg = theme["overdue_bg"] if overdue else row_bg

            # Slightly tint the background based on priority (if not overdue or selected)
            if not overdue and idx != self.selected_row:
                if priority == "High":
                    bg = blend_colors(row_bg, "#ff0000", ratio=0.18)
                elif priority == "Low":
                    bg = blend_colors(row_bg, "#00ff00", ratio=0.18)
                elif priority == "Medium":
                    bg = blend_colors(row_bg, "#0000ff", ratio=0.18)

            if idx == self.selected_row:
                bg = "#3399ff"
                fg = "#ffffff"

            # Index
            idx_lbl = tk.Label(self.tasks_frame, text=str(idx + 1), borderwidth=1, relief="solid",
                               width=self.col_widths[0], bg=bg, fg=fg, padx=4, pady=2)
            idx_lbl.grid(row=idx + 1, column=0, sticky="nsew")
            idx_lbl.bind("<Double-Button-1>", lambda e, i=idx: self.move_task(i))

            # Description
            desc_lbl = tk.Label(self.tasks_frame, text=desc, borderwidth=1, relief="solid",
                                width=self.col_widths[1], bg=bg, fg=fg, anchor="w", padx=4, pady=2,
                                font=("Segoe UI", 10, "overstrike" if completed else "normal"))
            desc_lbl.grid(row=idx + 1, column=1, sticky="nsew")
            desc_lbl.bind("<Double-Button-1>", lambda e, i=idx: self.edit_task(i))

            # Priority
            tk.Label(self.tasks_frame, text=priority, borderwidth=1, relief="solid",
                     width=self.col_widths[2], bg=bg, fg=fg, padx=4, pady=2).grid(row=idx + 1, column=2, sticky="nsew")

            # Due date
            due_bg = theme["overdue_bg"] if overdue else bg
            tk.Label(self.tasks_frame, text=due_date, borderwidth=1, relief="solid",
                     width=self.col_widths[3], bg=due_bg, fg=fg, padx=4, pady=2).grid(row=idx + 1, column=3, sticky="nsew")

            # Added
            tk.Label(self.tasks_frame, text=timestamp, borderwidth=1, relief="solid",
                     width=self.col_widths[4], bg=bg, fg=fg, padx=4, pady=2).grid(row=idx + 1, column=4, sticky="nsew")

        # Make columns expand
        for col in range(len(self.columns)):
            self.tasks_frame.grid_columnconfigure(col, weight=1)

    def move_task(self, idx):
        # Move a task to a new position
        task_count = len(self.manager.tasks)
        new_pos = simpledialog.askinteger(
            "Move Task", f"Enter new position for this task (1-{task_count}):",
            initialvalue=idx + 1, minvalue=1, maxvalue=task_count, parent=self.root
        )
        if new_pos is None or new_pos == idx + 1:
            return
        task = self.manager.tasks.pop(idx)
        self.manager.tasks.insert(new_pos - 1, task)
        self.manager.save_tasks()
        self.selected_row = new_pos - 1
        self.display_tasks()

    def sort_by_index(self, event=None):
        # Sort tasks by index
        self.manager.tasks.reverse()
        self.manager.save_tasks()
        self.selected_row = 0
        self.display_tasks()

    def on_close(self, event=None):
        # Handle application close
        self.manager.save_window_cfg(self.root.geometry())
        self.root.destroy()


def open_todo_window():
    # Open the To-Do List application
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()