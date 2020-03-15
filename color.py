from colorama import Style


def color_print(color_name, display_string, display_content):
    print(color_name + display_string + " " + Style.RESET_ALL + display_content)
