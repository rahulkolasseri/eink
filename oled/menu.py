import system, asyncio, time
from countdown import countdown_from
import webserver

class MenuItem:
    def __init__(self, name, callback):
        self.name = name
        self.callback = callback

class Menu:
    def __init__(self):
        self.state = "Hello"  # Initial state: just shows "hello"
        self.menu_active = False
        self.selected_index = 0
        self.menu_items = [
            MenuItem("Display random image", self.display_random_image),
            MenuItem("Start web server", self.start_web_server),
            MenuItem("Countdown from 5", self.start_countdown),
            MenuItem("Shutdown", self.shutdown)
        ]
    
    def handle_short_press(self):
        """Handle short press: enter menu or move selection"""
        if not self.menu_active:
            # If not in menu mode, activate it
            self.menu_active = True
            self.selected_index = 0
        else:
            # If in menu mode, move selection down (with wraparound)
            self.selected_index = (self.selected_index + 1) % len(self.menu_items)
        
        return self.get_display_text()
    
    def handle_long_press(self):
        """Handle long press: select current menu item"""
        if self.menu_active:
            # Execute the callback for the selected item
            selected_item = self.menu_items[self.selected_index]
            selected_item.callback()  # Execute callback but don't use return value
            
            # Return to initial state
            self.menu_active = False
            self.selected_index = 0
            
            # Return to default menu display regardless of callback result
            return self.get_display_text()
            
        return self.get_display_text()
    
    def get_display_text(self):
        """Get the current text to display"""
        if not self.menu_active:
            return "hello"
        
        # Build menu text with selection indicator
        menu_text = ""
        for i, item in enumerate(self.menu_items):
            prefix = "> " if i == self.selected_index else ""
            menu_text += f"{prefix}{item.name}\n"
        
        return menu_text.strip()
    
    # Placeholder functions for menu options
    def display_random_image(self):
        # This would be implemented to display a random image
        return "Displaying random image..."
    
    def start_web_server(self):
        # Start the web server in a blocking way
        webserver.start_server()
        return "Web server stopped"
    
    def shutdown(self):
        return "Shutting down..."
        time.sleep(2)
        system.sleeptimeforever()
    
    # New countdown function that uses the countdown module
    def start_countdown(self):
        return countdown_from(5)


async def menuStart():
    # Initialize menu
    menu = Menu()
    
    # Define callback functions for button presses
    async def on_short_press():
        system.oledclear()
        display_text = menu.handle_short_press()
        system.oledprint(display_text)
        system.pulse_vibe_motor(65)
        
    async def on_long_press():
        system.oledclear()
        display_text = menu.handle_long_press()
        display_text = menu.handle_short_press()  # Update click out of start screen
        system.oledprint(display_text)
    
    # Set up button handlers
    button = system.Pushbutton(system.TOUCH_BUTTON, suppress=True)
    button.release_func(on_short_press)
    button.long_func(on_long_press)
    
    # Show initial display
    system.oledclear()
    system.oledprint(menu.get_display_text())
    
    # Keep the coroutine running
    while True:
        await asyncio.sleep(1)


# Example usage:
if __name__ == "__main__":
    # Create menu instance
    menu = Menu()
    
    # Simulate interaction
    print("Initial state:")
    print(menu.get_display_text())
    
    print("\nAfter short press (enter menu):")
    print(menu.handle_short_press())
    
    print("\nAfter short press (move selection):")
    print(menu.handle_short_press())
    
    print("\nAfter long press (select option):")
    print(menu.handle_long_press())