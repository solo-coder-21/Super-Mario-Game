import tkinter as tk
from tkinter import Canvas
import math
import random

class MarioGame:
    def _init_(self):
        
        self.root = tk.Tk()
        self.root.title("Super Mario Bros - Enhanced Edition")
        self.root.geometry("1000x700")
        self.root.resizable(False, False)
        self.root.configure(bg='#87CEEB')
        
        self.canvas = Canvas(self.root, width=1000, height=700, bg='#87CEEB')
        self.canvas.pack()
        
        self.game_running = True
        self.score = 0
        self.level = 1
        self.difficulty_multiplier = 1.0
        
        # Game objects
        self.mario = None
        self.platforms = []
        self.enemies = []
        self.coins = []
        self.power_ups = []
        self.fireballs = []
        
        # Timing
        self.frame_count = 0
        self.last_fireball_time = 0
        
        # Key bindings
        self.keys_pressed = set()
        self.root.bind('<KeyPress>', self.key_press)
        self.root.bind('<KeyRelease>', self.key_release)
        self.root.focus_set()
        
        # Initialize game
        self.setup_game()
        self.game_loop()
    
    def key_press(self, event):
        """Handle key press events"""
        self.keys_pressed.add(event.keysym)
    
    def key_release(self, event):
        """Handle key release events"""
        self.keys_pressed.discard(event.keysym)
    
    def setup_game(self):
        """Initialize all game objects"""
        # Create Mario
        self.mario = Mario(100, 500, self.canvas)
        
        # Create platforms
        self.platforms = [
            Platform(0, 650, 1000, 50, self.canvas, "ground"),
            Platform(200, 550, 200, 20, self.canvas, "brick"),
            Platform(500, 450, 150, 20, self.canvas, "brick"),
            Platform(750, 350, 200, 20, self.canvas, "brick"),
            Platform(300, 300, 150, 20, self.canvas, "brick"),
        ]
        
        # Create initial enemies
        self.enemies = [
            Goomba(400, 620, self.canvas),
            Goomba(600, 420, self.canvas),
            Goomba(800, 320, self.canvas),
        ]
        
        # Create initial coins
        self.coins = [
            Coin(250, 500, self.canvas),
            Coin(550, 400, self.canvas),
            Coin(350, 250, self.canvas),
        ]
        
        # Create power-ups
        self.power_ups = [
            PowerUp(350, 500, self.canvas, "mushroom"),
            PowerUp(600, 400, self.canvas, "fire_flower"),
        ]
    
    def update_game(self):
        """Update all game objects"""
        if not self.game_running or self.mario is None:
            return
        
        self.frame_count += 1
        
        # Update Mario
        self.mario.update(self.keys_pressed, self.platforms)
        
        # Handle fireball shooting
        if 'x' in self.keys_pressed and self.mario.power_state == "fire":
            current_time = self.frame_count
            if current_time - self.last_fireball_time > 20:  # Limit firing rate
                direction = 1 if self.mario.facing_right else -1
                fireball_x = self.mario.x + (self.mario.width if direction == 1 else 0)
                fireball_y = self.mario.y + self.mario.height // 2
                self.fireballs.append(Fireball(fireball_x, fireball_y, self.canvas, direction))
                self.last_fireball_time = current_time
        
        # Update fireballs
        for fireball in self.fireballs[:]:
            fireball.update(self.platforms)
            
            # Remove fireballs that go off screen
            if fireball.x < -50 or fireball.x > 1050:
                self.fireballs.remove(fireball)
                fireball.destroy()
                continue
            
            # Check fireball-enemy collisions
            for enemy in self.enemies[:]:
                if fireball.check_collision(enemy):
                    self.enemies.remove(enemy)
                    enemy.destroy()
                    self.fireballs.remove(fireball)
                    fireball.destroy()
                    self.score += 200
                    break
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(self.platforms)
            if enemy.check_collision(self.mario):
                if self.mario.y_velocity > 0 and self.mario.y < enemy.y - 10:
                    # Mario stomps enemy
                    self.enemies.remove(enemy)
                    enemy.destroy()
                    self.score += 100
                    self.mario.y_velocity = -15
                else:
                    # Enemy hits Mario
                    if not self.mario.invincible:
                        self.mario.take_damage()
                        if self.mario.power_state == "small":
                            self.respawn_mario()
        
        # Update coins
        for coin in self.coins[:]:
            if coin.check_collision(self.mario):
                self.coins.remove(coin)
                coin.destroy()
                self.score += 200
        
        # Update power-ups
        for power_up in self.power_ups[:]:
            power_up.update(self.platforms)
            if power_up.check_collision(self.mario):
                self.power_ups.remove(power_up)
                power_up.destroy()
                self.mario.power_up(power_up.type)
                self.score += 1000
        
        # Spawn new objects periodically (never-ending game)
        if self.frame_count % 300 == 0:  # Every 5 seconds
            self.spawn_coin()
        
        if self.frame_count % 600 == 0:  # Every 10 seconds
            self.spawn_enemy()
            self.level += 1
            self.difficulty_multiplier += 0.1
        
        if self.frame_count % 1200 == 0:  # Every 20 seconds
            self.spawn_power_up()
        
        # Respawn if Mario falls
        if self.mario.y > 800:
            self.respawn_mario()
        
        # Update UI
        self.update_ui()
    
    def spawn_coin(self):
        """Spawn a new coin"""
        x = random.randint(100, 900)
        y = random.randint(200, 600)
        self.coins.append(Coin(x, y, self.canvas))
    
    def spawn_enemy(self):
        """Spawn a new enemy"""
        x = random.randint(100, 900)
        y = 620
        self.enemies.append(Goomba(x, y, self.canvas))
    
    def spawn_power_up(self):
        """Spawn a new power-up"""
        x = random.randint(200, 800)
        y = random.randint(300, 500)
        power_type = random.choice(["mushroom", "fire_flower"])
        self.power_ups.append(PowerUp(x, y, self.canvas, power_type))
    
    def respawn_mario(self):
        """Respawn Mario at start position"""
        if self.mario is not None:
            self.mario.x = 100
            self.mario.y = 500
            self.mario.x_velocity = 0
            self.mario.y_velocity = 0
            self.mario.invincible = True
            self.mario.invincible_timer = 120
    
    def update_ui(self):
        """Update the user interface"""
        self.canvas.delete("ui")
        
        # Display game info
        self.canvas.create_text(80, 30, text=f"Score: {self.score}", 
                              font=("Arial", 16, "bold"), fill="white", tags="ui")
        self.canvas.create_text(80, 60, text=f"Level: {self.level}", 
                              font=("Arial", 16, "bold"), fill="white", tags="ui")
        self.canvas.create_text(80, 90, text=f"Power: {self.mario.power_state.upper()}", 
                              font=("Arial", 14, "bold"), fill="yellow", tags="ui")
        
        # Controls
        self.canvas.create_text(850, 30, text="Controls:", 
                              font=("Arial", 12, "bold"), fill="white", tags="ui")
        self.canvas.create_text(850, 50, text="← →: Move", 
                              font=("Arial", 10), fill="lightgray", tags="ui")
        self.canvas.create_text(850, 70, text="Space: Jump", 
                              font=("Arial", 10), fill="lightgray", tags="ui")
        self.canvas.create_text(850, 90, text="X: Fireball (Fire Mode)", 
                              font=("Arial", 10), fill="lightgray", tags="ui")
    
    def game_loop(self):
        """Main game loop"""
        self.update_game()
        self.root.after(16, self.game_loop)  # ~60 FPS
    
    def run(self):
        """Start the game"""
        self.root.mainloop()


class Mario:
    def _init_(self, x, y, canvas):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.x_velocity = 0
        self.y_velocity = 0
        self.on_ground = False
        self.speed = 6
        self.jump_power = -18
        self.gravity = 0.8
        self.facing_right = True
        self.power_state = "small"  # small, big, fire
        self.invincible = False
        self.invincible_timer = 0
        
        self.sprite_parts = []
        self.create_sprite()
    
    def create_sprite(self):
        """Create Mario sprite based on power state"""
        # Clear previous sprite
        for part in self.sprite_parts:
            self.canvas.delete(part)
        self.sprite_parts = []
        
        # Adjust size and colors based on power state
        if self.power_state == "small":
            self.height = 32
            body_color = "#FF0000"
            hat_color = "#8B0000"
        elif self.power_state == "big":
            self.height = 42
            body_color = "#FF0000"
            hat_color = "#8B0000"
        else:  # fire
            self.height = 42
            body_color = "#FF6B6B"
            hat_color = "#FF0000"
        
        # Main body
        body = self.canvas.create_rectangle(
            self.x, self.y, self.x + self.width, self.y + self.height,
            fill=body_color, outline="black", width=2
        )
        self.sprite_parts.append(body)
        
        # Hat
        hat = self.canvas.create_rectangle(
            self.x, self.y, self.x + self.width, self.y + 12,
            fill=hat_color, outline="black", width=1
        )
        self.sprite_parts.append(hat)
        
        # Eyes
        eye_y = self.y + 8
        if self.facing_right:
            eye1 = self.canvas.create_oval(self.x + 8, eye_y, self.x + 12, eye_y + 4, fill="white")
            eye2 = self.canvas.create_oval(self.x + 20, eye_y, self.x + 24, eye_y + 4, fill="white")
            pupil1 = self.canvas.create_oval(self.x + 10, eye_y + 1, self.x + 12, eye_y + 3, fill="black")
            pupil2 = self.canvas.create_oval(self.x + 22, eye_y + 1, self.x + 24, eye_y + 3, fill="black")
        else:
            eye1 = self.canvas.create_oval(self.x + 8, eye_y, self.x + 12, eye_y + 4, fill="white")
            eye2 = self.canvas.create_oval(self.x + 20, eye_y, self.x + 24, eye_y + 4, fill="white")
            pupil1 = self.canvas.create_oval(self.x + 8, eye_y + 1, self.x + 10, eye_y + 3, fill="black")
            pupil2 = self.canvas.create_oval(self.x + 20, eye_y + 1, self.x + 22, eye_y + 3, fill="black")
        
        self.sprite_parts.extend([eye1, eye2, pupil1, pupil2])
        
        # Mustache
        mustache = self.canvas.create_rectangle(
            self.x + 10, self.y + 16, self.x + 22, self.y + 20, fill="black"
        )
        self.sprite_parts.append(mustache)
        
        # Invincibility effect
        if self.invincible and self.invincible_timer % 10 < 5:
            # Flash effect
            for part in self.sprite_parts:
                self.canvas.itemconfig(part, stipple="gray50")
    
    def update(self, keys_pressed, platforms):
        """Update Mario's position and physics"""
        # Handle invincibility
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        # Horizontal movement
        if 'Left' in keys_pressed:
            self.x_velocity = -self.speed
            self.facing_right = False
        elif 'Right' in keys_pressed:
            self.x_velocity = self.speed
            self.facing_right = True
        else:
            self.x_velocity *= 0.8  # Friction
        
        # Jumping
        if 'space' in keys_pressed and self.on_ground:
            self.y_velocity = self.jump_power
            self.on_ground = False
        
        # Apply gravity
        self.y_velocity += self.gravity
        if self.y_velocity > 15:
            self.y_velocity = 15
        
        # Update position
        self.x += self.x_velocity
        self.y += self.y_velocity
        
        # Keep Mario on screen
        if self.x < 0:
            self.x = 0
        elif self.x > 1000 - self.width:
            self.x = 1000 - self.width
        
        # Check platform collisions
        self.on_ground = False
        for platform in platforms:
            if self.check_platform_collision(platform):
                break
        
        # Update sprite
        self.create_sprite()
    
    def check_platform_collision(self, platform):
        """Check collision with a platform"""
        mario_left = self.x
        mario_right = self.x + self.width
        mario_top = self.y
        mario_bottom = self.y + self.height
        
        plat_left = platform.x
        plat_right = platform.x + platform.width
        plat_top = platform.y
        plat_bottom = platform.y + platform.height
        
        if (mario_right > plat_left and mario_left < plat_right and
            mario_bottom > plat_top and mario_top < plat_bottom):
            
            # Landing on top
            if self.y_velocity > 0 and mario_bottom - plat_top < 25:
                self.y = plat_top - self.height
                self.y_velocity = 0
                self.on_ground = True
                return True
            
            # Hitting from below
            elif self.y_velocity < 0 and plat_bottom - mario_top < 25:
                self.y = plat_bottom
                self.y_velocity = 0
                return True
        
        return False
    
    def power_up(self, power_type):
        """Apply power-up effect"""
        if power_type == "mushroom" and self.power_state == "small":
            self.power_state = "big"
        elif power_type == "fire_flower":
            self.power_state = "fire"
    
    def take_damage(self):
        """Take damage and downgrade power state"""
        if self.power_state == "fire":
            self.power_state = "big"
            self.invincible = True
            self.invincible_timer = 120
        elif self.power_state == "big":
            self.power_state = "small"
            self.invincible = True
            self.invincible_timer = 120


class Fireball:
    def _init_(self, x, y, canvas, direction):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = 12
        self.height = 12
        self.x_velocity = 8 * direction
        self.y_velocity = -3
        self.gravity = 0.3
        self.direction = direction
        self.bounces = 0
        self.max_bounces = 3
        
        self.sprite = self.create_sprite()
    
    def create_sprite(self):
        """Create fireball sprite"""
        return self.canvas.create_oval(
            self.x, self.y, self.x + self.width, self.y + self.height,
            fill="#FF4500", outline="#FF0000", width=2
        )
    
    def update(self, platforms):
        """Update fireball physics"""
        # Apply gravity
        self.y_velocity += self.gravity
        
        # Update position
        self.x += self.x_velocity
        self.y += self.y_velocity
        
        # Check platform collisions
        for platform in platforms:
            if self.check_platform_collision(platform):
                break
        
        # Update sprite position
        self.canvas.coords(self.sprite, self.x, self.y, 
                          self.x + self.width, self.y + self.height)
        
        # Remove if too many bounces
        if self.bounces >= self.max_bounces:
            return False
        return True
    
    def check_platform_collision(self, platform):
        """Check collision with platform"""
        if (self.x + self.width > platform.x and self.x < platform.x + platform.width and
            self.y + self.height > platform.y and self.y < platform.y + platform.height):
            
            if self.y_velocity > 0:  # Falling, bounce up
                self.y = platform.y - self.height
                self.y_velocity = -abs(self.y_velocity) * 0.7
                self.bounces += 1
                return True
        return False
    
    def check_collision(self, enemy):
        """Check collision with enemy"""
        return (self.x < enemy.x + enemy.width and
                self.x + self.width > enemy.x and
                self.y < enemy.y + enemy.height and
                self.y + self.height > enemy.y)
    
    def destroy(self):
        """Remove fireball from canvas"""
        self.canvas.delete(self.sprite)


class Platform:
    def _init_(self, x, y, width, height, canvas, platform_type="brick"):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = platform_type
        
        self.create_sprite()
    
    def create_sprite(self):
        """Create platform sprite"""
        if self.type == "ground":
            self.sprite = self.canvas.create_rectangle(
                self.x, self.y, self.x + self.width, self.y + self.height,
                fill="#8B4513", outline="#654321", width=2
            )
            # Grass on top
            self.canvas.create_rectangle(
                self.x, self.y, self.x + self.width, self.y + 8,
                fill="#228B22", outline="#006400"
            )
        else:
            self.sprite = self.canvas.create_rectangle(
                self.x, self.y, self.x + self.width, self.y + self.height,
                fill="#CD853F", outline="#8B4513", width=2
            )


class PowerUp:
    def _init_(self, x, y, canvas, power_type):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = 24
        self.height = 24
        self.type = power_type
        self.x_velocity = 2 if random.choice([True, False]) else -2
        self.y_velocity = 0
        self.gravity = 0.5
        
        self.sprite = self.create_sprite()
    
    def create_sprite(self):
        """Create power-up sprite"""
        if self.type == "mushroom":
            # Red mushroom
            sprite = self.canvas.create_oval(
                self.x, self.y, self.x + self.width, self.y + self.height,
                fill="#FF0000", outline="white", width=2
            )
            # White spots
            self.canvas.create_oval(self.x + 4, self.y + 4, self.x + 8, self.y + 8, fill="white")
            self.canvas.create_oval(self.x + 16, self.y + 8, self.x + 20, self.y + 12, fill="white")
        else:  # fire_flower
            # Orange flower
            sprite = self.canvas.create_rectangle(
                self.x, self.y, self.x + self.width, self.y + self.height,
                fill="#FFA500", outline="#FF4500", width=2
            )
            # Flower petals
            self.canvas.create_oval(self.x + 8, self.y + 2, self.x + 16, self.y + 10, fill="#FF0000")
        
        return sprite
    
    def update(self, platforms):
        """Update power-up physics"""
        # Apply gravity
        self.y_velocity += self.gravity
        
        # Update position
        self.x += self.x_velocity
        self.y += self.y_velocity
        
        # Reverse direction at screen edges
        if self.x <= 0 or self.x >= 1000 - self.width:
            self.x_velocity *= -1
        
        # Check platform collisions
        for platform in platforms:
            if self.check_platform_collision(platform):
                break
        
        # Update sprite position
        self.canvas.coords(self.sprite, self.x, self.y, 
                          self.x + self.width, self.y + self.height)
    
    def check_platform_collision(self, platform):
        """Check collision with platform"""
        if (self.x + self.width > platform.x and self.x < platform.x + platform.width and
            self.y + self.height > platform.y and self.y < platform.y + platform.height):
            
            if self.y_velocity > 0:
                self.y = platform.y - self.height
                self.y_velocity = 0
                return True
        return False
    
    def check_collision(self, mario):
        """Check collision with Mario"""
        return (self.x < mario.x + mario.width and
                self.x + self.width > mario.x and
                self.y < mario.y + mario.height and
                self.y + self.height > mario.y)
    
    def destroy(self):
        """Remove power-up from canvas"""
        self.canvas.delete(self.sprite)


class Goomba:
    def _init_(self, x, y, canvas):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = 28
        self.height = 28
        self.speed = 1.5
        self.direction = random.choice([-1, 1])
        self.y_velocity = 0
        self.gravity = 0.5
        
        self.sprite_parts = []
        self.create_sprite()
    
    def create_sprite(self):
        """Create Goomba sprite"""
        # Clear previous sprite
        for part in self.sprite_parts:
            self.canvas.delete(part)
        self.sprite_parts = []
        
        # Body
        body = self.canvas.create_oval(
            self.x, self.y, self.x + self.width, self.y + self.height,
            fill="#8B4513", outline="black", width=2
        )
        
        # Eyes
        eye1 = self.canvas.create_oval(
            self.x + 6, self.y + 8, self.x + 12, self.y + 14, fill="black"
        )
        eye2 = self.canvas.create_oval(
            self.x + 16, self.y + 8, self.x + 22, self.y + 14, fill="black"
        )
        
        # Angry eyebrows
        brow = self.canvas.create_line(
            self.x + 4, self.y + 6, self.x + 24, self.y + 6,
            fill="black", width=3
        )
        
        self.sprite_parts = [body, eye1, eye2, brow]
    
    def update(self, platforms):
        """Update Goomba movement"""
        # Apply gravity
        self.y_velocity += self.gravity
        
        # Move horizontally
        self.x += self.speed * self.direction
        self.y += self.y_velocity
        
        # Reverse at screen edges
        if self.x <= 0 or self.x >= 1000 - self.width:
            self.direction *= -1
        
        # Check platform collisions
        for platform in platforms:
            if self.check_platform_collision(platform):
                break
        
        # Update sprite
        self.create_sprite()
    
    def check_platform_collision(self, platform):
        """Check collision with platform"""
        if (self.x + self.width > platform.x and self.x < platform.x + platform.width and
            self.y + self.height > platform.y and self.y < platform.y + platform.height):
            
            if self.y_velocity > 0:
                self.y = platform.y - self.height
                self.y_velocity = 0
                return True
        return False
    
    def check_collision(self, mario):
        """Check collision with Mario"""
        return (self.x < mario.x + mario.width and
                self.x + self.width > mario.x and
                self.y < mario.y + mario.height and
                self.y + self.height > mario.y)
    
    def destroy(self):
        """Remove Goomba from canvas"""
        for part in self.sprite_parts:
            self.canvas.delete(part)


class Coin:
    def _init_(self, x, y, canvas):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.animation_frame = 0
        
        self.sprite = self.create_sprite()
    
    def create_sprite(self):
        """Create animated coin sprite"""
        # Spinning effect with different sizes
        size_offset = math.sin(self.animation_frame * 0.2) * 2
        return self.canvas.create_oval(
            self.x - size_offset, self.y - size_offset, 
            self.x + self.width + size_offset, self.y + self.height + size_offset,
            fill="gold", outline="orange", width=2
        )
    
    def update(self, camera_x=0):
        """Update coin animation"""
        self.animation_frame += 1
        
        # Update sprite for animation
        self.canvas.delete(self.sprite)
        self.sprite = self.create_sprite()
    
    def check_collision(self, mario):
        """Check collision with Mario"""
        return (self.x < mario.x + mario.width and
                self.x + self.width > mario.x and
                self.y < mario.y + mario.height and
                self.y + self.height > mario.y)
    
    def destroy(self):
        """Remove coin from canvas"""
        self.canvas.delete(self.sprite)


if _name_ == "_main_":
    game = MarioGame()
    game.run()
