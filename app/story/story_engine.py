from app.story.story_loader import load_chapter, load_choice_mapping

class Story:
    def __init__(self):
        self.chapter = 0
        self.choice_map = load_choice_mapping()

    def get_chapter(self, chapter_id):
        return load_chapter(chapter_id)

    def choose_path(self, choice):
        return self.choice_map.get(choice, 0)