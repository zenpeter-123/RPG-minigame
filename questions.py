"""
Question database for the Sphinx
Types: math, history, literature
Difficulties: easy, medium, hard
"""

import random
from typing import Dict, List, Optional


QUESTIONS = {
    "math": {
        "easy": [
            {
                "question": "What is 5! (5 factorial)?",
                "options": ["20", "60", "120", "240"],
                "correct_index": 2
            },
            {
                "question": "What is the square root of 144?",
                "options": ["10", "11", "12", "13"],
                "correct_index": 2
            },
            {
                "question": "What is the sum of the interior angles of a triangle?",
                "options": ["90°", "180°", "270°", "360°"],
                "correct_index": 1
            },
            {
                "question": "What is 2^10?",
                "options": ["512", "1024", "2048", "4096"],
                "correct_index": 1
            },
            {
                "question": "What is 25% of 200?",
                "options": ["25", "40", "50", "75"],
                "correct_index": 2
            },
            {
                "question": "Which number is prime?",
                "options": ["9", "15", "21", "23"],
                "correct_index": 3
            },
            {
                "question": "What is 7 × 8 × 9?",
                "options": ["504", "512", "624", "728"],
                "correct_index": 0
            },
            {
                "question": "A circle has an area of 16π. What is its radius?",
                "options": ["2", "4", "8", "16"],
                "correct_index": 1
            }
        ],
        "medium": [
            {
                "question": "Solve: 2x + 5 = 17, x = ?",
                "options": ["4", "5", "6", "7"],
                "correct_index": 2
            },
            {
                "question": "A rectangle has sides of 12 cm and 5 cm. What is its diagonal?",
                "options": ["10 cm", "13 cm", "15 cm", "17 cm"],
                "correct_index": 1
            },
            {
                "question": "What is 3^4 × 3^2?",
                "options": ["3^6", "3^8", "9^6", "9^8"],
                "correct_index": 0
            },
            {
                "question": "A geometric sequence starts with 3 and has ratio 2. What is the 6th term?",
                "options": ["48", "96", "192", "384"],
                "correct_index": 1
            },
            {
                "question": "What is 0.75 as a fraction?",
                "options": ["1/4", "3/4", "2/3", "5/8"],
                "correct_index": 1
            },
            {
                "question": "What is the derivative of x²?",
                "options": ["2x", "x²", "2", "x"],
                "correct_index": 0
            },
            {
                "question": "What is 20% of 80?",
                "options": ["12", "14", "16", "18"],
                "correct_index": 2
            },
            {
                "question": "How many sides does a hexagon have?",
                "options": ["4", "5", "6", "7"],
                "correct_index": 2
            }
        ],
        "hard": [
            {
                "question": "A ball thrown vertically has height h(t) = -5t² + 20t + 2. When does it reach maximum height?",
                "options": ["1 s", "2 s", "3 s", "4 s"],
                "correct_index": 1
            },
            {
                "question": "What is ∫(3x² - 4x + 1) dx?",
                "options": ["x³ - 2x² + x + C", "x³ - 4x² + x + C", "3x³ - 2x² + x + C", "x³ - 2x² + 1 + C"],
                "correct_index": 0
            },
            {
                "question": "If a matrix has determinant 0, what does that mean?",
                "options": [
                    "The matrix is invertible",
                    "The matrix is singular",
                    "The matrix is identity",
                    "The matrix is symmetric"
                ],
                "correct_index": 1
            },
            {
                "question": "What is sin(45°)?",
                "options": ["1/2", "√2/2", "√3/2", "1"],
                "correct_index": 1
            },
            {
                "question": "Solve: log₂(x) + log₂(x-2) = 3",
                "options": ["x = 4", "x = 8", "x = 2", "x = 6"],
                "correct_index": 0
            },
            {
                "question": "What is the eigenvalue of a 2x2 identity matrix?",
                "options": ["0", "1", "-1", "2"],
                "correct_index": 1
            },
            {
                "question": "What is the limit of (1 + 1/n)^n as n approaches infinity?",
                "options": ["e", "π", "√2", "1"],
                "correct_index": 0
            },
            {
                "question": "What is the complex conjugate of 3 + 4i?",
                "options": ["3 - 4i", "-3 + 4i", "3 + 4i", "-3 - 4i"],
                "correct_index": 0
            }
        ]
    },
    
    "history": {
        "easy": [
            {
                "question": "When did World War I begin?",
                "options": ["1912", "1914", "1916", "1918"],
                "correct_index": 1
            },
            {
                "question": "Who was the first President of the United States?",
                "options": ["Thomas Jefferson", "George Washington", "Benjamin Franklin", "John Adams"],
                "correct_index": 1
            },
            {
                "question": "Which civilization built the pyramids?",
                "options": ["Greek", "Roman", "Egyptian", "Mesopotamian"],
                "correct_index": 2
            },
            {
                "question": "When was the Magna Carta signed?",
                "options": ["1215", "1315", "1415", "1515"],
                "correct_index": 0
            },
            {
                "question": "Who was the first Roman emperor?",
                "options": ["Augustus", "Julius Caesar", "Caligula", "Nero"],
                "correct_index": 0
            },
            {
                "question": "When was America discovered?",
                "options": ["1392", "1492", "1592", "1692"],
                "correct_index": 1
            },
            {
                "question": "Who wrote 'War and Peace'?",
                "options": ["Dostoevsky", "Tolstoy", "Pushkin", "Chekhov"],
                "correct_index": 1
            },
            {
                "question": "Which ancient wonder was located in Babylon?",
                "options": [
                    "Hanging Gardens",
                    "Colossus",
                    "Lighthouse",
                    "Temple of Artemis"
                ],
                "correct_index": 0
            }
        ],
        "medium": [
            {
                "question": "When did the Berlin Wall fall?",
                "options": ["1987", "1988", "1989", "1990"],
                "correct_index": 2
            },
            {
                "question": "Who was the British Prime Minister during WWII?",
                "options": ["Churchill", "Chamberlain", "Attlee", "Wilson"],
                "correct_index": 0
            },
            {
                "question": "When was the French Revolution?",
                "options": ["1789", "1799", "1809", "1819"],
                "correct_index": 0
            },
            {
                "question": "Which dynasty ruled the Byzantine Empire in the 9th-11th century?",
                "options": ["Macedonian", "Komnenos", "Angelos", "Palaiologos"],
                "correct_index": 0
            },
            {
                "question": "When was the Suez Crisis?",
                "options": ["1954", "1956", "1958", "1960"],
                "correct_index": 1
            },
            {
                "question": "Which empire was the first to adopt Christianity as state religion?",
                "options": ["Roman Empire", "Byzantine Empire", "Armenian Kingdom", "Frankish Empire"],
                "correct_index": 2
            },
            {
                "question": "Who founded the Mongol Empire?",
                "options": ["Kublai Khan", "Genghis Khan", "Ogedei Khan", "Mongke Khan"],
                "correct_index": 1
            },
            {
                "question": "When did the Hundred Years' War begin?",
                "options": ["1337", "1347", "1357", "1367"],
                "correct_index": 0
            }
        ],
        "hard": [
            {
                "question": "Which treaty ended the Thirty Years' War?",
                "options": ["Peace of Westphalia", "Treaty of Utrecht", "Treaty of Paris", "Treaty of Brest-Litovsk"],
                "correct_index": 0
            },
            {
                "question": "Who was the founder of the Rurik dynasty?",
                "options": ["Igor", "Oleg", "Rurik", "Vladimir"],
                "correct_index": 2
            },
            {
                "question": "Which battle marked the end of the Roman Republic?",
                "options": ["Actium", "Pharsalus", "Cannae", "Zama"],
                "correct_index": 0
            },
            {
                "question": "Who was the last Byzantine emperor?",
                "options": ["Constantine XI", "Justinian I", "Basil II", "Alexios I"],
                "correct_index": 0
            },
            {
                "question": "Which empire ruled India before the British?",
                "options": ["Mughal", "Sikh", "Maratha", "Maurya"],
                "correct_index": 0
            },
            {
                "question": "When was the Bay of Pigs invasion?",
                "options": ["1960", "1961", "1962", "1963"],
                "correct_index": 1
            },
            {
                "question": "Which dynasty was the last to rule China?",
                "options": ["Ming", "Qing", "Han", "Tang"],
                "correct_index": 1
            },
            {
                "question": "Who was the first Roman emperor to convert to Christianity?",
                "options": ["Constantine", "Theodosius", "Augustus", "Diocletian"],
                "correct_index": 0
            }
        ]
    },
    
    "literature": {
        "easy": [
            {
                "question": "Who wrote 'Romeo and Juliet'?",
                "options": ["Charles Dickens", "William Shakespeare", "Victor Hugo", "Johann Wolfgang von Goethe"],
                "correct_index": 1
            },
            {
                "question": "Who is the hero of Homer's 'Odyssey'?",
                "options": ["Achilles", "Odysseus", "Hector", "Ajax"],
                "correct_index": 1
            },
            {
                "question": "Who wrote 'Crime and Punishment'?",
                "options": ["Tolstoy", "Dostoevsky", "Gogol", "Turgenev"],
                "correct_index": 1
            },
            {
                "question": "Where does 'Hamlet' take place?",
                "options": ["Denmark", "England", "Norway", "Sweden"],
                "correct_index": 0
            },
            {
                "question": "Who wrote 'The Great Gatsby'?",
                "options": ["Ernest Hemingway", "F. Scott Fitzgerald", "John Steinbeck", "William Faulkner"],
                "correct_index": 1
            },
            {
                "question": "What genre is the 'Iliad'?",
                "options": ["Tragedy", "Epic", "Comedy", "Elegy"],
                "correct_index": 1
            },
            {
                "question": "Who is the author of 'Dracula'?",
                "options": ["Mary Shelley", "Bram Stoker", "Edgar Allan Poe", "H.G. Wells"],
                "correct_index": 1
            },
            {
                "question": "Which Greek poet wrote the 'Theogony'?",
                "options": ["Homer", "Hesiod", "Sappho", "Pindar"],
                "correct_index": 1
            }
        ],
        "medium": [
            {
                "question": "Who wrote '1984'?",
                "options": ["Aldous Huxley", "George Orwell", "Ray Bradbury", "Kurt Vonnegut"],
                "correct_index": 1
            },
            {
                "question": "Who wrote 'The Three Musketeers'?",
                "options": ["Alexandre Dumas", "Victor Hugo", "Jules Verne", "Gustave Flaubert"],
                "correct_index": 0
            },
            {
                "question": "Which Shakespeare play features the 'To be or not to be' soliloquy?",
                "options": ["Macbeth", "Hamlet", "King Lear", "Othello"],
                "correct_index": 1
            },
            {
                "question": "Who wrote the 'Harry Potter' books?",
                "options": ["J.R.R. Tolkien", "J.K. Rowling", "C.S. Lewis", "George R.R. Martin"],
                "correct_index": 1
            },
            {
                "question": "Who wrote 'Moby-Dick'?",
                "options": ["Nathaniel Hawthorne", "Herman Melville", "Mark Twain", "Henry James"],
                "correct_index": 1
            },
            {
                "question": "What is the first book of the 'Lord of the Rings'?",
                "options": [
                    "The Two Towers",
                    "The Return of the King",
                    "The Fellowship of the Ring",
                    "The Hobbit"
                ],
                "correct_index": 2
            },
            {
                "question": "Who wrote 'The Catcher in the Rye'?",
                "options": ["J.D. Salinger", "Harper Lee", "Kurt Vonnegut", "John Knowles"],
                "correct_index": 0
            },
            {
                "question": "Which poet wrote 'The Divine Comedy'?",
                "options": ["Petrarch", "Dante", "Boccaccio", "Machiavelli"],
                "correct_index": 1
            }
        ],
        "hard": [
            {
                "question": "Who wrote 'Ulysses'?",
                "options": ["James Joyce", "Virginia Woolf", "T.S. Eliot", "W.B. Yeats"],
                "correct_index": 0
            },
            {
                "question": "For which work did Hemingway win the Nobel Prize?",
                "options": ["The Old Man and the Sea", "A Farewell to Arms", "For Whom the Bell Tolls", "The Sun Also Rises"],
                "correct_index": 0
            },
            {
                "question": "Who wrote 'Thus Spoke Zarathustra'?",
                "options": ["Schopenhauer", "Nietzsche", "Kant", "Hegel"],
                "correct_index": 1
            },
            {
                "question": "Who is the author of the 'Nibelungenlied'?",
                "options": ["Goethe", "Schiller", "Unknown", "Lessing"],
                "correct_index": 2
            },
            {
                "question": "Which Russian author wrote 'Dead Souls'?",
                "options": ["Dostoevsky", "Gogol", "Tolstoy", "Chekhov"],
                "correct_index": 1
            },
            {
                "question": "Who wrote 'The Metamorphosis'?",
                "options": ["Franz Kafka", "Thomas Mann", "Hermann Hesse", "Stefan Zweig"],
                "correct_index": 0
            },
            {
                "question": "Which literary movement does James Joyce belong to?",
                "options": ["Modernism", "Realism", "Romanticism", "Symbolism"],
                "correct_index": 0
            },
            {
                "question": "Who wrote 'The Name of the Rose'?",
                "options": ["Italo Calvino", "Umberto Eco", "Primo Levi", "Antonio Tabucchi"],
                "correct_index": 1
            }
        ]
    }
}


class QuestionManager:
    """
    Question manager for Sphinx
    """
    
    def __init__(self, questions_dict: Dict = None):
        self.questions = questions_dict if questions_dict else QUESTIONS
        self.type_names = {
            "math": "Math",
            "history": "History",
            "literature": "Literature"
        }
        self.difficulty_names = {
            "easy": "Easy",
            "medium": "Medium",
            "hard": "Hard"
        }
        self.used_questions = set()  # Track used questions
    
    def get_question(self, q_type: str, difficulty: str) -> Optional[Dict]:
        """
        Get a random question by type and difficulty
        
        Args:
            q_type: "math", "history", "literature"
            difficulty: "easy", "medium", "hard"
            
        Returns:
            dict: Question data, or None if not available
        """
        try:
            questions = self.questions[q_type][difficulty]
            # Filter out used questions if possible
            available = [q for q in questions if id(q) not in self.used_questions]
            if not available:
                # If all used, reset and use all
                self.used_questions.clear()
                available = questions
            
            chosen = random.choice(available) if available else None
            if chosen:
                self.used_questions.add(id(chosen))
            return chosen
        except KeyError:
            return None
    
    def get_question_by_type(self, q_type: str, difficulty: str = None) -> Optional[Dict]:
        """
        Get question by type, with optional difficulty
        """
        if difficulty is None:
            difficulty = random.choice(["easy", "medium", "hard"])
        return self.get_question(q_type, difficulty)
    
    def get_question_by_difficulty(self, difficulty: str) -> Optional[Dict]:
        """
        Get question by difficulty, random type
        """
        q_type = random.choice(["math", "history", "literature"])
        return self.get_question(q_type, difficulty)
    
    def get_random_question(self) -> Optional[Dict]:
        """
        Get a completely random question
        """
        q_type = random.choice(["math", "history", "literature"])
        difficulty = random.choice(["easy", "medium", "hard"])
        return self.get_question(q_type, difficulty)
    
    def get_question_with_skill(self, q_type: str, skill_level: int) -> Dict:
        """
        Get question based on player's skill level
        
        Args:
            q_type: "math", "history", "literature"
            skill_level: 0=bad, 1=middle, 2=good
            
        Returns:
            dict: Question data
        """
        if skill_level == 0:
            difficulty = "easy"
        elif skill_level == 1:
            difficulty = "medium"
        else:  # skill_level == 2
            difficulty = "hard"
        
        return self.get_question(q_type, difficulty)
    
    def get_sphinx_questions(self, skill_levels: List[int], count: int = 3) -> List[Dict]:
        """
        Get questions for the Sphinx based on player's skill levels
        
        Args:
            skill_levels: [math_level, history_level, literature_level]
            count: Number of questions (default 3)
            
        Returns:
            List of question dicts
        """
        type_map = ["math", "history", "literature"]
        questions = []
        
        # Get one question for each type
        for i, level in enumerate(skill_levels):
            q_type = type_map[i]
            q = self.get_question_with_skill(q_type, level)
            if q:
                questions.append(q)
        
        # Shuffle and return requested count
        random.shuffle(questions)
        return questions[:count]
    
    def check_answer(self, question: Dict, selected_index: int) -> bool:
        """
        Check if the answer is correct
        """
        return selected_index == question["correct_index"]
    
    def display_question(self, question: Dict) -> str:
        """
        Format question for display
        """
        text = f"\n {question['question']}\n"
        for i, option in enumerate(question["options"]):
            text += f"   {i+1}. {option}\n"
        return text
    
    def get_type_name(self, q_type: str) -> str:
        """Get display name for type"""
        return self.type_names.get(q_type, q_type)
    
    def get_difficulty_name(self, difficulty: str) -> str:
        """Get display name for difficulty"""
        return self.difficulty_names.get(difficulty, difficulty)
    
    def get_question_count(self) -> Dict:
        """
        Get question statistics
        """
        stats = {}
        for q_type in self.questions:
            stats[q_type] = {}
            for difficulty in self.questions[q_type]:
                stats[q_type][difficulty] = len(self.questions[q_type][difficulty])
        return stats
    
    def reset_used_questions(self):
        """Reset the used questions tracking"""
        self.used_questions.clear()
    
    def add_question(self, q_type: str, difficulty: str,
                     question: str, options: List[str], correct_index: int):
        """
        Add a new question to the database
        """
        if q_type not in self.questions:
            self.questions[q_type] = {}
        if difficulty not in self.questions[q_type]:
            self.questions[q_type][difficulty] = []
        
        self.questions[q_type][difficulty].append({
            "question": question,
            "options": options,
            "correct_index": correct_index
        })


# --- EXAMPLE USAGE ---

if __name__ == "__main__":
    qm = QuestionManager()
    
    print("=" * 50)
    print("Question Statistics:")
    print("=" * 50)
    
    stats = qm.get_question_count()
    for q_type, difficulties in stats.items():
        print(f"\n{qm.get_type_name(q_type)}:")
        for diff, count in difficulties.items():
            print(f"  {qm.get_difficulty_name(diff)}: {count} questions")
    
    print("\n" + "=" * 50)
    print("Sample Questions:")
    print("=" * 50)
    
    # Random question
    q = qm.get_random_question()
    if q:
        print(qm.display_question(q))
    
    # Question based on skill level
    q = qm.get_question_with_skill("math", skill_level=0)  # Bad at math
    if q:
        print("\n Bad at math (should be easy):")
        print(qm.display_question(q))
    
    # Get 3 questions for the Sphinx
    skills = [0, 1, 2]  # math=bad, history=middle, literature=good
    questions = qm.get_sphinx_questions(skills, count=3)
    print("\n Sphinx Questions:")
    for i, q in enumerate(questions, 1):
        print(f"\n Question {i}:")
        print(qm.display_question(q))