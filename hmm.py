"""
- Forward-Backward
- Viterbi
- Baum-Welch (EM)
"""

import numpy as np
from typing import List, Tuple, Union


class HMM:
    
    def __init__(self, n_states: int, n_observations: int):
        self.n_states = n_states
        self.n_observations = n_observations
        
        self._pi = None
        self._A = None
        self._B = None
        
        self.reset()
    
    def reset(self):
        #Random initialization of parameters
        self.pi = np.ones(self.n_states) / self.n_states
        self.A = np.random.rand(self.n_states, self.n_states)
        self.A = self.A / self.A.sum(axis=1, keepdims=True)
        self.B = np.random.rand(self.n_states, self.n_observations)
        self.B = self.B / self.B.sum(axis=1, keepdims=True)
    
    @property
    def pi(self):
        return self._pi
    
    @pi.setter
    def pi(self, value):
        self._pi = np.array(value, dtype=float)
        if self._pi.ndim == 1 and len(self._pi) == self.n_states:
            if self._pi.sum() > 0:
                self._pi = self._pi / self._pi.sum()
        else:
            raise ValueError(f"pi mérete {self.n_states} kell legyen")
    
    @property
    def A(self):
        return self._A
    
    @A.setter
    def A(self, value):
        self._A = np.array(value, dtype=float)
        if self._A.shape == (self.n_states, self.n_states):
            row_sums = self._A.sum(axis=1, keepdims=True)
            row_sums[row_sums == 0] = 1.0
            self._A = self._A / row_sums
        else:
            raise ValueError(f"A mérete ({self.n_states}, {self.n_states}) kell legyen")
    
    @property
    def B(self):
        return self._B
    
    @B.setter
    def B(self, value):
        self._B = np.array(value, dtype=float)
        if self._B.shape == (self.n_states, self.n_observations):
            row_sums = self._B.sum(axis=1, keepdims=True)
            row_sums[row_sums == 0] = 1.0
            self._B = self._B / row_sums
        else:
            raise ValueError(f"B mérete ({self.n_states}, {self.n_observations}) kell legyen")
    
    def copy(self) -> 'HMM':
        """Modell másolása"""
        new = HMM(self.n_states, self.n_observations)
        new.pi = self.pi.copy()
        new.A = self.A.copy()
        new.B = self.B.copy()
        return new
    
    def generate_sequence(self, T: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Véletlenszerű állapot- és megfigyeléssorozat generálása
        """
        states = np.zeros(T, dtype=int)
        observations = np.zeros(T, dtype=int)
        
        states[0] = np.random.choice(self.n_states, p=self.pi)
        observations[0] = np.random.choice(self.n_observations, p=self.B[states[0]])
        
        for t in range(1, T):
            states[t] = np.random.choice(self.n_states, p=self.A[states[t-1]])
            observations[t] = np.random.choice(self.n_observations, p=self.B[states[t]])
        
        return states, observations
    
    def __repr__(self):
        return f"HMM(n_states={self.n_states}, n_obs={self.n_observations})"


class ForwardBackward:
    
    def __init__(self, hmm: HMM, use_scaling: bool = True):
        self.hmm = hmm
        self.use_scaling = use_scaling
        self._alpha = None
        self._beta = None
        self._bel = None
        self._xi = None
        self._likelihood = None
        self._scaling_factors = None
    
    def run(self, observations: Union[List[int], np.ndarray]) -> Tuple[np.ndarray, ...]:
        """
        Returns:
            alpha: (T, N)
            beta: (T, N)
            bel: (T, N)
            xi: (T-1, N, N)
            likelihood: float
        """
        obs = np.array(observations, dtype=int)
        T = len(obs)
        N = self.hmm.n_states
        M = self.hmm.n_observations
        
        if np.max(obs) >= M or np.min(obs) < 0:
            raise ValueError(f"Megfigyelések 0 és {M-1} között kell legyenek")
        
        # --- FORWARD ---
        alpha = np.zeros((T, N))
        scaling = np.zeros(T) if self.use_scaling else None
        
        # Inicializáció: α₁(i) = π_i · B_{i,y₁}
        alpha[0, :] = self.hmm.pi * self.hmm.B[:, obs[0]]
        
        if self.use_scaling:
            scaling[0] = alpha[0, :].sum()
            if scaling[0] > 0:
                alpha[0, :] /= scaling[0]
            else:
                alpha[0, :] += 1e-10
                scaling[0] = alpha[0, :].sum()
                alpha[0, :] /= scaling[0]
        
        # Rekurzió: α_{t+1}(j) = B_{j,y_{t+1}} · Σᵢ α_t(i) · A_{ij}
        for t in range(1, T):
            for j in range(N):
                alpha[t, j] = self.hmm.B[j, obs[t]] * np.sum(alpha[t-1, :] * self.hmm.A[:, j])
            
            if self.use_scaling:
                scaling[t] = alpha[t, :].sum()
                if scaling[t] > 0:
                    alpha[t, :] /= scaling[t]
                else:
                    alpha[t, :] += 1e-10
                    scaling[t] = alpha[t, :].sum()
                    alpha[t, :] /= scaling[t]
        
        # --- BACKWARD ---
        beta = np.zeros((T, N))
        beta[T-1, :] = 1.0
        
        if self.use_scaling:
            beta[T-1, :] /= scaling[T-1]

        for t in range(T-2, -1, -1):
            for i in range(N):
                beta[t, i] = np.sum(self.hmm.A[i, :] * self.hmm.B[:, obs[t+1]] * beta[t+1, :])
            
            if self.use_scaling:
                if scaling[t] > 0:
                    beta[t, :] /= scaling[t]
                else:
                    beta[t, :] += 1e-10
                    beta[t, :] /= (beta[t, :].sum() if beta[t, :].sum() > 0 else 1.0)
        
        # --- UTÓLAGOS VALÓSZÍNŰSÉGEK (bel) ---
        bel = np.zeros((T, N))
        for t in range(T):
            bel[t, :] = alpha[t, :] * beta[t, :]
            total = bel[t, :].sum()
            if total > 0:
                bel[t, :] /= total
            else:
                bel[t, :] = 1.0 / N
        
        # --- ÁTMENET-UTÓLAGOSOK (xi) ---
        xi = np.zeros((T-1, N, N))
        for t in range(T-1):
            for i in range(N):
                for j in range(N):
                    xi[t, i, j] = alpha[t, i] * self.hmm.A[i, j] * self.hmm.B[j, obs[t+1]] * beta[t+1, j]
            
            total = xi[t, :, :].sum()
            if total > 0:
                xi[t, :, :] /= total
            else:
                xi[t, :, :] = 1.0 / (N * N)
        
        # --- LIKELIHOOD ---
        if self.use_scaling:
            likelihood = np.exp(np.sum(np.log(scaling)))
        else:
            likelihood = np.sum(alpha[T-1, :])
        
        self._alpha = alpha
        self._beta = beta
        self._bel = bel
        self._xi = xi
        self._likelihood = likelihood
        self._scaling_factors = scaling
        
        return alpha, beta, bel, xi, likelihood
    
    def get_most_likely_states(self) -> np.ndarray:

        if self._bel is None:
            raise RuntimeError("Először futtasd a run() metódust!")
        return np.argmax(self._bel, axis=1)
    
    @property
    def alpha(self):
        return self._alpha
    
    @property
    def beta(self):
        return self._beta
    
    @property
    def bel(self):
        return self._bel
    
    @property
    def xi(self):
        return self._xi
    
    @property
    def likelihood(self):
        return self._likelihood


class Viterbi:
    """
    Viterbi algoritmus a legvalószínűbb állapotsorozathoz
    
    Megoldja: argmax P(X_{1:T} | y_{1:T})
    """
    
    def __init__(self, hmm: HMM):
        self.hmm = hmm
    
    def decode(self, observations: Union[List[int], np.ndarray]) -> Tuple[np.ndarray, float]:
        """
        Viterbi dekódolás
        
        Returns:
            states: (T,) - Legvalószínűbb állapotsorozat
            max_prob: float - Út valószínűsége
        """
        obs = np.array(observations, dtype=int)
        T = len(obs)
        N = self.hmm.n_states
        
        delta = np.zeros((T, N))
        psi = np.zeros((T, N), dtype=int)
        
        # Inicializáció
        delta[0, :] = self.hmm.pi * self.hmm.B[:, obs[0]]
        if delta[0, :].sum() > 0:
            delta[0, :] /= delta[0, :].sum()
        else:
            delta[0, :] = 1.0 / N
        
        # Rekurzió
        for t in range(1, T):
            for j in range(N):
                vals = delta[t-1, :] * self.hmm.A[:, j]
                max_idx = np.argmax(vals)
                delta[t, j] = vals[max_idx] * self.hmm.B[j, obs[t]]
                psi[t, j] = max_idx
            
            if delta[t, :].sum() > 0:
                delta[t, :] /= delta[t, :].sum()
        
        # Visszakövetés
        states = np.zeros(T, dtype=int)
        states[-1] = np.argmax(delta[-1, :])
        max_prob = np.max(delta[-1, :])
        
        for t in range(T-2, -1, -1):
            states[t] = psi[t+1, states[t+1]]
        
        return states, max_prob


class BaumWelch:
    """
    Baum-Welch algoritmus (EM)
    """
    
    def __init__(self, hmm: HMM, use_scaling: bool = True):
        self.hmm = hmm
        self.use_scaling = use_scaling
        self._history = []
    
    def train(self, observations: Union[List[int], np.ndarray],
              max_iter: int = 100,
              tol: float = 1e-5,
              verbose: bool = False) -> HMM:
        """
        Baum-Welch tanítás
        
        Args:
            observations: (T,) megfigyelések
            max_iter: Maximális iterációszám
            tol: Konvergencia tolerancia
            verbose: Részletes kimenet
            
        Returns:
            hmm: Betanított modell
        """
        obs = np.array(observations, dtype=int)
        T = len(obs)
        N = self.hmm.n_states
        M = self.hmm.n_observations
        
        prev_pi = self.hmm.pi.copy()
        prev_A = self.hmm.A.copy()
        prev_B = self.hmm.B.copy()
        
        history = []
        
        for iteration in range(max_iter):
            # --- E-LÉPÉS: Forward-Backward ---
            fb = ForwardBackward(self.hmm, use_scaling=self.use_scaling)
            _, _, bel, xi, likelihood = fb.run(obs)
            
            log_lik = np.log(likelihood) if likelihood > 0 else -np.inf
            history.append(log_lik)
            
            if verbose:
                print(f"Iter {iteration+1}: log-lik = {log_lik:.4f}")
            
            # --- M-LÉPÉS: Paraméterfrissítés ---
            
            # 1. Kezdeti eloszlás
            new_pi = bel[0, :]
            new_pi = new_pi / new_pi.sum() if new_pi.sum() > 0 else np.ones(N) / N
            
            # 2. Átmeneti mátrix
            new_A = np.zeros((N, N))
            for i in range(N):
                denominator = np.sum(bel[:-1, i])
                if denominator > 0:
                    for j in range(N):
                        new_A[i, j] = np.sum(xi[:, i, j]) / denominator
                else:
                    new_A[i, :] = 1.0 / N
            
            # 3. Kibocsátási mátrix
            new_B = np.zeros((N, M))
            for i in range(N):
                denominator = np.sum(bel[:, i])
                if denominator > 0:
                    for k in range(M):
                        mask = (obs == k)
                        new_B[i, k] = np.sum(bel[mask, i]) / denominator
                else:
                    new_B[i, :] = 1.0 / M
            
            # Konvergencia ellenőrzése
            max_diff = max(
                np.max(np.abs(new_pi - prev_pi)),
                np.max(np.abs(new_A - prev_A)),
                np.max(np.abs(new_B - prev_B))
            )
            
            # Frissítés
            self.hmm.pi = new_pi
            self.hmm.A = new_A
            self.hmm.B = new_B
            
            prev_pi = new_pi.copy()
            prev_A = new_A.copy()
            prev_B = new_B.copy()
            
            if max_diff < tol:
                if verbose:
                    print(f"Konvergencia {iteration+1} iteráció után")
                break
        
        self._history = history
        return self.hmm
    
    @property
    def history(self):
        return self._history


def create_random_hmm(n_states: int, n_observations: int,
                      transition_sparsity: float = 1.0) -> HMM:
    """Véletlenszerű HMM"""
    hmm = HMM(n_states, n_observations)
    hmm.pi = np.random.rand(n_states)
    hmm.pi /= hmm.pi.sum()
    
    A = np.random.rand(n_states, n_states)
    if transition_sparsity < 1.0:
        mask = np.random.rand(n_states, n_states) < transition_sparsity
        A = A * mask
    hmm.A = A
    
    hmm.B = np.random.rand(n_states, n_observations)
    return hmm