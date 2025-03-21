import time
import system

def countdown_from(start=5):
    """
    Display a countdown from the specified number to 0 on the OLED screen.
    Counts down one number per second.
    """
    system.oledclear()
    system.oledprint(f"Countdown starting")
    time.sleep(1)
    
    for i in range(start, -1, -1):
        system.oledclear()
        system.oledprint(f"Countdown: {i}")
        if i > 0:  # Don't sleep after the last number
            time.sleep(1)
    
    # Display "Returning to menu" before actually returning
    system.oledclear()
    system.oledprint("Countdown complete!\nReturning to menu...")
    time.sleep(1.5)  # Show the return message for 1.5 seconds
    
    return None  # Return None so the menu system will display the default menu