import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading

# Function to run the script in a separate thread
def run_script(script_name):
    # Update the output box to show that the script is running
    output_box.insert(tk.END, f"Running {script_name}...\n")
    output_box.see(tk.END)
    
    # Call the script using subprocess
    subprocess.run(["python", script_name], check=True)
    
    # Update the output box after the script has finished running
    output_box.insert(tk.END, f"{script_name} finished.\n")
    output_box.see(tk.END)

# Function to create a thread for running a script
def create_thread(script_name):
    thread = threading.Thread(target=run_script, args=(script_name,))
    thread.start()

# Set up the GUI
root = tk.Tk()
root.title("Script Runner")

# Create the output box
output_box = scrolledtext.ScrolledText(root, width=40, height=10)
output_box.grid(row=0, column=0, columnspan=4)

# Create buttons for running scripts
button1 = tk.Button(root, text="Run Script 1", command=lambda: create_thread("1scrape_site.py"))
button1.grid(row=1, column=0)

button2 = tk.Button(root, text="Run Script 2", command=lambda: create_thread("2parse_tables.py"))
button2.grid(row=1, column=1)

button3 = tk.Button(root, text="Run Script 3", command=lambda: create_thread("3analyze.py"))
button3.grid(row=1, column=2)

# Create a close button
close_button = tk.Button(root, text="Close", command=root.destroy)
close_button.grid(row=1, column=3)

root.mainloop()
