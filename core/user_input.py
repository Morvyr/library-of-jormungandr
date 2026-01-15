"""   
User Interaction Utilities for the Library of Jörmungandr

Functions for human-in-the-loop workflows when automated 
repair fails or user guidance is needed.

These functions provide a consistent interface for:
- Interactive text editing
- User confirmations
- Multiple choice selections
- Issue reporting and repair guidance
"""

import sys
from typing import List, Optional, Dict, Any, Tuple

def confirm_action(message: str, default: bool = True) -> bool:
    """   
    Ask user to confirm an action with yes/no.

    Args:
        message: Question to ask the user
        default: Default choice if user just press Enter (True=yes, False=no)

    Returns:
        bool: True if user confirms, False otherwise

    Example:
        >>> if confirm_action("Delete this file?", default=False)
        >>>     delete_file()
    """

    # Format the promt with default indicator
    default_indicator = "[Y/n]" if default else "[y/N]"
    prompt_text = f"{message} {default_indicator}: "

    # Get user input
    response = input(prompt_text).strip().lower()

    # Handle empty response (use default)
    if not response:
        return default
    
    # Check for yes/no
    if response in ['y', 'yes']:
        return True
    elif response in ['n', 'no']:
        return False
    else:
        # Invalid input, ask again
        print("Invalid input. Please enter 'y' or 'n'")
        return confirm_action(message, default)
    
def choose_from_list(options: List[str], message: str, allow_multiple: bool = False) -> Optional[List[int]]:
    """   
    Present a numbered list of options and let user choose.

    Args:
        options: List of option strings to display
        message: Prompt message to show above the options
        allow_multiple: If True, user can select multiple options (comma-separated)

    Returns:
        List of selected option indices(0-based), or None if user cancels

    Example:
        >>> options = ["skip this row", "Merge fields", "Edit manually"]
        >>> choices = choose_from_list(options, "What would you like to do?")
        >>> if choices and choices[0] == 0:
        >>>     skip_row()
    """    
    # Display the message
    print("\n" + "=" * 60)
    print(message)
    print("=" * 60)

    # Display numbered options
    for i, option in enumerate(options, start=1):
        print(f"  {i}. {option}")
        
    # Add cancel options
    print(f"  0. Cancel")
    print("=" * 60)

    # Get user choice
    if allow_multiple:
        prompt_text = "Enter choices (comma-separated, e.g. '1,3'): "
    else:
        prompt_text = "Enter choice: "

    response = input(prompt_text).strip()

    # Handle cancel
    if response == '0' or response.lower() in ['cancel', 'c', 'q', 'quit']:
        return None
    
    # Parse response
    try:
        if allow_multiple:
            # Split by comma and convert to integers
            choices = [int(x.strip()) for x in response.split(',')]
        else:
            # Single choice
            choices = [int(response)]

        # Validate choices are in range(1 to len(options))
        for choice in choices:
            if choice < 1 or choice > len(options):
                print(f"Invalid choice :{choice}. Must be between 1 and {len(options)}")
                return choose_from_list(options, message, allow_multiple)
            
        # Convert to 0-based indices
        return [c - 1 for c in choices]
    
    except ValueError:
        print("Invalid input. Please enter numbers only.")
        return choose_from_list(options, message, allow_multiple)
    
def edit_text_interactive(text: str, message: str = "Edit the text below:") -> Optional[str]:
    """
    Allow user to interactively edit text.

    User prompt_toolkit for best UX (editable prefilled text),
    falls back to simple input if not available.

    Args:
        text: The text to edit (will be prefilled)
        message: Instruction message to show user

    Returns:
        Edited text, or None if user cancels

    Example:
        >>> original = "Hello, world!"
        >>> edited = edit_text_interactive(original, "Fix this greeting:")
        >>> if edited:
        >>>     save(edited)
    """

    print("\n" + "=" * 60)
    print(message)
    print("=" * 60)

    # Try to use prompt_toolkit for best UX
    try:
        from prompt_toolkit import prompt

        print("(Edit the text below, press Enter when done, Ctrl+C to cancel.)")
        print()

        try: 
            edited = prompt("", default=text)
            return edited if edited else None
        except KeyboardInterrupt:
            print("\nEdit cancelled.")
            return None
        
    except ImportError:
        # Fallback: show text and ask user to type new version
        print("Current text:")
        print(f"  {text}")
        print()
        print("Enter new text (or press Enter to keep unchanged, 'cancel to abort):")

        response = input("> ").strip()

        if not response:
            # Empty input means keep original
            return text
        elif response.lower() in ['cancel', 'c', 'quit', 'q']:
            print("Edit cancelled.")
            return None
        else:
            return response
        
def edit_line_interactive(line: str, line_number: int = 0) -> Optional[str]:
    """   
    Let user edit a specific CSV line interactively.

    This is a convenience wrapper around edit_text_interactive()
    specifically for CSV line editing.

    Args:
        line: The CSV line to edit
        line_number: Line number in file (for display, optional)

    Returns:
        Edited line, or None if user cancels

    Example:
        >>> bad_line = "1001,john,Laptop,$1,299.99"
        >>> fixed = edit_line_interactive(bad_line, line_number=2)
        >>> if fixed:
        >>>     update_csv(2, fixed)
    """

    # Build a helpful message
    if line_number > 0:
        message = f"Edit CSV line {line_number}:"
    else:
        message = "Edit this CSV line"

    # Add context about what we're looking for
    print("\nCommon fixes:")
    print("  - Add quotes around values with commas: Laptop, $1,299.99 -> Laptop,\"$1,299.99\"")
    print("  - Remove extra commas: Laptop, $1,299.99 -> Laptop, $1299.99 ")
    print("  - Close open ended quotes: john smith,Laptop Pro 15\" - > john smith,\"Laptop Pro 15\"")
    print()

    # Call the generic edit function
    return edit_text_interactive(line, message)

def show_issue_and_prompt_fix(
        issue_description: str,
        problematic_content: str,
        suggested_fixes: List[str],
        allow_edit: bool = True
) -> Optional[Dict[str, Any]]:
    """   
    Show user an issue and promt for how to fix it.

    This is a generic issue handler that can be used for any type of
    problem that needs user intervention.

    Args: 
        issue_description: Description of the problem
        problematic_content: The actual content causing the issue
        suggested_fixes: List of suggested fix options
        allow_edit: If True, include "Edit manually" option

    Returns:
        Dictionary with fix decision:
        {
            'action': 'skip' | 'apply_fix' | 'edit' | 'cancel',
            'fix_index': int(if action is 'apply_fix'),
            'edited_content': str (if action is 'edit')        
        }
        Returns None if User cancels

    Example:
        >>> issue = "Line has 12 fields but the header has 11"
        >>> content = "1001,John, Laptop,$1299.99,..."
        >>> fixes = [
                "Add quotations: ...$1,299.99 -> ...\"1,299.99\"",
                "Remove comma: ...$1,299.99 -> ...$1299.99          
        ]
        result = show_issue_and_prompt_fix(issue, content, fixes)
        if result['action'] == 'apply_fix':
            apply_fix_number(result['fix_index'])
    """

    # Show the issue
    print("\n" + "=" * 60)
    print("ISSUE DETECTED")
    print("=" * 60)
    print(f"Problem: {issue_description}")
    print()
    print("Content:")
    print(f"  {problematic_content}")
    print("=" * 60)

    # Build options list
    options = []

    #Add suggested fixes
    for fix in suggested_fixes:
        options.append(f"Apply fix: {fix}")

    # Add edit option if allowed
    if allow_edit:
        options.append("edit manually")

    # Always add skip option
    options.append("skip this issue (leave unchanged)")

    # Get user choice
    choices = choose_from_list(options, "How would you like to proceed?")

    if choices is None:
        # User cancelled
        return None
    
    choice_index = choices[0] # We only allow a single selection

    # Determine what action was chosen
    num_fixes = len(suggested_fixes)

    if choice_index < num_fixes:
        # User chose one of the suggested fixes
        return {
            'action': 'apply_fix',
            'fix_index': choice_index
        }
    
    elif allow_edit and choice_index == num_fixes:
        # User chose "Edit manually"
        edited = edit_text_interactive(problematic_content, "Edit the content:")

        if edited is None:
            # User cancelled the edit
            return None
        
        return {
            'action': 'edit',
            'edited_content': edited
        }
    
    else:
        # User chose "Skip"
        return {
            'action': 'skip'
        }

    