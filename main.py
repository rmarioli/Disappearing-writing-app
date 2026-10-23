from tkinter import *
from tkinter import ttk, messagebox
import string  # Import string module for letter checking

BEIGE = "#F1F7D4"
RED = "#9FCBAD"
GREEN = "#6EADBC"
YELLOW = "#4A4466"
FONT_NAME = "Courier"
goal_op = ""
selected_goal = ""
timer_started = False
timer_id = None
timer_run_out = None
lbl_goal_desc = None
progress_bar = None
words_counter = 0
reset_btn = None
update_after_id = None  #
saved_radio_value = None  # Store the radio button selection
saved_goal_value = None  # Store the listbox selection


# Function
def radio_used(event=None):
    global goal_op, saved_radio_value
    if radio_state.get() == 1:
        options = [1, 2, 3]
        goal_op = "minutes"
    else:
        options = [10, 150, 200]  # qwerty
        goal_op = "words"

    saved_radio_value = radio_state.get()

    listbox.delete(0, END)

    for item in options:
        listbox.insert(options.index(item), item)


def listbox_used(event):
    global selected_goal, saved_goal_value
    # Gets current selection from listbox
    selected_goal = listbox.get(listbox.curselection())
    saved_goal_value = selected_goal
    btn_start.configure(state="normal")


def start_game():
    global selected_goal, goal_op, lbl_goal_desc, timer_id, timer_run_out, progress_bar, words_counter, reset_btn, timer_started

    words_counter = 0

    # Hide everything
    for widget in stats_frame.winfo_children():
        widget.grid_remove()
    btn_start.grid_remove()

    # Enable and focus the text_input
    text_input.configure(state="normal")
    text_input.delete("1.0", END)
    text_input.focus()

    # Create and show the goal label above text_input
    lbl_goal_desc = Label(window, text=f"Your goal: {selected_goal} {goal_op}", font=(FONT_NAME, 14, "bold"), bg=BEIGE,
                          fg=YELLOW)
    lbl_goal_desc.grid(row=0, column=0, columnspan=2, pady=10)

    # Create reset button
    reset_btn = Button(window, text="Reset", command=reset_game, bg=RED, font=(FONT_NAME, 10, "bold"))
    reset_btn.grid(row=1, column=0, columnspan=2, pady=10)

    # Create load bar
    progress_bar = ttk.Progressbar(window, orient="horizontal", length=200, mode="determinate")
    progress_bar.grid(row=2, column=0, columnspan=2)

    # Set timers
    timer_run_out = 7
    if goal_op == "minutes":
        timer_id = selected_goal * 6  # qwerty
    else:
        timer_id = selected_goal

    timer_started = True

    # Start the timer or word counter
    update_timer()

    # Store references to these new widgets so reset can access them
    window.lbl_goal_desc = lbl_goal_desc
    window.reset_btn = reset_btn
    window.progress_bar = progress_bar


def reset_game():
    global selected_goal, goal_op, lbl_goal_desc, progress_bar, words_counter, update_after_id, timer_started  # /////////////////// Fixed: removed duplicate global

    if update_after_id is not None:  # Cancel after() callback
        window.after_cancel(update_after_id)
        update_after_id = None

    # Clear the text input
    text_input.delete("1.0", END)
    text_input.configure(state="disabled")

    if hasattr(window, 'lbl_goal_desc'):
        window.lbl_goal_desc.destroy()
    if hasattr(window, 'reset_btn'):
        window.reset_btn.destroy()
    if hasattr(window, 'progress_bar') and window.progress_bar:
        window.progress_bar.destroy()

    # Show all again
    for widget in stats_frame.winfo_children():
        widget.grid()
    btn_start.grid()

    # RESTORE THE SAVED SELECTIONS
    # Restore radio button selection
    if saved_radio_value is not None:
        radio_state.set(saved_radio_value)
        # Manually trigger radio_used to populate the listbox with correct options
        if saved_radio_value == 1:
            options = [1, 2, 3]
            goal_op = "minutes"
        else:
            options = [10, 150, 200]
            goal_op = "words"

        listbox.delete(0, END)
        for item in options:
            listbox.insert(options.index(item), item)

        # Restore listbox selection
        if saved_goal_value is not None:
            # Find the index of the saved goal in the listbox
            listbox_items = listbox.get(0, END)
            if saved_goal_value in listbox_items:
                goal_index = listbox_items.index(saved_goal_value)
                listbox.selection_set(goal_index)
                selected_goal = saved_goal_value
                btn_start.configure(state="normal")
    else:
        # If no saved values, reset normally
        radio_state.set(0)
        selected_goal = ""
        goal_op = ""

    # Reset global variables - MOVED THESE INSIDE THE else BLOCK OR REMOVED DUPLICATES  #///////////////////
    words_counter = 0
    timer_started = False

    # Unbind all letter keys when resetting
    for letter in string.ascii_lowercase:
        window.unbind(letter)

    for letter in string.ascii_uppercase:
        window.unbind(letter)

    window.unbind("<space>")
    bind_letter_keys()  # Rebind letter keys

    text_input.configure(state="disabled")
    btn_start.configure(state="disabled")


def update_timer():
    global timer_id, timer_started, timer_run_out, update_after_id, words_counter

    if not timer_started:
        pass
        # return

    if goal_op == "minutes":
        if timer_run_out > 0 and timer_id > 0:
            timer_run_out -= 1
            progress_bar['value'] = ((8 - timer_run_out) / 8) * 100
            lbl_goal_desc.config(text=f"Time left: {timer_id}/{selected_goal * 60}")
            timer_id -= 1
            update_after_id = window.after(1000, update_timer)
        elif timer_id <= 0:
            goal_over()
        else:
            time_over_bar()
    else:
        if timer_run_out > 0:
            timer_run_out -= 1
            progress_bar['value'] = ((8 - timer_run_out) / 8) * 100
            lbl_goal_desc.config(text=f"Words typed: {words_counter}/{selected_goal}")
            update_after_id = window.after(1000, update_timer)
            if words_counter >= int(selected_goal):
                goal_over()
        else:
            time_over_bar()


def time_over_bar():
    global timer_started, timer_id, timer_run_out, progress_bar

    # Stop timer completely
    timer_id = None
    timer_run_out = None

    # Show losing popup
    messagebox.showinfo(
        title="You Lost",
        message="You stopped typing for too long!\nGame Over."
    )

    # Reset timer value
    window.progress_bar.destroy()
    text_input.delete("1.0", END)

    reset_game()


def goal_over():
    global timer_id, timer_run_out, progress_bar, lbl_goal_desc

    lbl_goal_desc.config(text="GOAL COMPLETED! CONGRATULATIONS!")
    timer_id = None
    timer_run_out = None
    window.progress_bar.destroy()


def on_key(event):
    global timer_run_out, words_counter, timer_started

    # Start timer when any letter is pressed
    if event.keysym.lower() in string.ascii_lowercase:
        if not timer_started:
            timer_started = True
            update_timer()

        # Reset inactivity timer
        if timer_run_out is not None:
            timer_run_out = 7

            if progress_bar:
                progress_bar['value'] = 0

    # Count words ONLY when space is pressed
    if event.keysym == "space":
        words_counter += 1

        if goal_op == "words" and lbl_goal_desc:
            lbl_goal_desc.config(
                text=f"Words typed: {words_counter}/{selected_goal}"
            )

        # Check if goal reached
        if words_counter >= int(selected_goal) and goal_op == "words":
            goal_over()


# New function to bind all letter keys
def bind_letter_keys():
    for letter in string.ascii_lowercase:
        window.bind(letter, on_key)

    for letter in string.ascii_uppercase:
        window.bind(letter, on_key)

    # Bind spacebar
    window.bind("<space>", on_key)


window = Tk()
window.title("APP PIOLAZA")
window.config(padx=50, pady=25, bg=BEIGE)

stats_frame = Frame(window, bg=BEIGE)
stats_frame.grid(column=0, row=0)

radio_state = IntVar()
radiobutton1 = Radiobutton(stats_frame, text="Minutes", value=1, variable=radio_state, command=radio_used, bg=BEIGE)
radiobutton2 = Radiobutton(stats_frame, text="Words", value=2, variable=radio_state, command=radio_used, bg=BEIGE)
radiobutton1.grid(row=0, column=0)
radiobutton2.grid(row=1, column=0)

# Main Listbox
listbox = Listbox(stats_frame, height=3)
listbox.bind("<<ListboxSelect>>", listbox_used)
listbox.grid(row=0, column=1, rowspan=2)

# calls action() when pressed
btn_start = Button(text="Start", command=start_game)
btn_start.grid(row=0, column=1, columnspan=1)
btn_start.configure(state="disabled")

# width is in characters, height is in lines
text_input = Text(window, width=100, height=40, wrap=WORD, bg=BEIGE)
text_input.grid(row=3, column=0, columnspan=2, pady=0)
text_input.configure(state="disabled")

bind_letter_keys()  # Bind all letter keys at startup

# Add an info label to inform the user
info_label = Label(window, text="Press ANY letter key to reset timer or count words",
                   font=(FONT_NAME, 10, "bold"), bg=BEIGE, fg=YELLOW)
info_label.grid(row=4, column=0, columnspan=2, pady=5)

window.mainloop()