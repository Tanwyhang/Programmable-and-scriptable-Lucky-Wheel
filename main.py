import tkinter as tk
import random
import pygame
import math
import time
import sys
from PIL import ImageTk, Image

root = tk.Tk()
root.geometry("600x600")
root.minsize(400, 400)
root.config(bg="black")  # Set background color of the main window



pygame.mixer.init()
spin_sound = pygame.mixer.Sound("assets\\spin_sound.wav")
img = Image.open("assets\\logo.png")
r = 100
img = img.resize([r, r])
logo_image = ImageTk.PhotoImage(img)

canvas = tk.Canvas(root, bg="black")


class LuckyWheel:
    def __init__(self, master, win_list, canvas):

        
        # Original colors for segments
        self.base_colors = ["#F5EEDC", "#ECB390"]
        self.highlight_color = "#DD4A48"  # Light color for highlighting

        # Brightened version of the original colors
        self.brightened_colors = [self.brighten_color(c, self.highlight_color) for c in self.base_colors]

        self.delay = 0

        # Canvas to draw the wheel
        self.canvas = canvas  # Set background color of the canvas

        # Winner label
        self.winner_label = tk.Label(self.canvas, text="Press [space]", font=("Arial", 35), bg="black", fg=self.highlight_color)
        self.winner_label.pack(pady=10)  # Add some padding to position it nicely
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.segments = 20
        self.angle_per_segment = 360 / self.segments
        self.current_angle = 0
        self.trail_segments = []  # Store the previous highlighted segments for trail effect
        self.master = master

        # Bind the resizing event
        self.master.bind("<Configure>", self.on_resize)

        # Bind the spacebar key to the spin function
        self.master.bind("<space>", self.spin_wheel)

        # Metadata

        self.current_segment = 0
        self.spinning = False
        self.first_spin = True

        # Preset list
        self.winner_preset_list = win_list
        for i in range(len(self.winner_preset_list)):
            self.winner_preset_list[i] -= 1
        

        #self.hide()

    def on_resize(self, event):
        """Adjust the wheel when the window is resized."""
        self.canvas.config(width=event.width, height=event.height)
        self.draw_wheel()

    def draw_wheel(self):
        try:
            self.canvas.delete("all")
        except:
            sys.exit()

        # Calculate radius and center based on current canvas size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.radius = min(canvas_width, canvas_height) // 2 - 130
        self.center_x = canvas_width // 2
        self.center_y = int(canvas_height * 0.5)

        for i in range(self.segments):
            start_angle = i * self.angle_per_segment + self.current_angle
            original_color = self.base_colors[i % len(self.base_colors)]

            # Apply the trail effect: previous segments use the dimmed brightened color
            if i in self.trail_segments:
                trail_index = self.trail_segments.index(i)
                dim_factor = min(0.99, 1 - (0.99 ** (trail_index + 1)))
                color = self.apply_dim(self.brightened_colors[i % len(self.base_colors)], dim_factor, highlight_color=self.highlight_color)
            else:
                color = original_color

            if len(self.trail_segments) > 0 and i == self.trail_segments[-1]:  # Highlight the current segment
                color = self.highlight_color

            self.canvas.create_arc(
                self.center_x - self.radius, self.center_y - self.radius,
                self.center_x + self.radius, self.center_y + self.radius,
                start=start_angle, extent=self.angle_per_segment, fill=color
            )

            # Calculate position for number
            text_angle = start_angle + self.angle_per_segment / 2
            x = self.center_x + (self.radius + 30) * math.cos(math.radians(text_angle))
            y = self.center_y - (self.radius + 30) * math.sin(math.radians(text_angle))

            text_size = 0

            if i == self.current_segment and self.spinning:
                text_size = int(self.radius * 0.05 * 2)
                text_color = self.highlight_color
                self.winner_label.config(text=str(self.current_segment + 1))  # Clear the winner label
            else:
                text_color = "gray"
                text_size = int(self.radius * 0.05 * 1.5)

            if i == self.current_segment and not self.first_spin:
                text_color = self.highlight_color
                text_size = int(self.radius * 0.05 * 3)

            self.canvas.create_image(self.center_x, self.center_y, image=logo_image)
            self.canvas.create_text(x, y, text=str(i + 1), font=("Arial", text_size), fill=text_color)

    def brighten_color(self, color, highlight_color):
        """Brighten the color."""
        color = color.lstrip('#')
        highlight_color = highlight_color.lstrip("#")

        r = (int(color[0:2], 16) + int(highlight_color[0:2], 16)) // 2
        g = (int(color[2:4], 16) + int(highlight_color[2:4], 16)) // 2
        b = (int(color[4:6], 16) + int(highlight_color[4:6], 16)) // 2

        return f'#{r:02x}{g:02x}{b:02x}'

    def apply_dim(self, color, dim_factor, highlight_color):
        """Dim the color by the given factor."""
        color = color.lstrip('#')
        highlight_color = highlight_color.lstrip("#")

        r = int((int(color[0:2], 16) + int(highlight_color[0:2], 16)) * dim_factor / 2 + 30)
        g = int((int(color[2:4], 16) + int(highlight_color[2:4], 16)) * dim_factor / 2 + 30)
        b = int((int(color[4:6], 16) + int(highlight_color[4:6], 16)) * dim_factor / 2 + 30)

        return f'#{r:02x}{g:02x}{b:02x}'

    def spin_wheel(self, event=None):
        global play_count, canvas
        if not self.spinning:
            self.spinning = True
            self.winner_label.config(text=str(self.current_segment + 1))  # Clear the winner label

            # Determine the winning segment
            self.winning_segment = 0
            if play_count < len(self.winner_preset_list):
                if self.winner_preset_list[play_count] > 0:
                    self.winning_segment = self.winner_preset_list[play_count]
            else:
                self.winning_segment = random.randint(0, self.segments - 1)

            spin_count = 0
            rounds = 5  # Number of initial fast rounds
            self.delay = 0.01  # Initial delay for fast speed
            total_spins = self.segments * rounds  # Total spins for the initial fast rounds
            total_spins += self.winning_segment  # Add spins to reach winning segment

            while spin_count < total_spins:
                self.current_segment = (spin_count % self.segments)
                self.trail_segments.append(self.current_segment)

                if len(self.trail_segments) > self.segments:  # Limit the trail length
                    self.trail_segments.pop(0)

                self.draw_wheel()
                self.master.update()
                time.sleep(self.delay)

                # Gradually slow down the spin after the fast rounds
                self.delay = 1 / ((total_spins - spin_count) ** 1.5) + (1 / 60)

                trail_remove = min(5, (self.delay / 0.02))
                for i in range(int(trail_remove)):
                    if self.trail_segments:
                        self.trail_segments.pop(0)

                spin_count += 1
                spin_sound.play()

            # Finalize by highlighting the winning segment
            self.trail_segments = [self.winning_segment]  # Eliminate all trails
            self.current_segment = self.winning_segment
            self.draw_wheel()
            
            play_count += 1
            print(f"playcount : {play_count}")

            # Update the winner label with the winning segment
            self.winner_label.config(text=f"Item: {self.winning_segment + 1}")
            self.spinning = False



            self.canvas.pack_forget()
            NumberShuffler(root, number_shuffler_win_list, canvas)
            return 0

        self.first_spin = False

        #confirmation here

        #hide, go back to number shuffling
        
    
    def hide(self):
        self.canvas.pack_forget()

    
    def show(self):
        self.canvas.pack(fill=tk.BOTH, expand=True)


class NumberShuffler:

    def __init__(self, master, win_list, canvas):

        self.master = master
        self.master.title("Lucky Wheel")

        # Make the window resizable

        # Canvas to draw the wheel
        self.canvas = canvas
        self.canvas.pack(padx=60, pady=60)

        
        self.preset_list = win_list
        self.chosen_number = None
        self.running = False
        self.delay = 1 / 30  # 30Hz -> 1/30 seconds

        self.label = tk.Label(self.canvas, text="0", font=("Arial", 100), bg="black", fg="white", borderwidth=0)
        self.label.pack()

        self.prompt_start_stop = tk.Label(self.canvas, text="START", font=("Arial", 25), bg="black", fg="white", borderwidth=0)
        self.prompt_start_stop.pack()

        self.button = tk.Button(self.canvas, image=logo_image, command=self.start, borderwidth=0, activebackground="black", bg="black")
        self.button.pack(pady=10)

        # metadata
        self.play_count = play_count
        self.win_list = win_list


    def start(self):
        if not self.running:
            self.running = True
            self.button.config(command=self.stop)
            self.prompt_start_stop.config(text="STOP")
            self.shuffle_numbers()
        else:
            self.stop()

    def shuffle_numbers(self):
        if self.running:
            self.chosen_number = random.choice(self.win_list)
            self.label.config(text=str(self.chosen_number))
            self.master.after(int(self.delay * 1000), self.shuffle_numbers)

    def stop(self):
        global play_count
        self.running = False
        self.label.config(text=self.win_list[play_count])
        self.button.config(text="Start", command=self.start)
        self.prompt_start_stop.config(text="START")


        clear_screen()
        canvas = tk.Canvas(root, bg="black")
        LuckyWheel(root, lucky_wheel_win_list, canvas)
        return 0
    

def clear_screen():
    global canvas
    canvas.destroy()
    canvas = None
    canvas = tk.Canvas(root, bg="black")
        
#setup
play_count = 0

# winners setup
number_shuffler_win_list = [1,2,3,4,5]
lucky_wheel_win_list     = [6,7,8,9,1]




NumberShuffler(root, number_shuffler_win_list, canvas)
    

if __name__ == "__main__":
    root.mainloop()


"""
A callback is a function that is passed as an 
argument to another function or object, which 
is then called at a later time when a specific 
event or condition occurs. It essentially allows 
you to specify a sequence of actions that should
 be performed in response to an event.
 """