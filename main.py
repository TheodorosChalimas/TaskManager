from task_manager import open_todo_window

if __name__ == "__main__":
    try:
        open_todo_window()
    except Exception as e:
        print(f"An error occurred: {e}")