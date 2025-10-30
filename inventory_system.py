"""
A simple command-line inventory management system.

This module allows users to add, remove, and check the quantity of items
in an inventory. The inventory is persisted to a JSON file.
"""

import json
import logging

# --- Setup Logging ---
# Configure logging to print to console with a clear format
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Global variable
stock_data = {}


def add_item(item, qty):
    """Adds a given quantity of an item to the stock."""

    # --- Type and Value Validation ---
    if not isinstance(item, str) or not item:
        logging.error("Invalid item name: %s. Item must be a non-empty string.", item)
        return
    if not isinstance(qty, int):
        logging.error("Invalid quantity: %s for item '%s'. Must be an integer.",
                      qty, item)
        return
    if qty <= 0:
        logging.warning("Invalid quantity: %s. Must be positive. No action taken.", qty)
        return

    # --- Logic ---
    stock_data[item] = stock_data.get(item, 0) + qty
    logging.info("Added %d of '%s'. New total: %d",
                 qty, item, stock_data[item])


def remove_item(item, qty):
    """Removes a given quantity of an item from the stock."""

    # --- Type and Value Validation ---
    if not isinstance(item, str) or not item:
        logging.error("Invalid item name: %s. Item must be a non-empty string.", item)
        return
    if not isinstance(qty, int):
        logging.error("Invalid quantity: %s for item '%s'. Must be an integer.",
                      qty, item)
        return
    if qty <= 0:
        logging.warning("Invalid quantity: %s. Must be positive.", qty)
        return

    # --- Logic with Explicit Checks ---
    if item not in stock_data:
        logging.warning("Attempted to remove non-existent item: '%s'.", item)
        return

    current_qty = stock_data[item]

    if qty > current_qty:
        logging.warning("Attempted to remove %d of '%s', but only %d exist. "
                        "Removing all.", qty, item, current_qty)
        del stock_data[item]
        logging.info("Removed all %d of '%s'.", current_qty, item)
    elif qty == current_qty:
        del stock_data[item]
        logging.info("Removed all %d of '%s'. Stock is now 0.", qty, item)
    else:
        stock_data[item] -= qty
        logging.info("Removed %d of '%s'. New total: %d",
                     qty, item, stock_data[item])


def get_qty(item):
    """Safely gets the quantity of an item. Returns 0 if item not found."""
    return stock_data.get(item, 0)


def load_data(file="inventory.json"):
    """
    Loads inventory data from a JSON file.
    Returns a dictionary with the loaded data or an empty dictionary on error.
    """
    try:
        # Use 'with' and specify encoding
        with open(file, "r", encoding="utf-8") as f:
            data = f.read()
            if not data:
                # Handle empty file
                logging.warning("File '%s' is empty. Initializing empty inventory.", file)
                return {}
            stock = json.loads(data)
            logging.info("Successfully loaded data from '%s'.", file)
            return stock
    except FileNotFoundError:
        logging.warning("File not found: '%s'. Starting with empty inventory.", file)
    except json.JSONDecodeError:
        logging.error("Error decoding JSON from '%s'. File may be corrupt.", file)
    except (IOError, OSError) as e:
        logging.error("An unexpected error occurred while loading data: %s", e)
    return {}


def save_data(file="inventory.json"):
    """Saves the current inventory data to a JSON file."""
    try:
        # Use 'with' and specify encoding
        with open(file, "w", encoding="utf-8") as f:
            # indent=4 makes the JSON file human-readable
            f.write(json.dumps(stock_data, indent=4))
        logging.info("Successfully saved data to '%s'.", file)
    except PermissionError:
        logging.error("Permission denied. Could not write to file: '%s'.", file)
    except (IOError, OSError) as e:
        logging.error("An unexpected error occurred while saving data: %s", e)


def print_data():
    """Prints a report of the current inventory."""
    print("\n--- Items Report ---")
    if not stock_data:
        print("Inventory is empty.")
    else:
        # .items() is a cleaner way to loop through a dictionary
        for item, qty in stock_data.items():
            print(f"{item} -> {qty}")
    print("--------------------\n")


def check_low_items(threshold=5):
    """Returns a list of items with stock below the threshold."""
    result = []
    for item, qty in stock_data.items():
        # This is now safe because add_item ensures qty is an int
        if qty < threshold:
            result.append(item)
    return result


def main():
    """
    Main function to run the inventory management system test.
    """
    global stock_data  # We are assigning to the global variable
    # Load data first, in case there's a previous inventory
    stock_data = load_data()
    print_data()

    # --- Test successful additions ---
    add_item("apple", 10)
    add_item("banana", 20)
    add_item("apple", 5)  # Add more to an existing item

    # --- Test invalid inputs (will be logged and skipped) ---
    add_item("banana", -2)    # Will log warning, do nothing
    add_item(123, 10)         # Will log error, do nothing
    add_item("pear", "ten")   # Will log error, do nothing

    # --- Test removals ---
    remove_item("apple", 3)
    remove_item("orange", 1)      # Will log warning (item not found)
    remove_item("banana", 25)     # Will log warning (over-removal)

    # --- Check final quantities ---
    print("Apple stock:", get_qty("apple"))
    print("Banana stock:", get_qty("banana"))  # Should be 0
    print("Orange stock:", get_qty("orange"))  # Should be 0

    print("Low items (threshold 15):", check_low_items(threshold=15))

    print_data()
    save_data()

    # Removed eval() for security
    print("eval() function was removed for security reasons.")


# Standard Python practice to run main()
if __name__ == "__main__":
    main()