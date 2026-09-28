import numpy as np
from hmm import HMM, ForwardBackward, BaumWelch
from questions import QuestionManager
from typing import List, Dict, Tuple, Optional, Union
import random


class SphinxHMM:
    """
    Szfinx HMM modell a játékos képességeinek becsléséhez
    """
    
    def __init__(self, initial_skills: Optional[List[int]] = None):
        self.num_types = 3
        self.num_levels = 3
        self.n_states = 27
        self.n_observations = 8

        self.int_to_type = {
            0: "math",
            1: "history",
            2: "literature"
        }

        self.type_to_int = {
            "math": 0,
            "history": 1,
            "literature": 2
        }

        if initial_skills is None:
            initial_skills = [1, 1, 1]

        self.initial_skills = initial_skills
        
        # HMM modell létrehozása
        self.hmm = self._create_model()
        
        # Megfigyelések tárolása (kódolt formában)
        self.observations = []

        self.question_manager = QuestionManager()
        
        # Legutóbbi becslés
        self.last_estimate = initial_skills.copy()

    def get_question_for_type(self, q_type: Union[int, str]) -> Dict:

        """
        Get a question for a specific type based on player's skill
        """
        if isinstance(q_type, int):
            type_name = self.int_to_type.get(q_type, "math")
        else:
            type_name = q_type

        skill_level = self.get_skill_level(q_type)

        return self.question_manager.get_question_with_skill(type_name, skill_level)

    def get_sphinx_challenge(self, count: int = 3) -> List[Dict]:

        skill_levels = self.estimate_skills()
        if skill_levels is None:
            skill_levels = [1, 1, 1]

        type_names = ["math", "history", "literature"]
        questions = []
        for i, level in enumerate(skill_levels):
            q_type = type_names[i]
            q = self.question_manager.get_question_with_skill(q_type, level)
            if q:
                questions.append(q)
        
        while len(questions) < count:
            q = self.question_manager.get_random_question()
            if q:
                questions.append(q)
        
        random.shuffle(questions)
        return questions[:count]


    def ask_question(self, q_type: int, selected_index: int = None) -> Tuple[Dict, bool]:

        question = self.get_question_for_type(q_type)

        if selected_index is None:
            return question, None

        correct = self.question_manager.check_answer(question, selected_index)

        self.add_answer(q_type, correct)

        return question, correct

    
    def _create_model(self) -> HMM:
        """Szfinx-specifikus HMM létrehozása"""
        hmm = HMM(self.n_states, self.n_observations)
        
        # Kezdeti eloszlás: egyenletes
        hmm.pi = np.ones(self.n_states) / self.n_states

        initial_state = self._encode_skills(self.initial_skills)


        # Kezdeti eloszlás: 90% esély a kezdeti állapotra, 10% véletlenszerű
        pi = np.ones(self.n_states) * 0.1 / (self.n_states - 1)
        pi[initial_state] = 0.9
        hmm.pi = pi
        
        # Átmeneti mátrix: lassú változás
        A = np.zeros((self.n_states, self.n_states))

        
        for i in range(self.n_states):
            state_i = self._decode_state(i)
            for j in range(self.n_states):
                state_j = self._decode_state(j)
                diff = sum(abs(state_i[t] - state_j[t]) for t in range(self.num_types))
                
                if diff == 0:
                    A[i, j] = 0.7
                elif diff == 1:
                    A[i, j] = 0.15
                else:
                    A[i, j] = 0.0
        
        hmm.A = A
        
        # Kibocsátási mátrix
        B = np.zeros((self.n_states, self.n_observations))
        
        for state in range(self.n_states):
            levels = self._decode_state(state)
            for obs in range(self.n_observations):
                bits = []
                temp = obs
                for _ in range(self.num_types):
                    bits.append(temp % 2)
                    temp //= 2
                
                prob = 1.0
                for t in range(self.num_types):
                    level = levels[t]  # 0=rossz, 1=közepes, 2=jó
                    correct = bits[t]
                    
                    if level == 2:
                        p_correct = 0.8
                    elif level == 1:
                        p_correct = 0.5
                    else:
                        p_correct = 0.2
                    
                    prob *= p_correct if correct else (1 - p_correct)
                
                B[state, obs] = prob
        
        hmm.B = B
        return hmm

    def _encode_skills(self, skills: List[int]) -> int:
        """Encode skill levels to state index"""

        state_idx = 0
        for i, level in enumerate(skills):
            state_idx += level * (3 ** i)
        return state_idx
    
    def encode_answer(self, q_type: int, correct: bool) -> int:
        """
        Args:
            q_type: 0, 1, 2
            correct: True/False
            
        Returns:
            int: 0-7 közötti kód
        """
        bits = [0, 0, 0]
        bits[q_type] = 1 if correct else 0
        return bits[0] + 2*bits[1] + 4*bits[2]
    
    def _decode_state(self, state_idx: int) -> List[int]:
        """
        Returns:
            list: [típus0_szint, típus1_szint, típus2_szint]
            Szintek: 0=rossz, 1=közepes, 2=jó
        """
        levels = []
        temp = state_idx
        for _ in range(self.num_types):
            levels.append(temp % self.num_levels)
            temp //= self.num_levels
        return levels
    
    def add_answer(self, q_type: int, correct: bool):
        """Válasz hozzáadása a történethez"""

        if isinstance(q_type, str):
            q_type = self.type_to_int.get(q_type, 0)

        encoded = self.encode_answer(q_type, correct)
        self.observations.append(encoded)
    
    def estimate_skills(self) -> Optional[List[int]]:
        """
        Returns:
            list: [típus0_szint, típus1_szint, típus2_szint]
        """
        if len(self.observations) < 5:
            return self.initial_skills.copy()

        try:
            fb = ForwardBackward(self.hmm, use_scaling=True)
            _, _, bel, _, _ = fb.run(self.observations)
            
            # Legutolsó állapot
            current_bel = bel[-1, :]
            most_likely = np.argmax(current_bel)
            
            self.last_estimate = self._decode_state(most_likely)
            return self.last_estimate
        except:
            return self.initial_skills.copy()
    
    def get_skill_level(self, q_type: Union[int, str]) -> int:
        """
        Egy adott típus szintjének lekérése
        
        Returns:
            int: 0=rossz, 1=közepes, 2=jó
        """

        if isinstance(q_type, str):
            q_type = self.type_to_int.get(q_type, 0)

        skills = self.estimate_skills()
        if skills is None:
            return 1
        return skills[q_type] if q_type < len(skills) else 1
    
    def get_question_difficulty(self, q_type: Union[int, str]) -> str:
        """
        Kérdés nehézségének szöveges formája
        """

        if isinstance(q_type, int):
            type_name = self.int_to_type.get(q_type, "math")
        else:
            type_name = q_type

        level = self.get_skill_level(q_type)
        if level == 0:
            return "easy"
        elif level == 1:
            return "medium"
        else:
            return "hard"
    
    def reset(self):
        """Új játék (történet törlése)"""
        self.observations = []
        self.last_estimate = self.initial_skills.copy()
    
    def train_from_history(self, max_iter: int = 50):
        """
        Paraméterek finomhangolása a felhalmozott adatok alapján
        """
        if len(self.observations) < 5:
            return
        
        bw = BaumWelch(self.hmm, use_scaling=True)
        bw.train(self.observations, max_iter=max_iter, verbose=False)