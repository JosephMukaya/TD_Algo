import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# Paramètres du système
m = 10  # masse en kg
alpha = 20  # coefficient de frottement en Ns/m
k = 4000  # constante de raideur du ressort en N/m
x0 = 0.01  # déplacement initial en m
v0 = 0  # vitesse initiale en m/s
F0 = 100  # amplitude de la force externe en N
omega = 10  # fréquence angulaire en rad/s

# Fonction pour l'équation différentielle du système
def equation_du_systeme(t, y, alpha, k, m, F0, omega, force_exterieure):
    x, v = y
    F_t = F0 * np.cos(omega * t) if force_exterieure else 0
    dxdt = v
    dvdt = (-alpha * v - k * x + F_t) / m
    return [dxdt, dvdt]

# Conditions initiales
conditions_initiales = [x0, v0]

# Intervalle de temps pour la simulation
t_debut = 0
t_fin = 10
t_points = np.linspace(t_debut, t_fin, 1000)

# Résolution pour le cas (a) - Oscillations libres
solution_libre = solve_ivp(equation_du_systeme, [t_debut, t_fin], conditions_initiales, args=(alpha, k, m, F0, omega, False), t_eval=t_points)

# Résolution pour le cas (b) - Force extérieure
solution_forcee = solve_ivp(equation_du_systeme, [t_debut, t_fin], conditions_initiales, args=(alpha, k, m, F0, omega, True), t_eval=t_points)

# Calcul des énergies pour le cas (a)
x_libre = solution_libre.y[0]
v_libre = solution_libre.y[1]
Ec_libre = 0.5 * m * v_libre**2
Ep_libre = 0.5 * k * x_libre**2
Em_libre = Ec_libre + Ep_libre

# Affichage des résultats
plt.figure(figsize=(14, 10))

# Déplacement pour les cas (a) et (b)
plt.subplot(3, 1, 1)
plt.plot(t_points, solution_libre.y[0], label='Déplacement (cas a)')
plt.plot(t_points, solution_forcee.y[0], label='Déplacement (cas b)', linestyle='--')
plt.legend()
plt.title('Déplacement en fonction du temps')

# Vitesse pour les cas (a) et (b)
plt.subplot(3, 1, 2)
plt.plot(t_points, solution_libre.y[1], label='Vitesse (cas a)')
plt.plot(t_points, solution_forcee.y[1], label='Vitesse (cas b)', linestyle='--')
plt.legend()
plt.title('Vitesse en fonction du temps')

# Énergies pour le cas (a)
plt.subplot(3, 1, 3)
plt.plot(t_points, Ec_libre, label='Énergie cinétique (Ec)')
plt.plot(t_points, Ep_libre, label='Énergie potentielle (Ep)')
plt.plot(t_points, Em_libre, label='Énergie mécanique (Em)')
plt.legend()
plt.title('Énergies en fonction du temps (cas a)')

plt.xlabel('Temps (s)')
plt.tight_layout()
plt.show()
