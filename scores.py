import json
import os
import time

HIGHSCORE_FILE = "highscores.json"

class ScoreManager:
    def __init__(self):
        # Check for Snap environment
        snap_data = os.environ.get('SNAP_USER_DATA')
        if snap_data:
            self.filename = os.path.join(snap_data, 'highscores.json')
        else:
            self.filename = 'highscores.json'
        self.scores = self.load_scores()

    def load_scores(self):
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except:
            return []

    def save_score(self, score: int, moves: int):
        entry = {
            "score": score,
            "moves": moves,
            "date": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.scores.append(entry)
        # Sort by score descending
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        # Keep top 10
        self.scores = self.scores[:10]
        
        with open(self.filename, 'w') as f:
            json.dump(self.scores, f, indent=2)

    def get_high_scores(self):
        return self.scores
