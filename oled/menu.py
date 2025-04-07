import system, asyncio, time
import webserver
from epdscreen.displayepd import display, pickbin
from system import wri, ssd

# Update debug helper to print to console instead of OLED
def debug_print(message):
    isdebug = False  # Set to True to enable debug messages
    """Print debug message to console"""
    if isdebug:
        # Only print if debug mode is enabled
        print(f"DEBUG: {message}")
    

class MenuItem:
    def __init__(self, name, callback):
        self.name = name
        self.callback = callback

class Menu:
    def __init__(self):
        self.state = "Hello"  # Initial state: just shows "hello"
        self.menu_active = False
        self.selected_index = 0
        self.current_page = 0
        self.server_running = False
        self.confirm_dialog = False
        self.server_task = None
        self.in_image_menu = False
        self.image_files = []
        self.items_per_page = 5  # Maximum items per page
        # Initialize menu items
        self.main_menu_items = [
            MenuItem("Display random image", self.display_random_image),
            MenuItem("Select image", self.enter_image_selection),
            MenuItem("Start web server", self.start_web_server),
            MenuItem("Shutdown", self.shutdown)
        ]
        self.server_menu_items = [
            MenuItem("Shutdown server", self.prompt_shutdown_server)
        ]
        self.confirm_items = [
            MenuItem("Yes", self.shutdown_server),
            MenuItem("No", self.cancel_shutdown)
        ]
    
    def get_current_menu_items(self):
        """Get the complete list of current menu items based on state"""
        if self.confirm_dialog:
            return self.confirm_items
        elif self.server_running:
            return self.server_menu_items
        elif self.in_image_menu:
            return self.image_menu_items
        else:
            return self.main_menu_items
    
    def get_visible_items(self):
        """Get only the items visible on the current page"""
        all_items = self.get_current_menu_items()
        
        debug_print(f"Total items: {len(all_items)}, Page: {self.current_page}/{self.get_total_pages()}")
        
        # For image menu, we handle pagination differently to always include "Back" option
        if self.in_image_menu:
            # First page is special case
            if self.current_page == 0:
                # First page shows "Back" and up to items_per_page-1 images
                result = all_items[:self.items_per_page]
                debug_print(f"Image menu page 0: showing items 0-{min(self.items_per_page, len(all_items))-1}")
                return result
            else:
                # Subsequent pages always include "Back" as first item
                visible = [all_items[0]]  # Back option
                
                # Calculate which images to show on this page
                effective_items_per_page = self.items_per_page - 1  # Reserve space for "Back"
                # First page shows items 1 through effective_items_per_page
                # Second page (index 1) should start from item effective_items_per_page+1
                first_page_image_count = min(effective_items_per_page, len(all_items)-1)
                start_item = 1 + first_page_image_count + (self.current_page - 1) * effective_items_per_page
                end_item = min(start_item + effective_items_per_page, len(all_items))
                
                debug_print(f"Image menu page {self.current_page}: first_page_count={first_page_image_count}, showing Back + items {start_item}-{end_item-1}")
                
                # Add the proper items for this page
                visible.extend(all_items[start_item:end_item])
                return visible
        else:
            # Regular pagination for other menus
            start_idx = self.current_page * self.items_per_page
            end_idx = min(start_idx + self.items_per_page, len(all_items))
            result = all_items[start_idx:end_idx]
            debug_print(f"Regular menu page {self.current_page}: showing items {start_idx}-{end_idx-1}")
            return result
    
    def get_total_pages(self):
        """Calculate total number of pages for current menu"""
        all_items = self.get_current_menu_items()
        
        if self.in_image_menu:
            # We have a "Back" button plus images
            total_images = len(all_items) - 1
            
            if total_images <= 0:
                return 1  # Just one page with only "Back" button
                
            # First page can show "Back" plus up to (items_per_page-1) images
            first_page_capacity = self.items_per_page - 1
            first_page_images = min(first_page_capacity, total_images)
            remaining_images = total_images - first_page_images
            
            # Each subsequent page shows "Back" plus up to (items_per_page-1) images
            subsequent_page_capacity = self.items_per_page - 1
            additional_pages = (remaining_images + subsequent_page_capacity - 1) // subsequent_page_capacity if remaining_images > 0 else 0
            
            total = 1 + additional_pages  # First page + additional pages
            debug_print(f"Image menu pages: {total} (total_images={total_images}, first_page={first_page_images}, remaining={remaining_images})")
            return total
        else:
            # Regular pagination for other menus
            if not all_items:
                return 1
            total = (len(all_items) + self.items_per_page - 1) // self.items_per_page
            debug_print(f"Regular menu pages: {total}")
            return total
    
    def get_current_page(self):
        """Return the current page number"""
        return self.current_page
    
    def handle_short_press(self):
        """Handle short press: enter menu or move selection"""
        if not self.menu_active:
            # If not in menu mode, activate it
            self.menu_active = True
            self.selected_index = 0
            self.current_page = 0
        else:
            # Move to next visible item
            visible_items = self.get_visible_items()
            old_index = self.selected_index
            
            # Determine if we should move to the next page
            if self.selected_index >= len(visible_items) - 1:
                # We're at the last item, check if there are more pages
                total_pages = self.get_total_pages()
                if total_pages > 1:
                    debug_print(f"Last item reached, checking page transition. Current: {self.current_page}, Total: {total_pages}")
                    
                    # Calculate next page
                    next_page = (self.current_page + 1) % total_pages
                    self.current_page = next_page
                    self.selected_index = 0  # Reset selection for new page
                    
                    debug_print(f"Moving to page {next_page}")
                else:
                    # Only one page, just wrap around selection
                    self.selected_index = 0
            else:
                # Not at the end of the page, just increment selection
                self.selected_index += 1
            
            # Debug selection state
            debug_print(f"Select: {old_index}->{self.selected_index}, Page: {self.current_page}")
        
        return self.get_display_text()
    
    def handle_long_press(self):
        """Handle long press: select current menu item"""
        if self.menu_active:
            # Get the currently visible items and select the right one
            visible_items = self.get_visible_items()
            if 0 <= self.selected_index < len(visible_items):
                selected_item = visible_items[self.selected_index]
                result = selected_item.callback()
                
                # Return to initial state only if we're not in a special menu
                if not self.confirm_dialog and not self.server_running and not self.in_image_menu:
                    self.menu_active = False
                    self.selected_index = 0
                    self.current_page = 0
                
                return result
        
        return self.get_display_text()
    
    def get_display_text(self):
        """Get the current text to display with pagination"""
        global pagenumber
        if not self.menu_active:
            return "hello"
        
        # Get visible items for current page
        visible_items = self.get_visible_items()
        
        # Build menu text
        menu_text = ""
        
        # Add context-specific headers
        if self.confirm_dialog:
            menu_text = "Confirm shutdown?\n\n"
        elif self.server_running:
            # Show IP address when server is running
            from system import ipaddr
            ip = ipaddr()
            menu_text = f"Server: {ip}\n\n"
        elif self.in_image_menu:
            menu_text = "Select image:\n"
        
        # Add menu items with selection indicator
        for i, item in enumerate(visible_items):
            prefix = "> " if i == self.selected_index else "  "
            menu_text += f"{prefix}{item.name}\n"
        
        # Set page indicator for multi-page menus (but don't add to text)
        total_pages = self.get_total_pages()
        if total_pages > 1:
            pagenumber = f"{self.current_page + 1}/{total_pages}"
        else:
            pagenumber = None
        
        return menu_text.strip()
    
    def enter_image_selection(self):
        """Enter the image selection submenu"""
        try:
            import os
            # Get list of .bin files
            self.image_files = [f for f in os.listdir("/bins") if f.endswith('.bin')]
            
            # Debug available images
            debug_print(f"Found {len(self.image_files)} images")
            
            # Create menu items dynamically
            self.image_menu_items = [
                MenuItem("Back to main menu", self.exit_image_selection)
            ]
            
            # Add all image items - fix closure issue by creating function
            for img_file in self.image_files:
                # Create a function that captures the current value of img_file
                def make_callback(filename):
                    return lambda: self.display_selected_image(filename)
                
                self.image_menu_items.append(
                    MenuItem(self.truncate_filename(img_file), make_callback(img_file))
                )
            
            # Debug menu items
            debug_print(f"Menu items: {len(self.image_menu_items)}")
            
            # Enter image menu mode
            self.in_image_menu = True
            self.selected_index = 0
            self.current_page = 0
            return "Select an image:"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def truncate_filename(self, filename, max_length=18):
        """Truncate filename if it's longer than max_length chars"""
        if len(filename) > max_length:
            return filename[:max_length-3] + ".."
        return filename
    
    def exit_image_selection(self):
        """Exit the image selection submenu"""
        self.in_image_menu = False
        self.selected_index = 0
        return "Returning to main menu"
    
    def display_selected_image(self, image_name):
        """Display the selected image"""
        path = f"/bins/{image_name}"
        try:
            # Clear OLED and show feedback before blocking call
            system.oledclear()
            system.oledprint(f"Displaying {self.truncate_filename(image_name)}...")
            
            # Now make the blocking display call
            display(path)
            
            return f"Displayed {self.truncate_filename(image_name)}"
        except Exception as e:
            system.oledprint(f"Error: {str(e)}")
            return f"Error displaying image: {str(e)}"
    
    def display_random_image(self):
        """Display a random image from bins directory"""
        image = pickbin()
        if image:
            path = f"/bins/{image}"
            
            # Clear OLED and show feedback before blocking call
            system.oledclear()
            system.oledprint(f"Displaying {self.truncate_filename(image)}...")
            
            # Now make the blocking display call
            display(path)
            
            return f"Displayed {self.truncate_filename(image)}"
        else:
            system.oledprint("No images found")
            return "No images found"
    
    # Web server control functions
    def start_web_server(self):
        """Start the web server without blocking the menu"""
        system.oledclear()
        system.oledprint("Starting server...")
        
        # Create a task that runs the server in the background
        self.server_task = asyncio.create_task(webserver.run_server(autoconnect=True))
        
        # Update menu state
        self.server_running = True
        self.selected_index = 0
        
        return "Server starting..."
    
    def prompt_shutdown_server(self):
        """Show confirmation dialog for server shutdown"""
        self.confirm_dialog = True
        self.selected_index = 0
        return "Confirm shutdown?"
    
    def shutdown_server(self):
        """Shutdown the server and return to main menu"""
        system.oledclear()
        system.oledprint("Shutting down server...")
        
        # Cancel the server task first
        if self.server_task:
            self.server_task.cancel()
            self.server_task = None
        
        # Attempt to send shutdown signal with a timeout
        try:
            import requests # type: ignore
            # Try to hit the shutdown endpoint with a 1-second timeout
            requests.get('http://localhost/shutdown', timeout=1)
        except Exception:
            # Ignore errors (e.g., timeout, connection refused, ImportError)
            # Task cancellation is the primary mechanism
            pass
        
        # Reset menu state
        self.server_running = False
        self.confirm_dialog = False
        self.selected_index = 0
        self.menu_active = True # Keep menu active after server shutdown
        
        return "Server stopped"
    
    def cancel_shutdown(self):
        """Cancel the shutdown and return to server menu"""
        self.confirm_dialog = False
        self.selected_index = 0
        return "Shutdown cancelled"
    
    def shutdown(self):
        """Shutdown the device"""
        system.oledclear()
        system.oledprint("Shutting down...")
        
        # Don't return immediately so the other code can execute
        time.sleep(2)
        system.sleeptimeforever()
        return "Shutting down..."  # This will only execute if sleeptimeforever fails

    def check_server_status(self):
        """Check if the server task is still running and update menu state if needed"""
        if self.server_running and self.server_task:
            # Check if the task has completed - in MicroPython we can only check done()
            # The cancelled() method isn't available in MicroPython's asyncio implementation
            if self.server_task.done():
                debug_print("Server task completed externally - updating menu state")
                # Update menu state
                self.server_running = False
                self.confirm_dialog = False
                self.selected_index = 0
                
                # Return true if state changed
                return True
        return False


async def menuStart():    
    # Initialize menu and global page indicator variable
    global pagenumber 
    pagenumber = None
    menu = Menu()
    x = 50
    y = 108
    
    # Define callback functions for button presses
    async def on_short_press():
        result = menu.handle_short_press()
        system.oledclear()
        await system.pulse_vibe_motor(80)  # Vibration feedback
        system.oledprint(result)  # Use the returned display text
        
        # Add page number in bottom right AFTER printing the main text
        if pagenumber:
            # Save current cursor position
            curr_x, curr_y = wri.get_text_position(ssd)
            debug_print(f"Current cursor position: {curr_x}, {curr_y}")
            
            # Set position to bottom right for page number (Y depends on screen height)
            # Setting y=115 puts it near the bottom and x=90 puts it on the right
            wri.set_textpos(ssd, x, y)
            wri.printstring(pagenumber)
            debug_print(f"{pagenumber} printed at position: {x}, {y}")
            
            # Restore cursor position (without printing anything)
            wri.set_textpos(ssd, curr_x, curr_y)
            debug_print(f"Cursor position restored to: {curr_x}, {curr_y}")
            
            # Update the display
            ssd.show()
        
    async def on_long_press():
        await system.pulse_vibe_motor(150)
        result = menu.handle_long_press()
        system.oledclear()
        system.oledprint(result)  # Use the returned result directly
        result = menu.handle_short_press()
        system.oledclear()
        system.oledprint(result)
        # Add page number AFTER printing the main text
        if pagenumber:
            # Save current cursor position
            curr_x, curr_y = wri.get_text_position(ssd)
            debug_print(f"Current cursor position: {curr_x}, {curr_y}")
            
            # Set position to bottom right for page number
            wri.set_textpos(ssd, x, y)
            wri.printstring(pagenumber)
            debug_print(f"{pagenumber} printed at position: {x}, {y}")
            
            # Restore cursor position
            wri.set_textpos(ssd, curr_x, curr_y)
            debug_print(f"Cursor position restored to: {curr_x}, {curr_y}")
            
            # Update the display
            ssd.show()

    # Set up button handlers
    button = system.Pushbutton(system.TOUCH_BUTTON, suppress=True)
    button.release_func(on_short_press)
    button.long_func(on_long_press)
    
    # Show initial display
    system.oledclear()
    system.oledprint(menu.get_display_text())
    
    # Keep the coroutine running and check server status periodically
    last_check_time = 0
    check_interval = 2  # Check server status every 2 seconds
    
    while True:
        # Only check server status if the server is running
        if menu.server_running:
            current_time = time.time()
            
            # Check server status periodically with rate limiting
            if current_time - last_check_time >= check_interval:
                # If server status changed, update the display
                if menu.check_server_status():
                    debug_print("Server status changed, updating display")
                    system.oledclear()
                    system.oledprint(menu.get_display_text())
                    
                    # Add page number in bottom right
                    if pagenumber:
                        curr_x, curr_y = wri.get_text_position()
                        wri.set_textpos(ssd, 58, 90)
                        wri.printstring(pagenumber)
                        wri.set_textpos(ssd, curr_x, curr_y)
                        ssd.show()
                    
                last_check_time = current_time
        
        await asyncio.sleep(0.1)  # Non-blocking sleep to allow other operations


# Example usage:
if __name__ == "__main__":
    # Create menu instance
    menu = Menu()