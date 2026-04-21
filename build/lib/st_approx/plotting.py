import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

def plot (values, approx, approx_type='linear', xlabel=r'$x$, усл. ед.', ylabel=r'$y$, усл. ед.', 
                          zoom_factor=0.1, x_limits=None, y_limits=None,
                             legend_location = 'best', title = r'', saving=None):
    """
    values: [x[], y[], dy[]]
    approx: [k, b, dk, db]
    zoom_factor: increase argument to zoom
    approx_type: linear, hyperbola
    xlabel, ylabel: label names
    legend_location: 'best', 'upper (right/left)', 'bottom (right/left)'
    title: string 
    saving: file path
    """
    data = np.array(values)
    x, y, dy = data[:, 0], data[:, 1], data[:, 2]
    k, b, dk, db = approx

    # Включаем интерактивный режим (в некоторых IDE нужно 'qt', в других работает по умолчанию)
    # plt.ion() 

    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)

    # 1. Расчет границ для масштабирования
    x_range = x.max() - x.min()
    y_range = y.max() - y.min()
    
    # Автоматические границы с учетом зума
    def_xlim = (x.min() - x_range * zoom_factor, x.max() + x_range * zoom_factor)
    def_ylim = (y.min() - y_range * zoom_factor, y.max() + y_range * zoom_factor)
    
    # Линия для отрисовки (берем с запасом для красоты)
    x_line = np.linspace(def_xlim[0], def_xlim[1], 100)

    # 2. Отрисовка аппроксимации
    if approx_type == 'linear':
        f = lambda k_val, b_val, x_val: k_val*x_val + b_val
        formula_str = rf'$y = ({k:.3f} \pm {dk:.3f})x + ({b:.3f} \pm {db:.3f})$'
    if approx_type == 'hyperbola':
        f = lambda k_val, b_val, x_val: k_val/x_val + b_val
        formula_str = rf'$y = \frac{{{k:.3f} \pm {dk:.3f}}}{{x}} + ({b:.3f} \pm {db:.3f})$'
    if approx_type == 'exponential':
        f = lambda k_val, b_val, x_val: k_val * np.exp(b_val * x_val)
        formula_str = rf'$y = ({k:.3f} \pm {dk:.3f}) e^{{({b:.3f} \pm {db:.3f})x}}$'
    
    formula_label = (formula_str)
    
    ax.plot(x_line, f(k, b, x_line), color='black', linewidth=1.5, label=formula_label, zorder=4)
    
    # Предельные прямые (пунктир)
    ax.plot(x_line, f(k + dk, b - db, x_line), '--', color='gray', alpha=0.5, label='Предельные прямые', zorder=2)
    ax.plot(x_line, f(k - dk, b + db, x_line), '--', color='gray', alpha=0.5, zorder=2)

    # 3. Экспериментальные точки
    ax.errorbar(x, y, yerr=dy, fmt='o', color='firebrick', markersize=5, 
                capsize=3, elinewidth=1.2, markeredgecolor='black', label='Эксперимент', zorder=5)

    # 4. Настройка сетки
    ax.grid(which='major', color='#B0B0B0', linestyle='-', linewidth=0.7)
    ax.grid(which='minor', color='#E0E0E0', linestyle=':', linewidth=0.5)
    ax.minorticks_on()
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())

    # 5. Оформление осей и легенды
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    
    # Легенда в "окошке"
    ax.legend(loc=legend_location, fontsize=10, frameon=True, fancybox=True, shadow=True, 
              facecolor='white', edgecolor='black', borderpad=1)
    ax.set_title(fr'{title}', size=20)

    # Применение масштабирования
    ax.set_xlim(x_limits if x_limits else def_xlim)
    ax.set_ylim(y_limits if y_limits else def_ylim)

    if saving != None: 
        plt.savefig(f'{saving}')

    plt.tight_layout()
    plt.show()