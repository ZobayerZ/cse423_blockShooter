from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
import math

# Window dimensions
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 800

# Global score variables
rocket1_score = 0
rocket2_score = 0

rocket1_collisions = 0
rocket2_collisions = 0
game_over = False
winner = None
freeze = False

# Zigzag movement parameters
ZIGZAG_STEP = 4  # Horizontal step size for zigzag
ZIGZAG_INTERVAL = 5  # Number of vertical steps before changing direction

# Shield variables for both rockets
rocket1_shield_active = False
rocket2_shield_active = False

#shield_flag
rocket1_shield_flag = True
rocket2_shield_flag = True

rocket1_shield_timer = 0  # Timer for Rocket 1's shield
rocket2_shield_timer = 0  # Timer for Rocket 2's shield

SHIELD_DURATION = 10  # Shield duration in seconds


# Define new firing intervals for both rockets
ROCKET1_FIRE_INTERVAL = 3000  # 7 seconds for Rocket 1
ROCKET2_FIRE_INTERVAL = 3000  # 7 seconds for Rocket 2

ROCKET1_FIRE_INTERVAL_FLAG_5 = True
ROCKET2_FIRE_INTERVAL_FLAG_5 = True
ROCKET1_FIRE_INTERVAL_FLAG_10 = True
ROCKET2_FIRE_INTERVAL_FLAG_10 = True

########################################################################################################################

# Function to draw a line using MPL
### Algorithm to convert from a different zone to zone 0
def other_zone_to_zone0(x, y, zone):
    co_ordinates_zone = {
        0: (x, y), 1: (y, x), 2: (y, -x),
        3: (-x, y), 4: (-x, -y), 5: (-y, -x),
        6: (-y, x), 7: (x, -y)
    }
    return co_ordinates_zone[zone]

### Algorithm to convert from zone 0 to others
def zone0_to_other_zone(x, y, zone):
    co_ordinates_zone = {
        0: (x, y), 1: (y, x), 2: (-y, x), 3: (-x, y),
        4: (-x, -y), 5: (-y, -x), 6: (y, -x),
        7: (x, -y)
    }
    return co_ordinates_zone[zone]

def mpl_mid_point_line_algrtm(x_1, y_1, x_2, y_2):
    # Calculate deltas
    d_x = x_2 - x_1
    d_y = y_2 - y_1

    # Determine the zone
    def determine_zone(d_x, d_y):
        if abs(d_x) > abs(d_y):
            if d_x >= 0:
                return 0 if d_y >= 0 else 7
            else:
                return 3 if d_y >= 0 else 4
        else:
            if d_y >= 0:
                return 1 if d_x >= 0 else 2
            else:
                return 6 if d_x >= 0 else 5

    zone = determine_zone(d_x, d_y)

    # Convert to Zone 0
    x_1, y_1 = other_zone_to_zone0(x_1, y_1, zone)
    x_2, y_2 = other_zone_to_zone0(x_2, y_2, zone)

    # Recalculate deltas in Zone 0
    d_x = x_2 - x_1
    d_y = y_2 - y_1

    # Initialize decision parameters
    del_init = 2 * d_y - d_x
    del_east = 2 * d_y
    del_NE = 2 * (d_y - d_x)

    # Start plotting
    x, y = x_1, y_1
    plot_point(x, y, zone)

    # Iterate and draw the line
    while x < x_2:
        if del_init <= 0:
            del_init += del_east
        else:
            del_init += del_NE
            y += 1
        x += 1
        plot_point(x, y, zone)


########################################################################################################################

###mid point circle algorithm
def mpc_midpoint_circle_algrthm(radius, cen_x=0, cen_y=0):
    glBegin(GL_POINTS)
    X = 0
    Y = radius
    del_init = 1 - radius
    while Y > X:
        glVertex2f(X + cen_x, Y + cen_y)
        glVertex2f(X + cen_x, -Y + cen_y)
        glVertex2f(-X + cen_x, Y + cen_y)
        glVertex2f(-X + cen_x, -Y + cen_y)
        glVertex2f(Y + cen_x, X + cen_y)
        glVertex2f(Y + cen_x, -X + cen_y)
        glVertex2f(-Y + cen_x, X + cen_y)
        glVertex2f(-Y + cen_x, -X + cen_y)
        if del_init < 0:
            del_init += 2 * X + 3
        else:
            del_init += 2 * X - 2 * Y + 5
            Y -= 1
        X += 1
    glEnd()

########################################################################################################################

### Functions for plotting the points
def plot_point(x, y, zone):
    original_x, original_y = zone0_to_other_zone(x, y, zone)
    glPointSize(2)
    glBegin(GL_POINTS)
    glVertex2f(original_x, original_y)
    glEnd()

########################################################################################################################

# Initial positions of rockets
rocket1_x = -125  # Centered in the left block
rocket2_x = 125   # Centered in the right block
rocket_y = -340   # Same vertical position for both rockets
rocket_radius = 20 #==========================================================================================

# Rocket movement boundaries
LEFT_BLOCK_LIMIT = -250
RIGHT_BLOCK_LIMIT = 0
ROCKET_STEP = 8  # Movement step size

# Function to draw Rocket 1
def draw_rocket_1(base_x, base_y):
    b_w, b_h = 9, 30  # Scaled-down body width and height
    tip_h = 15        # Tip height
    fin_w, fin_h = 4, 8  # Fin width and height
    l_t_h = 18        # W-shaped structure height
    l_t_w = 7         # W-shaped structure width

    if rocket1_shield_active:
        glColor3f(0, 1, 1)  # Cyan color for shield
        mpc_midpoint_circle_algrthm(rocket_radius + 10, base_x, base_y)  # Slightly larger circle

    # Rocket body (Yellow)
    glColor3f(1, 1, 0)
    mpl_mid_point_line_algrtm(base_x - b_w, base_y, base_x - b_w, base_y + b_h)
    mpl_mid_point_line_algrtm(base_x + b_w, base_y, base_x + b_w, base_y + b_h)
    mpl_mid_point_line_algrtm(base_x - b_w, base_y + b_h, base_x + b_w, base_y + b_h)

    # Rocket tip (Red)
    glColor3f(1, 0, 0)
    mpl_mid_point_line_algrtm(base_x - b_w, base_y + b_h, base_x, base_y + b_h + tip_h)
    mpl_mid_point_line_algrtm(base_x + b_w, base_y + b_h, base_x, base_y + b_h + tip_h)

    # Rocket fins (Red)
    glColor3f(1, 0, 0)
    mpl_mid_point_line_algrtm(base_x - b_w, base_y, base_x - b_w - fin_w, base_y - fin_h)
    mpl_mid_point_line_algrtm(base_x + b_w, base_y, base_x + b_w + fin_w, base_y - fin_h)

    # Lower W-shaped structure (Yellow with boundary)
    glColor3f(1, 1, 0)
    mpl_mid_point_line_algrtm(base_x - l_t_w, base_y - fin_h, base_x - l_t_w // 2, base_y - fin_h - l_t_h)
    mpl_mid_point_line_algrtm(base_x - l_t_w // 2, base_y - fin_h - l_t_h, base_x, base_y - fin_h)
    mpl_mid_point_line_algrtm(base_x, base_y - fin_h, base_x + l_t_w // 2, base_y - fin_h - l_t_h)
    mpl_mid_point_line_algrtm(base_x + l_t_w // 2, base_y - fin_h - l_t_h, base_x + l_t_w, base_y - fin_h)
    mpl_mid_point_line_algrtm(base_x - l_t_w, base_y - fin_h, base_x + l_t_w, base_y - fin_h)

# Function to draw Rocket 2
def draw_rocket_2(base_x, base_y):
    b_w, b_h = 9, 30  # Scaled-down body width and height
    tip_h = 15        # Tip height
    fin_w, fin_h = 4, 8  # Fin width and height
    l_t_h = 18        # W-shaped structure height
    l_t_w = 7         # W-shaped structure width

    if rocket2_shield_active:
        glColor3f(0, 1, 1)  # Cyan color for shield
        mpc_midpoint_circle_algrthm(rocket_radius + 10, base_x, base_y)  # Slightly larger circle

    # Rocket body (Blue)
    glColor3f(0, 0, 1)
    mpl_mid_point_line_algrtm(base_x - b_w, base_y, base_x - b_w, base_y + b_h)
    mpl_mid_point_line_algrtm(base_x + b_w, base_y, base_x + b_w, base_y + b_h)
    mpl_mid_point_line_algrtm(base_x - b_w, base_y + b_h, base_x + b_w, base_y + b_h)

    # Rocket tip (Green)
    glColor3f(0, 1, 0)
    mpl_mid_point_line_algrtm(base_x - b_w, base_y + b_h, base_x, base_y + b_h + tip_h)
    mpl_mid_point_line_algrtm(base_x + b_w, base_y + b_h, base_x, base_y + b_h + tip_h)

    # Rocket fins (Blue)
    glColor3f(0, 0, 1)
    mpl_mid_point_line_algrtm(base_x - b_w, base_y, base_x - b_w - fin_w, base_y - fin_h)
    mpl_mid_point_line_algrtm(base_x + b_w, base_y, base_x + b_w + fin_w, base_y - fin_h)

    # Lower W-shaped structure (Green with boundary)
    glColor3f(0, 1, 0)
    mpl_mid_point_line_algrtm(base_x - l_t_w, base_y - fin_h, base_x - l_t_w // 2, base_y - fin_h - l_t_h)
    mpl_mid_point_line_algrtm(base_x - l_t_w // 2, base_y - fin_h - l_t_h, base_x, base_y - fin_h)
    mpl_mid_point_line_algrtm(base_x, base_y - fin_h, base_x + l_t_w // 2, base_y - fin_h - l_t_h)
    mpl_mid_point_line_algrtm(base_x + l_t_w // 2, base_y - fin_h - l_t_h, base_x + l_t_w, base_y - fin_h)
    mpl_mid_point_line_algrtm(base_x - l_t_w, base_y - fin_h, base_x + l_t_w, base_y - fin_h)

########################################################################################################################

# Function to draw the dividing line
def draw_dividing_line():
    glColor3f(1, 1, 1)  # White line
    x = 0  # Vertical line at x = 0
    y_start = -WINDOW_HEIGHT // 2  # Start of the line
    y_end = WINDOW_HEIGHT // 2    # End of the line

    # Use the Mid-Point Line Algorithm to draw the line
    mpl_mid_point_line_algrtm(x, y_start, x, y_end)

########################################################################################################################

# Maximum number of boxes
MAX_BOXES = 3

# Box attributes
boxes = []

# Box movement step
BOX_STEP = 5

# Draw a box using MPL
def draw_box(x, y, size, color):
    glColor3f(*color)
    half_size = size // 2

    mpl_mid_point_line_algrtm(x - half_size, y - half_size, x + half_size, y - half_size)  # Bottom edge
    mpl_mid_point_line_algrtm(x + half_size, y - half_size, x + half_size, y + half_size)  # Right edge
    mpl_mid_point_line_algrtm(x + half_size, y + half_size, x - half_size, y + half_size)  # Top edge
    mpl_mid_point_line_algrtm(x - half_size, y + half_size, x - half_size, y - half_size)  # Left edge

# Create a new box
def create_random_box(block):
    x = random.randint(-250 + 20, -20) if block == "left" else random.randint(20, 250 - 20)
    y = 340
    health = random.randint(1, 3)
    color = (0, 1, 0) if health == 3 else (1, 1, 0) if health == 2 else (1, 0, 0)
    size = 30
    return {"x": x, "y": y, "size": size, "color": color, "health": health}

# Function to check if a box can be placed in the block without overlapping with other boxes
def can_place_box(new_box, block_boxes):
    for box in block_boxes:
        # Check if the new box overlaps with any existing box in the block
        if abs(new_box["x"] - box["x"]) < (new_box["size"] // 2 + box["size"] // 2) and \
           abs(new_box["y"] - box["y"]) < (new_box["size"] // 2 + box["size"] // 2):
            return False  # If it overlaps, return False
    return True  # No overlap, return True


# Update box positions

def update_boxes():
    global boxes, pointlesses
    # Move all boxes down
    if not freeze:
        for box in boxes:
            if box.get("zigzag", False):  # Check if the box should move in a zigzag pattern
                update_zigzag_box(box)  # Update the box with zigzag movement
            else:
                box["y"] -= BOX_STEP  # Regular downward movement

        # Remove boxes that are out of bounds
        boxes = [box for box in boxes if box["y"] > -WINDOW_HEIGHT // 2]

        # Add random boxes to the blocks
        left_boxes = [box for box in boxes if box["x"] < 0]
        right_boxes = [box for box in boxes if box["x"] > 0]

        total_new_boxes = random.randint(1, 4)

        left_box_count = random.randint(1, max(2, total_new_boxes))
        right_box_count = total_new_boxes - left_box_count  # The rest go to the right block
        right_box_count = max(2, right_box_count)

        # Add boxes to the left block if needed
        while len(left_boxes) < left_box_count:
            new_box = create_random_box("left")
            if can_place_any_box(new_box, left_boxes + right_boxes, pointlesses):  # Check against both boxes and pointlesses
                new_box["zigzag"] = random.random() < 0.2  # 20% chance for zigzag
                left_boxes.append(new_box)

        # Add boxes to the right block if needed
        while len(right_boxes) < right_box_count:
            new_box = create_random_box("right")
            if can_place_any_box(new_box, left_boxes + right_boxes, pointlesses):  # Check against both boxes and pointlesses
                new_box["zigzag"] = random.random() < 0.2  # 20% chance for zigzag
                right_boxes.append(new_box)

        boxes = left_boxes + right_boxes


# Draw all boxes
def draw_boxes():
    for box in boxes:
        draw_box(box["x"], box["y"], box["size"], box["color"])
########################################################################################################################

max_pointless = 2
pointlesses = []
pointless_step = 5
def draw_pointless(x, y, size, color):
    glColor3f(*color)
    half_size = size // 2

    mpl_mid_point_line_algrtm(x - half_size, y - half_size, x, y - 2*half_size)  # Bottom edges
    mpl_mid_point_line_algrtm(x + half_size, y - half_size, x + half_size, y + half_size)  # Right edge
    mpl_mid_point_line_algrtm(x + half_size, y + half_size, x, y + 2*half_size)  # Top edges
    mpl_mid_point_line_algrtm(x - half_size, y + half_size, x - half_size, y - half_size)  # Left edge
    mpl_mid_point_line_algrtm(x - half_size, y + half_size, x, y + 2*half_size)  # Top edges
    mpl_mid_point_line_algrtm(x + half_size, y - half_size, x, y - 2*half_size)  # Bottom edges

# Create a new box
def create_random_pointless(block):
    x = random.randint(-250 + 20, -20) if block == "left" else random.randint(20, 250 - 20)
    y = 330
    health = random.randint(1, 3)
    color = (0, 1, 0) if health == 3 else (1, 1, 0) if health == 2 else (1, 0, 0)
    size = 30
    return {"x": x, "y": y, "size": size, "color": color, "health": health}

# Function to check if a box can be placed in the block without overlapping with other boxes
def can_place_pointless(new_pointless, block_pointless):
    for pointless in block_pointless:
        # Check if the new box overlaps with any existing box in the block
        if abs(new_pointless["x"] - pointless["x"]) < (new_pointless["size"] // 2 + pointless["size"] // 2) and \
           abs(new_pointless["y"] - pointless["y"]) < (new_pointless["size"] // 2 + pointless["size"] // 2):
            return False  # If it overlaps, return False
    return True  # No overlap, return True


# Update box positions
def update_pointlesses():
    global pointlesses, boxes
    # Move all boxes down
    if not freeze:
        for pointless in pointlesses:
            pointless["y"] -= pointless_step

        # Remove boxes that are out of bounds
        pointless = [pointless for pointless in pointlesses if pointless["y"] > -WINDOW_HEIGHT // 2]

        # Add random boxes to the blocks
        left_pointlesses = [pointless for pointless in pointlesses if pointless["x"] < 0]
        right_pointlesses = [pointless for pointless in pointlesses if pointless["x"] > 0]

        total_new_pointlesses = random.randint(1, 2)

        left_pointless_count = random.randint(1, max(2, total_new_pointlesses))
        right_pointless_count = total_new_pointlesses - left_pointless_count  # The rest go to the right block
        right_pointless_count = max(2, right_pointless_count)

        # Add boxes to the left block if needed
        while len(left_pointlesses) < left_pointless_count:
            new_pointless = create_random_pointless("left")
            if can_place_any_box(new_pointless, boxes, left_pointlesses + right_pointlesses):  # Check against both boxes and pointlesses
                left_pointlesses.append(new_pointless)

        # Add boxes to the right block if needed
        while len(right_pointlesses) < right_pointless_count:
            new_pointless = create_random_pointless("right")
            if can_place_any_box(new_pointless, boxes, left_pointlesses + right_pointlesses):  # Check against both boxes and pointlesses
                right_pointlesses.append(new_pointless)

        pointlesses = left_pointlesses + right_pointlesses


# Draw all boxes
def draw_pointlesses():
    for pointless in pointlesses:
        draw_pointless(pointless["x"], pointless["y"], pointless["size"], pointless["color"])

########################################################################################################################
# no overlap ensuring
# Function to check if a box can be placed without overlapping with any other box (either box or pointless)
def can_place_any_box(new_box, all_boxes, all_pointlesses):
    # Check overlap with existing boxes
    for box in all_boxes:
        if abs(new_box["x"] - box["x"]) < (new_box["size"] // 2 + box["size"] // 2) and \
           abs(new_box["y"] - box["y"]) < (new_box["size"] // 2 + box["size"] // 2):
            return False  # If it overlaps, return False

    # Check overlap with existing pointlesses
    for pointless in all_pointlesses:
        if abs(new_box["x"] - pointless["x"]) < (new_box["size"] // 2 + pointless["size"] // 2) and \
           abs(new_box["y"] - pointless["y"]) < (new_box["size"] // 2 + pointless["size"] // 2):
            return False  # If it overlaps, return False

    return True  # No overlap, return True
########################################################################################################################

##zigzag##
def update_zigzag_box(box):
    # Move the box down
    box["y"] -= BOX_STEP

    # Check if it's time to change horizontal direction
    if box.get("zigzag_counter", 0) % ZIGZAG_INTERVAL == 0:
        # Reverse the horizontal direction
        box["zigzag_direction"] = -box.get("zigzag_direction", 1)

    # Move the box horizontally based on the zigzag direction
    box["x"] += box.get("zigzag_direction", 1) * ZIGZAG_STEP

    # Increment the zigzag counter
    box["zigzag_counter"] = box.get("zigzag_counter", 0) + 1
##zigzag##


### Shield Codes##

##Shield code here
#############################

def activate_shield(rocket):
    global rocket1_shield_active, rocket2_shield_active
    global rocket1_shield_timer, rocket2_shield_timer

    if rocket == "rocket1":
        rocket1_shield_active = True
        rocket1_shield_timer = SHIELD_DURATION  # Set timer to 5 seconds
        print("Rocket 1 shield activated!")  # Debug print
    elif rocket == "rocket2":
        rocket2_shield_active = True
        rocket2_shield_timer = SHIELD_DURATION  # Set timer to 5 seconds
        print("Rocket 2 shield activated!")  # Debug print

def update_shield_status():
    global rocket1_shield_active, rocket2_shield_active
    global rocket1_shield_timer, rocket2_shield_timer
    global rocket1_shield_flag, rocket2_shield_flag

    # Decrement Rocket 1's shield timer
    if rocket1_shield_active:
        rocket1_shield_timer -= 1  # Decrement by 1 second
        print(f"Rocket 1 shield timer: {rocket1_shield_timer}")  # Debug print
        if rocket1_shield_timer <= 0:  # Deactivate shield when timer reaches 0
            rocket1_shield_active = False
            rocket1_shield_flag = False  # Ensure the shield cannot be reactivated
            print("Rocket 1 shield deactivated!")  # Debug print

    # Decrement Rocket 2's shield timer
    if rocket2_shield_active:
        rocket2_shield_timer -= 1  # Decrement by 1 second
        print(f"Rocket 2 shield timer: {rocket2_shield_timer}")  # Debug print
        if rocket2_shield_timer <= 0:  # Deactivate shield when timer reaches 0
            rocket2_shield_active = False
            rocket2_shield_flag = False  # Ensure the shield cannot be reactivated
            print("Rocket 2 shield deactivated!")  # Debug print


def check_and_activate_shields():
    global rocket1_shield_flag, rocket2_shield_flag

    # Activate Rocket 1's shield if the score condition is met and the shield is not active
    if rocket1_score >= 5 and not rocket1_shield_active and rocket1_shield_flag:
        activate_shield("rocket1")
        rocket1_shield_flag = False  # Prevent multiple activations

    # Activate Rocket 2's shield if the score condition is met and the shield is not active
    if rocket2_score >= 5 and not rocket2_shield_active and rocket2_shield_flag:
        activate_shield("rocket2")
        rocket2_shield_flag = False  # Prevent multiple activations

############################

### Shield Codes##


## Adjust Firing Code##

# adjust firing rate function start
def adjust_firing_rate():
    global ROCKET1_FIRE_INTERVAL, ROCKET2_FIRE_INTERVAL
    global ROCKET1_FIRE_INTERVAL_FLAG_5, ROCKET2_FIRE_INTERVAL_FLAG_5, ROCKET1_FIRE_INTERVAL_FLAG_10, ROCKET2_FIRE_INTERVAL_FLAG_10
    # Reduce the firing interval for Rocket 1 if its score is 5 or more
    if ROCKET1_FIRE_INTERVAL_FLAG_5:
        if rocket1_score >= 0:
            ROCKET1_FIRE_INTERVAL = ROCKET1_FIRE_INTERVAL - 1000
            ROCKET1_FIRE_INTERVAL_FLAG_5 = False
    if ROCKET1_FIRE_INTERVAL_FLAG_10:
        if rocket1_score >= 10:
            ROCKET1_FIRE_INTERVAL = ROCKET1_FIRE_INTERVAL - 1000
            ROCKET1_FIRE_INTERVAL_FLAG_10 = False

    if ROCKET2_FIRE_INTERVAL_FLAG_5:
        if rocket2_score >= 5:
            ROCKET2_FIRE_INTERVAL = ROCKET2_FIRE_INTERVAL - 1000
            ROCKET2_FIRE_INTERVAL_FLAG_5 = False
    if ROCKET2_FIRE_INTERVAL_FLAG_10:
        if rocket2_score >= 10:
            ROCKET2_FIRE_INTERVAL = ROCKET2_FIRE_INTERVAL - 1000
            ROCKET2_FIRE_INTERVAL_FLAG_10 = False
    return ROCKET1_FIRE_INTERVAL, ROCKET2_FIRE_INTERVAL


##########################

## Adjust Fire Code##

# Projectile attributes
# Lists to hold projectiles
regular_projectiles = []  # List for regular projectiles
special_projectiles = []  # List for special projectiles

# Projectile properties
PROJECTILE_SPEED = 5                 # Speed at which the projectiles move
PROJECTILE_RADIUS = 5                # Radius of the projectile (size)
PROJECTILE_DAMAGE = 1                # Regular projectile damage
SPECIAL_PROJECTILE_DAMAGE = 2        # Special projectile damage

# Colors for projectiles
REGULAR_PROJECTILE_COLOR = (1, 0.5, 0)  # Orange color for regular projectiles
SPECIAL_PROJECTILE_COLOR = (0.5, 0, 1)  # Purple color for special projectiles

# Time intervals for firing projectiles (in milliseconds)
FIRE_INTERVAL = 5000                       # Regular projectile firing interval
SPECIAL_FIRE_INTERVAL = 8000               # Base special projectile firing interval
SPECIAL_PROJECTILE_MIN_INTERVAL = 8000     # Minimum random interval for special projectiles
SPECIAL_PROJECTILE_MAX_INTERVAL = 12000    # Maximum random interval for special projectiles

# Timing variables for rockets
# Regular projectile firing times
last_regular_rocket1_time = 0              # Last time Rocket 1 fired a regular projectile
last_regular_rocket2_time = 0              # Last time Rocket 2 fired a regular projectile

# Special projectile firing times
last_special_rocket1_time = 0        # Last time Rocket 1 fired a special projectile
last_special_rocket2_time = 0        # Last time Rocket 2 fired a special projectile

# Randomized intervals for special projectiles (initial values)
rocket1_special_interval = SPECIAL_PROJECTILE_MIN_INTERVAL  # Randomized special interval for Rocket 1
rocket2_special_interval = SPECIAL_PROJECTILE_MIN_INTERVAL  # Randomized special interval for Rocket 2

# Buffer time to prevent overlapping shots (milliseconds)
OVERLAP_BUFFER_TIME = 500

# Function to create a projectile
def create_projectile(x, y, is_special=False, rocket=""):
    color = SPECIAL_PROJECTILE_COLOR if is_special else REGULAR_PROJECTILE_COLOR
    damage = SPECIAL_PROJECTILE_DAMAGE if is_special else PROJECTILE_DAMAGE
    radius = PROJECTILE_RADIUS
    return {"x": x, "y": y, "color": color, "damage": damage, "radius": radius, "rocket": rocket}

# Function to fire projectiles
def fire_projectiles():
    global last_regular_rocket1_time, last_regular_rocket2_time
    global last_special_rocket1_time, last_special_rocket2_time
    global rocket1_special_interval, rocket2_special_interval
    global ROCKET1_FIRE_INTERVAL, ROCKET2_FIRE_INTERVAL


    current_time = int(time.time() * 1000)  # Get current time in milliseconds
    if not freeze:

        adjust_firing_rate()

        # Randomize special intervals if the interval has passed
        if current_time - last_special_rocket1_time > rocket1_special_interval:
            rocket1_special_interval = random.randint(SPECIAL_PROJECTILE_MIN_INTERVAL, SPECIAL_PROJECTILE_MAX_INTERVAL)

        if current_time - last_special_rocket2_time > rocket2_special_interval:
            rocket2_special_interval = random.randint(SPECIAL_PROJECTILE_MIN_INTERVAL, SPECIAL_PROJECTILE_MAX_INTERVAL)

        # Fire regular projectiles for Rocket 1
        if (
            current_time - last_regular_rocket1_time > ROCKET1_FIRE_INTERVAL and
            current_time - last_special_rocket1_time > OVERLAP_BUFFER_TIME
        ):
            regular_projectiles.append(create_projectile(rocket1_x, rocket_y + 30, False, "rocket1"))
            last_regular_rocket1_time = current_time

        # Fire regular projectiles for Rocket 2
        if (
            current_time - last_regular_rocket2_time > ROCKET2_FIRE_INTERVAL and
            current_time - last_special_rocket2_time > OVERLAP_BUFFER_TIME
        ):
            regular_projectiles.append(create_projectile(rocket2_x, rocket_y + 30, False, "rocket2"))
            last_regular_rocket2_time = current_time

        # Fire special projectiles for Rocket 1
        if (
            current_time - last_special_rocket1_time > rocket1_special_interval and
            current_time - last_regular_rocket1_time > OVERLAP_BUFFER_TIME
        ):
            special_projectiles.append(create_projectile(rocket1_x, rocket_y + 30, True, "rocket1"))
            last_special_rocket1_time = current_time

        # Fire special projectiles for Rocket 2
        if (
            current_time - last_special_rocket2_time > rocket2_special_interval and
            current_time - last_regular_rocket2_time > OVERLAP_BUFFER_TIME
        ):
            special_projectiles.append(create_projectile(rocket2_x, rocket_y + 30, True, "rocket2"))
            last_special_rocket2_time = current_time

# Function to update projectiles

def update_projectiles():
    global regular_projectiles, special_projectiles
    if not freeze:
        # Move regular projectiles upwards
        for projectile in regular_projectiles:
            projectile["y"] += PROJECTILE_SPEED

        # Move special projectiles upwards
        for projectile in special_projectiles:
            projectile["y"] += PROJECTILE_SPEED

        # Remove off-screen regular projectiles
        regular_projectiles = [proj for proj in regular_projectiles if proj["y"] < WINDOW_HEIGHT]

        # Remove off-screen special projectiles
        special_projectiles = [proj for proj in special_projectiles if proj["y"] < WINDOW_HEIGHT]

        # Handle projectile collision with boxes
        handle_projectile_collision()


# Function to draw projectiles
def draw_projectiles():
    # Draw regular projectiles
    for projectile in regular_projectiles:
        glColor3f(*projectile["color"])  # Set the color
        mpc_midpoint_circle_algrthm(projectile["radius"], projectile["x"], projectile["y"])

    # Draw special projectiles
    for projectile in special_projectiles:
        glColor3f(*projectile["color"])  # Set the special color
        mpc_midpoint_circle_algrthm(projectile["radius"], projectile["x"], projectile["y"])


########################################################################################################################

# Function to handle projectile collision with boxes and update health/score
def handle_projectile_collision():
    global boxes, rocket1_score, rocket2_score, regular_projectiles, special_projectiles, game_over, winner
    if rocket1_score<0:
        game_over=True
        winner="Rocket 2"
    elif rocket2_score<0:
        game_over=True
        winner="Rocket 1"
    # Track projectiles to remove after collision
    regular_to_remove = []
    special_to_remove = []
    if not game_over:
        # Check collision for regular projectiles
        for projectile in regular_projectiles:
            for box in boxes:
                # Check if the projectile collides with the box (using distance between center of projectile and box)
                if abs(projectile["x"] - box["x"]) < (projectile["radius"] + box["size"] // 2) and \
                   abs(projectile["y"] - box["y"]) < (projectile["radius"] + box["size"] // 2):
                    regular_to_remove.append(projectile)  # Mark projectile for removal

                    if box["color"] == (0, 1, 0):  # Green box (health = 3)
                        box["health"] -= PROJECTILE_DAMAGE
                        box["color"] = (1, 1, 0)  # Change color to yellow

                    elif box["color"] == (1, 1, 0):  # Yellow box (health = 2)
                        box["health"] -= PROJECTILE_DAMAGE
                        if box["health"] <= 1:
                            box["color"] = (1, 0, 0)  # Change color to red

                    elif box["color"] == (1, 0, 0):  # Red box (health = 1)
                        # Create a circle before removing the box
                        create_circle(box["x"], box["y"])
                        boxes.remove(box)
                        if projectile["rocket"] == "rocket1":
                            rocket1_score += 1
                        elif projectile["rocket"] == "rocket2":
                            rocket2_score += 1
                    break  # Exit the loop since the projectile has hit a box
            #pointless ---------------------------------------------------
            for pointless in pointlesses:
                # Check if the projectile collides with the box (using distance between center of projectile and box)
                if abs(projectile["x"] - pointless["x"]) < (projectile["radius"] + pointless["size"] // 2) and \
                   abs(projectile["y"] - pointless["y"]) < (projectile["radius"] + pointless["size"] // 2):
                    regular_to_remove.append(projectile)  # Mark projectile for removal

                    if pointless["color"] == (0, 1, 0):  # Green box (health = 3)
                        pointless["health"] -= PROJECTILE_DAMAGE
                        pointless["color"] = (1, 1, 0)  # Change color to yellow

                    elif pointless["color"] == (1, 1, 0):  # Yellow box (health = 2)
                        pointless["health"] -= PROJECTILE_DAMAGE
                        if pointless["health"] <= 1:
                            pointless["color"] = (1, 0, 0)  # Change color to red

                    elif pointless["color"] == (1, 0, 0):  # Red box (health = 1)
                        # Create a circle before removing the box
                        pointlesses.remove(pointless)
                    break  # Exit the loop since the projectile has hit a box

    # Check collision for special projectiles
    for projectile in special_projectiles:
        for box in boxes:
            if abs(projectile["x"] - box["x"]) < (projectile["radius"] + box["size"] // 2) and \
               abs(projectile["y"] - box["y"]) < (projectile["radius"] + box["size"] // 2):
                special_to_remove.append(projectile)  # Mark projectile for removal

                if box["color"] == (0, 1, 0):  # Green box (health = 3)
                    box["health"] = 1  # Special projectile reduces health to 1
                    box["color"] = (1, 0, 0)  # Change color to red

                elif box["color"] == (1, 1, 0):  # Yellow box (health = 2)
                    # Create a circle before removing the box
                    create_circle(box["x"], box["y"])
                    boxes.remove(box)
                    if projectile["rocket"] == "rocket1":
                        rocket1_score += 1
                    elif projectile["rocket"] == "rocket2":
                        rocket2_score += 1

                elif box["color"] == (1, 0, 0):  # Red box (health = 1)
                    # Create a circle before removing the box
                    create_circle(box["x"], box["y"])
                    boxes.remove(box)
                    if projectile["rocket"] == "rocket1":
                        rocket1_score += 1
                    elif projectile["rocket"] == "rocket2":
                        rocket2_score += 1
                break  # Exit the loop since the projectile has hit a box
        for pointless in pointlesses:
            if abs(projectile["x"] - pointless["x"]) < (projectile["radius"] + pointless["size"] // 2) and \
               abs(projectile["y"] - pointless["y"]) < (projectile["radius"] + pointless["size"] // 2):
                special_to_remove.append(projectile)  # Mark projectile for removal

                if pointless["color"] == (0, 1, 0):  # Green box (health = 3)
                    pointless["health"] = 1  # Special projectile reduces health to 1
                    pointless["color"] = (1, 0, 0)  # Change color to red

                elif pointless["color"] == (1, 1, 0):  # Yellow box (health = 2)
                    # Create a circle before removing the box
                    pointlesses.remove(pointless)

                elif pointless["color"] == (1, 0, 0):  # Red box (health = 1)
                    # Create a circle before removing the box
                    pointlesses.remove(pointless)
                break  # Exit the loop since the projectile has hit a box


    # Remove projectiles that collided
    regular_projectiles = [proj for proj in regular_projectiles if proj not in regular_to_remove]
    special_projectiles = [proj for proj in special_projectiles if proj not in special_to_remove]
########################################################################################################################
#plane box collision
import math
def check_collisions():
    """
    Check for collisions between boxes and rockets.
    """
    global rocket1_collisions, rocket2_collisions, game_over, winner, boxes, pointlesses
    for box in boxes[:]:  # Iterate over a copy of the boxes to allow removal
        box_radius = box["size"] // 2  # Half the box size for radius comparison

        # Collision with Rocket 1
        distance_to_rocket1 = math.sqrt((box["x"] - rocket1_x) ** 2 + (box["y"] - rocket_y) ** 2)
        if distance_to_rocket1 <= (rocket_radius + box_radius):  # Check for collision
            if not rocket1_shield_active:  # Only count collision if shield is not active
                rocket1_collisions += 1
                if rocket1_collisions >= 3:
                    game_over = True
                    winner = "Rocket 2"
            boxes.remove(box)  # Remove collided box
            return  # Handle one collision at a time

        # Collision with Rocket 2
        distance_to_rocket2 = math.sqrt((box["x"] - rocket2_x) ** 2 + (box["y"] - rocket_y) ** 2)
        if distance_to_rocket2 <= (rocket_radius + box_radius):  # Check for collision
            if not rocket2_shield_active:  # Only count collision if shield is not active
                rocket2_collisions += 1
                if rocket2_collisions >= 3:
                    game_over = True
                    winner = "Rocket 1"
            boxes.remove(box)  # Remove collided box
            return  # Handle one collision at a time
#pointlesses --------------------------------------------------------------------------------------------------------------
        for pointless in pointlesses[:]:  # Iterate over a copy of the boxes to allow removal
            pointless_radius = pointless["size"] // 2  # Half the box size for radius comparison

            # Collision with Rocket 1
            distance_to_rocket1 = math.sqrt((pointless["x"] - rocket1_x) ** 2 + (pointless["y"] - rocket_y) ** 2)#-----------------
            if distance_to_rocket1 <= (rocket_radius + pointless_radius):  # Check for collision
                rocket1_collisions += 1
                pointlesses.remove(pointless)  # Remove collided box
                if rocket1_collisions >= 3:
                    game_over = True
                    winner = "Rocket 2"
                return  # Handle one collision at a time

            # Collision with Rocket 2
            distance_to_rocket2 = math.sqrt((pointless["x"] - rocket2_x) ** 2 + (pointless["y"] - rocket_y) ** 2) #---------------
            if distance_to_rocket2 <= (rocket_radius + pointless_radius):  # Check for collision
                rocket2_collisions += 1
                pointlesses.remove(pointless)  # Remove collided box
                if rocket2_collisions >= 3:
                    game_over = True
                    winner = "Rocket 1"
                return  # Handle one collision at a time


########################################################################################################################
circle_radius = 10  # Radius of the circle
circle_objects = []  # List to store circles
CIRCLE_LIFETIME = 200


# Function to create a circle when a box is destroyed
def create_circle(x, y):
    # Randomly choose whether the circle will be a power-up or power-down
    is_positive = random.random() < 0.7  # 70% chance for a power-up
    score_change = random.choice([3, 5]) if is_positive else random.choice([-1, -3])

    # Add the circle to the list
    circle_objects.append({
        "x": x,
        "y": y,
        "radius": circle_radius,
        "score_change": score_change,  # Score change (positive or negative)
        "is_positive": is_positive,  # Whether it's a power-up or power-down
        "life_time": CIRCLE_LIFETIME,
    })


# Function to draw circles
def draw_circles():
    for circle in circle_objects:

        glColor3f(1.5, 0, 1.5)
        mpc_midpoint_circle_algrthm(circle["radius"], circle["x"], circle["y"])

def update_circles():
    global circle_objects
    for circle in circle_objects[:]:  # Iterate through a copy to allow safe removal
        circle["life_time"] -= 1  # Decrement lifetime
        if circle["life_time"] <= 0:
            circle_objects.remove(circle)  # Remove circle when lifetime is over

def handle_projectile_circle_collision():
    global rocket1_score, rocket2_score, game_over

    projectiles_to_remove = []
    circles_to_remove = []
    if not game_over:
        for projectile in regular_projectiles + special_projectiles:
            for circle in circle_objects[:]:
                # Calculate the Euclidean distance between the center of the projectile and the circle
                distance = math.sqrt((projectile["x"] - circle["x"])**2 + (projectile["y"] - circle["y"])**2)

                # Check if the distance between the centers is less than or equal to the sum of the radii
                if distance <= (projectile["radius"] + circle["radius"]):
                    # Apply score change based on the rocket that fired the projectile
                    if projectile["rocket"] == "rocket1":
                        rocket1_score += circle["score_change"]
                        print(f"Rocket 1 score updated: {rocket1_score}")  # Debug print
                    elif projectile["rocket"] == "rocket2":
                        rocket2_score += circle["score_change"]
                        print(f"Rocket 2 score updated: {rocket2_score}")  # Debug print

                    # Mark circle and projectile for removal
                    circles_to_remove.append(circle)
                    projectiles_to_remove.append(projectile)

                    # Stop further checking once a collision is detected
                    break

        # Remove collided projectiles and circles
        for circle in circles_to_remove:
            circle_objects.remove(circle)

        for projectile in projectiles_to_remove:

            if projectile in regular_projectiles:
                regular_projectiles.remove(projectile)
            elif projectile in special_projectiles:
                special_projectiles.remove(projectile)

# Check if any rocket's score is below 0
def check_game_over():
    global game_over, winner

    if game_over:
        return  # Skip checks if the game is already over

    if rocket1_score < 0:
        winner = "Rocket 2"
        print(f"Game Over! {winner} wins with a score of {rocket2_score}.")  # Debug print---------------------
        game_over = True  # Set the game-over state

    elif rocket2_score < 0:
        winner = "Rocket 1"
        print(f"Game Over! {winner} wins with a score of {rocket1_score}.")  # Debug print
        game_over = True  # Set the game-over state

# Function to render the game over message
def render_game_over():
    if game_over:
        glColor3f(1, 1, 1)  # White color for text
        glRasterPos2f(0, 0)  # Center the text
        render_text(-50, 0, "Game Over!", font=GLUT_BITMAP_HELVETICA_18, color=(1, 1, 1))
        render_text(-100, -30,f"{winner} wins with score {rocket1_score if winner == 'Rocket 1' else rocket2_score}!", font=GLUT_BITMAP_HELVETICA_18, color=(1, 1, 1))

# Main game drawing function
def draw_game():
    if not game_over:
        # Draw the dividing line and the rockets, projectiles, and circles as usual
        draw_dividing_line()
        draw_rocket_1(rocket1_x, rocket_y)
        draw_rocket_2(rocket2_x, rocket_y)
        draw_boxes()
        draw_pointlesses()
        draw_projectiles()
        draw_circles()
    else:
        render_game_over()  # Render game over message if the game is over

########################################################################################################################


# Keyboard input handling
def keyboard(key, x, y):
    global rocket1_x, rocket2_x

    if key == b'a' and not freeze:  # Move Rocket 1 left
        if rocket1_x - ROCKET_STEP >= LEFT_BLOCK_LIMIT:
            rocket1_x -= ROCKET_STEP
    elif key == b'd' and not freeze:  # Move Rocket 1 right
        if rocket1_x + ROCKET_STEP <= RIGHT_BLOCK_LIMIT - 20:  # Allowing space for rocket width
            rocket1_x += ROCKET_STEP
    glutPostRedisplay()

def special_keys(key, x, y):
    global rocket2_x

    if key == GLUT_KEY_LEFT and not freeze:  # Move Rocket 2 left
        if rocket2_x - ROCKET_STEP >= RIGHT_BLOCK_LIMIT + 20:  # Allowing space for rocket width
            rocket2_x -= ROCKET_STEP
    elif key == GLUT_KEY_RIGHT and not freeze:  # Move Rocket 2 right
        if rocket2_x + ROCKET_STEP <= WINDOW_WIDTH // 2 - 20:
            rocket2_x += ROCKET_STEP
    glutPostRedisplay()

def co_orninate_conversion(x, y):
    a = x - 250
    b = 250 - y
    return a, b

def game_reset():
    global boxes, regular_projectiles, special_projectiles, last_regular_rocket1_time, last_regular_rocket2_time, last_special_rocket1_time, last_special_rocket2_time
    global freeze, rocket1_score, rocket2_score, rocket1_collisions, rocket2_collisions, game_over, winner, rocket1_x, rocket2_x, circle_objects, pointlesses
    freeze = False
    game_over = False
    winner = None
    rocket1_x = -125
    rocket2_x = 125
    rocket1_score = rocket2_score = rocket1_collisions = rocket2_collisions = 0
    boxes = []
    pointlesses = []
    regular_projectiles = []
    special_projectiles = []
    last_regular_rocket1_time = 0
    last_regular_rocket2_time = 0
    last_special_rocket1_time = 0
    last_special_rocket2_time = 0
    circle_objects = []

def mouse_listener(button, state, x, y):
    global freeze

    # Left button pressed
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        x_coord, y_coord = co_orninate_conversion(x, y)       # Converting into OpenGL coordinates
        if -212 < x_coord < -158 and 185 < y_coord < 226:     # Checking the mouse click if in the resest button boundary
            game_reset()


        elif -17 < x_coord < 17 and 183 < y_coord < 226:       # Checking  the mouse click if in the pause boundary
            freeze = not freeze


        elif 178 < x_coord < 222 and 192 < y_coord < 221:      # Checking  the mouse click if in the terminate boundary
            glutLeaveMainLoop()

    glutPostRedisplay()


# Modify draw function to show the score
def draw_score():
    # Draw scores of both rockets
    draw_text(-200, 350, f"Rocket 1 Score: {rocket1_score}", (1, 1, 1))
    draw_text(100, 350, f"Rocket 2 Score: {rocket2_score}", (1, 1, 1))

# Function to render text on the screen
def render_text(x, y, text, font=(GLUT_BITMAP_HELVETICA_18), color=(1, 1, 1)):
    glColor3f(*color)  # Set text color
    glRasterPos2f(x, y)  # Set text position
    for char in text:
        glutBitmapCharacter(font, ord(char))

########################################################################################################################
########################################################################################################################
# Animation function
shield_update_counter = 0  # Counter to track elapsed time for shield updates


def animate(value):
    global shield_update_counter

    fire_projectiles()  # Make the rockets fire projectiles
    update_projectiles()  # Update the positions of all projectiles
    update_boxes()  # Update the boxes
    update_circles()  # Update the circles and handle their lifetime
    handle_projectile_circle_collision()
    update_pointlesses()

    # Check and activate shields
    check_and_activate_shields()

    # Update shield status every second
    shield_update_counter += 1
    if shield_update_counter >= 10:  # 10 * 100ms = 1 second
        update_shield_status()
        shield_update_counter = 0

    glutPostRedisplay()  # Request a redraw of the display
    glutTimerFunc(100, animate, 0)  # Reschedule the animation function

def display():
    glClear(GL_COLOR_BUFFER_BIT)  # Clear the screen

    # Draw all game elements
    draw_game()
    glColor3f(0, 0, 1)
    mpl_mid_point_line_algrtm(-210, 352, -158, 352)
    mpl_mid_point_line_algrtm(-212, 352, -192, 372)
    mpl_mid_point_line_algrtm(-212, 352, -192, 332)

    # Pause Button // Space button
    glColor3f(1, 0.5, 0)
    if freeze:
        mpl_mid_point_line_algrtm(-17, 372, -17, 328)
        mpl_mid_point_line_algrtm(-17, 372, 17, 352)
        mpl_mid_point_line_algrtm(-17, 328, 17, 352)
    else:
        mpl_mid_point_line_algrtm(-12, 372, -12, 328)
        mpl_mid_point_line_algrtm(12, 372, 12, 328)

    # Cross Button // Terminate button
    glPointSize(4)
    glColor3f(1, 0, 0)
    mpl_mid_point_line_algrtm(212, 367, 178, 337)
    mpl_mid_point_line_algrtm(212, 337, 178, 367)
    # Draw scores
    if not game_over:
        render_text(-200, -385, f"Rocket1 Score: {rocket1_score}", font=GLUT_BITMAP_HELVETICA_18, color=(1, 1, 1))
        render_text(100, -385, f"Rocket2 Score: {rocket2_score}", font=GLUT_BITMAP_HELVETICA_18, color=(1, 1, 1))
    check_collisions()
    glutSwapBuffers()  # Swap buffers for double buffering


# Initialization
def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Set background color to black
    glMatrixMode(GL_PROJECTION)        # Set projection matrix mode
    glLoadIdentity()                   # Load identity matrix (clear the previous transformations)
    gluOrtho2D(-WINDOW_WIDTH // 2, WINDOW_WIDTH // 2, -WINDOW_HEIGHT // 2, WINDOW_HEIGHT // 2)  # Set 2D view
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)  # Set viewport to the window size


# Main function
def main():
    glutInit()
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Rocket Game")  # Create the window
    init()  # Initialize OpenGL settings
    glutDisplayFunc(display)  # Set the display callback
    glutKeyboardFunc(keyboard)  # Set the keyboard callback
    glutMouseFunc(mouse_listener)
    glutSpecialFunc(special_keys)  # Set the special key callback
    glutTimerFunc(100, animate, 0)  # Start the animation
    glutMainLoop()  # Enter the GLUT main loop


if __name__ == "__main__":
    main()
