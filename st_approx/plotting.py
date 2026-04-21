import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from scipy.stats import norm

def plot(datasets, xlabel=r'$x$, усл. ед.', ylabel=r'$y$, усл. ед.', 
         zoom_factor=0.1, x_limits=None,
         legend_location='best', title=r'', saving=None, show=True):
    """
    datasets: список словарей вида:
        {
            'values': [x[], y[], dy[]],
            'approx': [k, b, dk, db], (опционально)
            'approx_type': 'linear' | 'hyperbola' | 'exponential',
            'label': 'Эксперимент 1',
            'color': 'firebrick'
        }
    xlabel, ylabel: подписи осей
    zoom_factor: сколько добавить к границам по X (в процентах от диапазона) для лучшего отображения
    x_limits: (min, max) — если None, то границы определяются автоматически по данным с учетом zoom_factor
    legend_location: расположение легенды (по умолчанию 'best')
    title: заголовок графика
    saving: путь для сохранения графика (если None, то график не сохраняется)
    show: показывать график (True) или только сохранять (False)
    """
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    
    # Списки для автоматического определения границ
    all_x, all_y = [], []

    for ds in datasets:
        val = ds.get('values')
        if val:
            data = np.array(val)
            x, y, dy = data[:, 0], data[:, 1], data[:, 2]
            all_x.extend(x); all_y.extend(y)
        else: 
            all_x.extend([0, 100]); all_y.extend([0, 100])
            
        
        color = ds.get('color', 'firebrick')
        label = ds.get('label', 'Эксперимент')
        approx = ds.get('approx')
        approx_type = ds.get('approx_type', 'linear')

        # 1. Отрисовка точек
        ax.errorbar(x, y, yerr=dy, fmt='o', color=color, markersize=5, 
                    capsize=3, elinewidth=1.2, markeredgecolor='black', 
                    label=label, zorder=5) if val else None

        # 2. Отрисовка аппроксимации
        if approx:
            k, b, dk, db = approx
            # Создаем расширенный диапазон x для плавности линий
            x_line = np.linspace(min(x) * (1 - zoom_factor), max(x) * (1 + zoom_factor), 200)
            
            if approx_type == 'linear':
                f = lambda k_v, b_v, x_v: k_v * x_v + b_v
                formula = rf'${label}: ({k:.2f} \pm {dk:.2f})x + ({b:.2f} \pm {db:.2f})$'
            elif approx_type == 'hyperbola':
                f = lambda k_v, b_v, x_v: k_v / x_v + b_v
                formula = rf'${label}: \frac{{{k:.2f}}}{{x}} + {b:.2f}$'
            elif approx_type == 'exponential':
                f = lambda k_v, b_v, x_v: b_v * np.exp(k_v / x_v)
                formula = rf'${label}: {b:.2f} e^{{{k:.2f}/x}}$'

            ax.plot(x_line, f(k, b, x_line), color=color, linewidth=1.5, label=formula, zorder=4)
            
            # Предельные прямые (опционально можно добавить и сюда)
            ax.plot(x_line, f(k + dk, b - db, x_line), '--', color=color, alpha=0.2, zorder=2)
            ax.plot(x_line, f(k - dk, b + db, x_line), '--', color=color, alpha=0.2, zorder=2)

    # 3. Настройка осей и сетки
    ax.grid(which='major', color='#B0B0B0', linestyle='-', linewidth=0.7)
    ax.grid(which='minor', color='#E0E0E0', linestyle=':', linewidth=0.5)
    ax.minorticks_on()
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())

    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, size=16)

    # Авто-масштабирование
    if not x_limits:
        x_min, x_max = min(all_x), max(all_x)
        dx = (x_max - x_min) * zoom_factor
        ax.set_xlim(x_min - dx, x_max + dx)
    else:
        ax.set_xlim(x_limits)

    ax.legend(loc=legend_location, fontsize=9, frameon=True, shadow=True)
    
    if saving: plt.savefig(saving)
    plt.tight_layout()
    if show: plt.show()

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