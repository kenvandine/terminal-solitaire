from setuptools import setup

setup(
    name='terminal-solitaire',
    version='1.0.0',
    py_modules=['solitaire', 'game_logic', 'ui', 'scores'],
    entry_points={
        'console_scripts': [
            'terminal-solitaire=solitaire:main',
        ],
    },
)
