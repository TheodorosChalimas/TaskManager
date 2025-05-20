# To-Do List Application

A themeable, and animated To-Do List desktop app built with Python and Tkinter.
Recomended use: Setup bash script to run with key binding

## Features

- **Add, edit, delete, and reorder tasks**
- **Set priorities and due dates**
- **Mark tasks as completed**
- **Undo delete**
- **Keyboard navigation and shortcuts**
- **Multiple color themes (Light, Dark, Purple-Green)**
- **Animated UI transitions**
- **Auto-saving and window size persistence**

## Keyboard Shortcuts

| Shortcut           | Action                        |
|--------------------|------------------------------|
| Ctrl+N             | Focus task entry              |
| Ctrl+Enter         | Add task                      |
| Ctrl+Z             | Undo delete                   |
| Ctrl+Q             | Quit application              |
| Ctrl+T             | Toggle theme                  |
| Up/Down            | Select previous/next task     |
| Delete             | Delete selected task          |
| Ctrl+Space         | Toggle completion             |
| Enter              | Edit selected task            |
| Ctrl+Left/Right    | Animated matrix transition    |

## Project Structure

```
main.py               # Entry point
task_manager.py       # Main UI and logic
animations.py         # UI animations
logging_utils/        # TaskManager and logging
```

## Customization

- **Themes:** Easily switch or add new color themes in `task_manager.py`.
- **Animations:** Edit or add new animations in `animations.py`.

## License

MIT License

---
