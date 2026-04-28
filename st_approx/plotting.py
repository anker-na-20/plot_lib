import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

def plot(datasets, xlabel=r'$x$, усл. ед.', ylabel=r'$y$, усл. ед.', 
         zoom_factor=0.1, x_limits=None,
         legend_location='best', title=r'', saving=None, show=True):
    
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    all_x, all_y = [], []

    for ds in datasets:
        val = ds.get('values')
        if val is None: continue 
        
        data = np.array(val)
        x, y, dy = data[:, 0], data[:, 1], data[:, 2]
        all_x.extend(x); all_y.extend(y)
        
        color = ds.get('color', 'firebrick')
        label = ds.get('label', 'Эксперимент')
        
        # 1. Отрисовка точек
        ax.errorbar(x, y, yerr=dy, fmt='o', color=color, markersize=5, 
                    capsize=3, elinewidth=1.2, markeredgecolor='black', 
                    label=label, zorder=5)

        # 2. Отрисовка универсальной аппроксимации
        fit_res = ds.get('fit_result') # Берем словарь из нашей функции universal_fit
        if fit_res:
            coeffs = fit_res['coeffs']
            errors = fit_res['errors']
            degs = fit_res['degrees']

            # Создаем сетку для плавной линии
            x_min, x_max = min(x), max(x)
            margin = (x_max - x_min) * zoom_factor
            x_line = np.linspace(x_min - margin, x_max + margin, 500)

            # Универсальный расчет y для любых степеней: y = sum(k_i * x^d_i)
            def apply_fit(x_v, c_v):
                return sum(c * x_v**d for c, d in zip(c_v, degs))

            y_line = apply_fit(x_line, coeffs)
            
            # Формируем красивую подпись (берем первые пару слагаемых для краткости)
            formula_parts = [f"{c:.2f}x^{{{d}}}" for c, d in zip(coeffs, degs)]
            formula_str = f"${label}: y = " + " + ".join(formula_parts[:10]) + "...$"

            ax.plot(x_line, y_line, color=color, linewidth=1.8, label=formula_str, zorder=4)
            
            # Отрисовка коридора погрешности (опционально)
            # Используем верхнюю и нижнюю границы коэффициентов
            y_high = apply_fit(x_line, coeffs + errors)
            y_low = apply_fit(x_line, coeffs - errors)
            ax.fill_between(x_line, y_low, y_high, color=color, alpha=0.15, zorder=2)

    # 3. Дизайн и сетка (сохраняем ваш стиль)
    ax.grid(which='major', color='#B0B0B0', linestyle='-', linewidth=0.7)
    ax.grid(which='minor', color='#E0E0E0', linestyle=':', linewidth=0.5)
    ax.minorticks_on()
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())

    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, size=16)

    # Авто-масштабирование
    if x_limits:
        ax.set_xlim(x_limits)
    elif all_x:
        x_min, x_max = min(all_x), max(all_x)
        dx = (x_max - x_min) * zoom_factor
        ax.set_xlim(x_min - dx, x_max + dx)

    ax.legend(loc=legend_location, fontsize=9, frameon=True, shadow=True)
    
    if saving: plt.savefig(saving)
    plt.tight_layout()
    if show: plt.show()

def plot_grain_dist(values, cell_width=1.5, x_range_cells=None, 
                    density=False, xlabel=r'$x$, см', ylabel=None, 
                    zoom_factor=0.1, x_limits=None, y_limits=None,
                    title=r'', saving=None, legend_location='best', h=None):
    """
    values: [[количество_элементов, номер_ячейки], ...]
    cell_width: ширина ячейки в см
    x_range_cells: (min_idx, max_idx) — сколько ячеек показать (напр. от -10 до 10)
    density: если True, нормирует Y (доля элементов от общего количества) и рисует гауссову кривую
    h: параметр гауссовой кривой (если density=True). Если None, то рассчитывается по формуле h = sqrt(N/(2*cell_width*sum((cell_idx^2)*count)))
    """
    data = np.array(values)
    raw_counts = data[:, 0]        # Количество элементов (высота)
    cell_indices = data[:, 1].astype(int) # Номера ячеек (позиция)

    # 1. Создаем словарь: {номер_ячейки: количество_элементов}
    # Это нужно на случай, если в данных пропущены пустые ячейки
    dist_dict = dict(zip(cell_indices, raw_counts))

    # 2. Определяем границы по ячейкам
    if x_range_cells is None:
        min_idx, max_idx = int(min(cell_indices)), int(max(cell_indices))
    else:
        min_idx, max_idx = x_range_cells

    # Генерируем полный список индексов (чтобы пустые ячейки тоже были на графике)
    plot_indices = np.arange(min_idx, max_idx + 1)
    # Берем количество элементов из словаря, если ячейки нет — ставим 0
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
        ylabel = ylabel or 'Доля элементов (отн. ед.)'
    else:
        ylabel = ylabel or 'Количество элементов, шт'


    # 4. Отрисовка
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    
    # Рисуем ячейки. align='center' ставит центр столбика ровно на координату X
    ax.bar(x_centers, plot_counts, width=cell_width * 0.98, 
           color='firebrick', edgecolor='black', alpha=0.8, zorder=3, label='Распределение элементов по ячейкам')
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