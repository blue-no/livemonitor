class Color:
    RED = [
        '#fc8f59',
        '#f6735f',
        '#ed555a',
        '#e33f5c',
        '#d02964',
    ],
    GREEN = [
        '#35bc88',
        '#20ae7c',
        '#1ba37d',
        '#13947d',
        '#0b7e7f',
    ],
    BLUE = [
        '#1ed7cd',
        '#18c4b8',
        '#05a7be',
        '#087ea2',
        '#017598',
    ],
    PURPLE = [
        '#d876a9',
        '#c967a2',
        '#9c539c',
        '#804595',
        '#6a398c',
    ],
    WHEEL12 = [
        '#B5184F',
        '#DD3737',
        '#E66D00',
        '#EEAC00',
        '#C8BB00',
        '#4AA315',
        '#008C69',
        '#007C8C',
        '#005A91',
        '#00509D',
        '#663E8C',
        '#892C71',
    ]


def code_to_rgb(code):
    c = code.lstrip('#')
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:], 16))
