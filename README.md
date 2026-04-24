[English](#english) | [Русский](#russian)

### Russian <a name="russian"></a>
# Про что здесь 
Библиотека написана для личного удобства построения графиков и аппроксимации. Пишу ее по ходу обучения в вузе, чтобы было удобно техать лабы. 
Реализация всех методов сделана исключительно опираясь на требования преподавателей, а не на здравый смысл. 
# Структура
Все функции рабиты на два лагеря: аппроксимация и построение. Хорошо работают как в паре, так и по отдельности.
## Аппроксимация
Самая лоукод часть функции и самая приятная с токи зрения математики. 
Здесь реализован метод $$\chi ^2 $$ для многочлена 1 и -1 степени (прямая или гипербола). 
Как выглядит на бумаге: 

$$\chi^2 = \sum_{i=1}^{N} \frac{ \Delta y_i^2}{\sigma_i^2 }$$

$$
\begin{cases}
    \frac{\partial \chi^2}{\partial k} = k \sum \frac{x_i^2}{\sigma_i^2} + b \sum \frac{x_i}{\sigma_i^2} - \sum \frac{x_i y_i}{\sigma_i^2} = 0 \\
    \\
    \frac{\partial \chi^2}{\partial b} = k \sum \frac{x_i}{\sigma_i^2} + b \sum \frac{1}{\sigma_i^2} - \sum \frac{y_i}{\sigma_i^2} = 0
\end{cases}
$$

Решая такую систему, получим $$k$$ и $$b$$ для линейной зависимости.
Погрешности коэффициентов: 

$$s^2 = \frac{ 1} {N-2} \sum \frac{\Delta y^2 }{ \delta_i^2}$$
$$ dk = s \cdot \frac{1}{\Delta} \cdot \sum_{i}^{n} \frac{1}{\sigma_i}$$
$$ db = s \cdot \frac{1}{\Delta} \cdot \sum_{i}^{n} \frac{x^2}{\sigma_i}$$
$$\text{где} \ \Delta - \text{определитель матрицы системы}$$

В коде же все это дело не отличается красотой. В будущем перепишу на матрицы.

## Графики 
Тут просто. 
Есть два метода: плот **точек с зависимостью** (линейная, гипербола и экспонента) или без (зависимости или точек) и плот гистограммы. 
### Точки и зависимость
Можно построить просто точки или просто зависимость. Работает так:
 - Подается список словарей вида:
    ```
      {
      'values': [x[], y[], dy[]] (опционально), 
      'approx': [k, b, dk, db] (опционально),
      'approx_type': 'linear' | 'hyperbola' | 'exponential',
      'label': 'Эксперимент 1',
      'color': 'firebrick'
      }
    ```
 - Указываются остальные параметры (название, зум, путь сохранения и тп)
 - Плот
### Гистограмма 
Сделана для проверки гауссова распределения. 
- Подается список вида
  ```
  [[столбец 1 (ячейка 1), количество элементов в ячейке 1], [столбец 2 (ячейка 2), количество элементов в ячейке 2], ...]
  ```
- Задается параметр density (`True` - рассчет Гауссовой кривой, `False` - просто гистограмма)
- Пути, зумы, размеры ячеек и тп
- Плот

Отмечу, что к каждому методу есть быстрая документация.

# Быстрый старт
```python
data_1 = {
    'values': c,
    'approx': st.linear_fit(c),
    'approx_type': 'linear',
    'label': 'Эксперимент',
    'color': 'firebrick'
}

data_2 = {
    'approx': [0.6, 331.6, 0, 0],
    'approx_type': 'linear',
    'label': 'Теория',
    'color': 'blue'
}

plot([data_1, data_2], zoom_factor=0.1, x_limits=[20,60] , title=r'Зависимость скорости звука от температуры', xlabel=r'$T, ^\circ C$', ylabel='c, м/с', saving='D:/Physics/labs 2/13/tex/img/volume.png')
```

### English <a name="english"></a>
# Overview
This library was created for personal convenience in plotting and data approximation. I am developing it alongside my university studies to streamline the process of "TeXing" (typesetting) lab reports.

Note: The implementation of all methods is strictly based on specific faculty requirements rather than "common sense" or industry standards.

# Structure
The toolkit is divided into two main modules: **Approximation** and **Plotting**. They are designed to work seamlessly together or as standalone tools.

## Approximation
The most straightforward part of the code, yet the most mathematically satisfying.
It implements the $\chi^2$ (Chi-squared) method for 1st and -1st degree polynomials (linear and hyperbolic fits).

Mathematical basis:

$$\chi^2 = \sum_{i=1}^{N} \frac{ \Delta y_i^2}{\sigma_i^2 }$$

To find the coefficients, the following system of equations is solved:

$$
\begin{cases}
    \frac{\partial \chi^2}{\partial k} = k \sum \frac{x_i^2}{\sigma_i^2} + b \sum \frac{x_i}{\sigma_i^2} - \sum \frac{x_i y_i}{\sigma_i^2} = 0 \\
    \\
    \frac{\partial \chi^2}{\partial b} = k \sum \frac{x_i}{\sigma_i^2} + b \sum \frac{1}{\sigma_i^2} - \sum \frac{y_i}{\sigma_i^2} = 0
\end{cases}
$$

Solving this system yields $k$ and $b$ for the linear dependence.
Coefficient uncertainties (errors):

$$s^2 = \frac{ 1} {N-2} \sum \frac{\Delta y^2 }{ \delta_i^2}$$

$$ dk = s \cdot \frac{1}{\Delta} \cdot \sum_{i}^{n} \frac{1}{\sigma_i}$$

$$ db = s \cdot \frac{1}{\Delta} \cdot \sum_{i}^{n} \frac{x^2}{\sigma_i}$$

where $\Delta$ is the determinant of the system matrix.

*Current Status:* The internal code is a bit messy; a future refactor using matrix operations is planned.

## Plotting
This module provides two main methods: plotting data points with fits and plotting histograms.

### Points and Approximation
Supports plotting experimental points, their fits (linear, hyperbolic, or exponential), or both.
**Workflow:**
- Pass a list of dictionaries in the following format:
    ```python
    {
      'values': [x[], y[], dy[]] (optional), 
      'approx': [k, b, dk, db] (optional),
      'approx_type': 'linear' | 'hyperbola' | 'exponential',
      'label': 'Experiment 1',
      'color': 'firebrick'
    }
    ```
- Configure additional parameters (title, zoom, save path, etc.).
- Call the plot function.

### Histograms
Designed for Gaussian distribution verification.
- Input data format:
  ```python
  [[bin_1_center, count_1], [bin_2_center, count_2], ...]
  ```
- `density` parameter: Set to `True` to calculate and overlay a Gaussian curve, or `False` for a standard histogram.
- Supports customization of paths, zoom, and bin sizes.

*Note: Each method includes docstrings for quick reference.*

# Quick Start
```python
data_1 = {
    'values': c,
    'approx': st.linear_fit(c),
    'approx_type': 'linear',
    'label': 'Эксперимент',
    'color': 'firebrick'
}

data_2 = {
    'approx': [0.6, 331.6, 0, 0],
    'approx_type': 'linear',
    'label': 'Теория',
    'color': 'blue'
}

plot([data_1, data_2], zoom_factor=0.1, x_limits=[20,60] , title=r'Зависимость скорости звука от температуры', xlabel=r'$T, ^\circ C$', ylabel='c, м/с', saving='D:/Physics/labs 2/13/tex/img/volume.png')
```
