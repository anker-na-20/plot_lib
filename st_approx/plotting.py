import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from scipy.stats import norm

def plot (values, approx=None, approx_type='linear', xlabel=r'$x$, усл. ед.', ylabel=r'$y$, усл. ед.', 
                          zoom_factor=0.1, x_limits=None, y_limits=None,
                             legend_location = 'best', title = r'', saving=None, show=True):
    """
    values: [x[], y[], dy[]]
    approx: [k, b, dk, db]
    zoom_factor: increase argument to zoom
    approx_type: linear, hyperbola, exponential(b_val * np.exp(k_val / x_val))
    xlabel, ylabel: label names
    legend_location: 'best', 'upper (right/left)', 'bottom (right/left)'
    title: title of the plot
    saving: file path
    """
    data = np.array(values)
    x, y, dy = data[:, 0], data[:, 1], data[:, 2]
    k, b, dk, db = approx if approx else (None, None, None, None)

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
    if approx:
        if approx_type == 'linear':
            f = lambda k_val, b_val, x_val: k_val*x_val + b_val
            formula_str = rf'$y = ({k:.3f} \pm {dk:.3f})x + ({b:.3f} \pm {db:.3f})$'
        if approx_type == 'hyperbola':
            f = lambda k_val, b_val, x_val: k_val/x_val + b_val
            formula_str = rf'$y = \frac{{{k:.3f} \pm {dk:.3f}}}{{x}} + ({b:.3f} \pm {db:.3f})$'
        if approx_type == 'exponential':
            f = lambda k_val, b_val, x_val: b_val * np.exp(k_val / x_val)
            formula_str = rf'$y = ({b:.3f} \pm {db:.3f}) e^{{({k:.3f} \pm {dk:.3f})/x}}$'

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
    plt.show() if show else None

def plot_grain_dist(values, cell_width=1.5, x_range_cells=None, 
                    density=False, xlabel=r'$x$, см', ylabel=None, 
                    zoom_factor=0.1, x_limits=None, y_limits=None,
                    title=r'', saving=None, legend_location='best', h=None):
    """
    values: [[количество_зерен, номер_ячейки], ...]
    cell_width: ширина ячейки в см
    x_range_cells: (min_idx, max_idx) — сколько ячеек показать (напр. от -10 до 10)
    density: если True, нормирует Y (доля зерен)
    """
    data = np.array(values)
    raw_counts = data[:, 0]        # Количество зерен (высота)
    cell_indices = data[:, 1].astype(int) # Номера ячеек (позиция)

    # 1. Создаем словарь: {номер_ячейки: количество_зерен}
    # Это нужно на случай, если в данных пропущены пустые ячейки
    dist_dict = dict(zip(cell_indices, raw_counts))

    # 2. Определяем границы по ячейкам
    if x_range_cells is None:
        min_idx, max_idx = int(min(cell_indices)), int(max(cell_indices))
    else:
        min_idx, max_idx = x_range_cells

    # Генерируем полный список индексов (чтобы пустые ячейки тоже были на графике)
    plot_indices = np.arange(min_idx, max_idx + 1)
    # Берем количество зерен из словаря, если ячейки нет — ставим 0
    plot_counts = np.array([float(dist_dict.get(i, 0)) for i in plot_indices])
    
    # Центры ячеек в сантиметрах
    x_centers = plot_indices * cell_width

    # 3. Нормировка
    if density:
        total = plot_counts.sum()
        if total > 0:
            plot_counts /= total
            if h == None:
                h = math.sqrt(total/(2*cell_width*sum([(cell_indices[i]**2)*raw_counts[i] for i in range(len(raw_counts))])))
            f = lambda x_val, h_val: (h_val/np.sqrt(math.pi)) * np.exp(-1*(x_val*h_val)**2)
            x_line = np.linspace(x_centers.min() - cell_width, x_centers.max() + cell_width, 200)
            label_str = rf'Гауссова кривая: $h={h:.3f}$ {total:.3f}'
        ylabel = ylabel or 'Доля зерен (отн. ед.)'
    else:
        ylabel = ylabel or 'Количество зерен, шт'


    # 4. Отрисовка
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    
    # Рисуем ячейки. align='center' ставит центр столбика ровно на координату X
    ax.bar(x_centers, plot_counts, width=cell_width * 0.98, 
           color='firebrick', edgecolor='black', alpha=0.8, zorder=3, label='Распределение зерен')
    ax.plot(x_line, f(x_line, h), color='black', linestyle='--', label=label_str, zorder=4) if density else None

    # 5. Настройка Zoom и лимитов
    y_max = plot_counts.max() if len(plot_counts) > 0 else 1
    
    # Края по X: от самой левой стенки до самой правой стенки ячеек
    x_left_edge = x_centers.min() - cell_width/2
    x_right_edge = x_centers.max() + cell_width/2
    x_span = x_right_edge - x_left_edge
    
    def_xlim = (x_left_edge - x_span * zoom_factor, x_right_edge + x_span * zoom_factor)
    def_ylim = (0, y_max * (1 + zoom_factor))

    # 6. Оформление сетки (твой стиль)
    ax.grid(which='major', color='#B0B0B0', linestyle='-', linewidth=0.7)
    ax.grid(which='minor', color='#E0E0E0', linestyle=':', linewidth=0.5)
    ax.minorticks_on()
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())

    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)

    ax.legend(loc=legend_location, fontsize=10, frameon=True, fancybox=True, shadow=True, 
            facecolor='white', edgecolor='black', borderpad=1)
    ax.set_title(title, size=20)

    ax.set_xlim(x_limits if x_limits else def_xlim)
    ax.set_ylim(y_limits if y_limits else def_ylim)

    if saving:
        plt.savefig(saving)

    plt.tight_layout()
    plt.show()