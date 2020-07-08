import string


def get_xlib_to_pyautogui_keymapping():
    # Ascii chars
    m = {x: x for x in string.ascii_lowercase + string.digits}

    # F keys
    for x in range(1, 13):
        m['f' + str(x)] = 'f' + str(x)

    # Special chars
    m['escape'] = 'escape'
    m['tab'] = 'tab'
    m['period'] = '.'
    m['minus'] = '-'
    m['comma'] = ','
    m['slash'] = '/'
    m['apostrophe'] = '\''
    m['colon'] = ':'
    m['delete'] = 'delete'
    m['underscore'] = '_'
    m['parenleft'] = '('
    m['parenright'] = ')'
    m['page_up'] = 'pageup'
    m['equal'] = '='
    m['p_add'] = 'add'
    m['semicolon'] = ';'
    m['p_subtract'] = 'subtract'
    m['quotedbl'] = '"'
    m['bracketleft'] = '['
    m['bracketright'] = ']'
    m['dollar'] = '$'
    m['numbersign'] = '#'
    m['p_down'] = 'down'
    m['p_left'] = 'left'
    m['p_enter'] = 'enter'
    m['asterisk'] = '*'
    m['home'] = 'home'
    m['end'] = 'end'
    m['grave'] = '`'
    m['less'] = '<'
    m['question'] = '?'
    m['braceleft'] = '{'
    m['braceright'] = '}'
    m['plus'] = '+'
    m['p_page_up'] = 'pageup'
    m['p_right'] = 'right'
    m['p_up'] = 'up'
    m['exclam'] = '!'
    m['backslash'] = '\\'
    m['at'] = '@'
    m['percent'] = '%'
    m['bar'] = '|'
    m['asciitilde'] = '~'
    m['num_lock'] = 'numlock'
    m['ampersand'] = '&'
    m['caps_lock'] = 'capslock'
    m['asciicircum'] = '^'
    m['p_end'] = 'end'
    m['p_insert'] = 'insert'
    m['insert'] = 'insert'
    m['p_home'] = 'home'
    m['greater'] = '>'
    m['print'] = 'print'
    m['p_delete'] = 'delete'
    m['p_multiply'] = 'multiply'
    m['p_divide'] = 'divide'
    m['next'] = 'pagedown'
    m['odiaeresis'] = 'ö'

    return m
