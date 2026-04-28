import numpy as np

def universal_fit(values, degrees=[1, 2, 3], auto=False):
    """
    values: [[x, y, dy], ...]
    degrees: список степеней, например [-2, -1, 1, 2, 3]
    auto: если True, попробует найти лучший набор из стандартных и отрицательных степеней
    """
    data = np.array(values)
    x, y, dy = data[:, 0], data[:, 1], data[:, 2]
    
    # Чтобы избежать деления на ноль при отрицательных степенях
    if any(d < 0 for d in degrees) and np.any(x == 0):
        raise ValueError("Данные содержат x=0, что недопустимо для отрицательных степеней.")

    def solve_for_degrees(degs):
        # Строим матрицу дизайна: столбцы — это x^degree
        # Каждое значение x_i возводится в каждую степень из списка degs
        # Добавляем 0 в список степеней для свободного члена (константы d)
        actual_degs = sorted(list(set(degs + [0])), reverse=True)
        
        # Матрица A для системы A*W*X = B*W
        A = np.column_stack([x**d for d in actual_degs])
        
        # Применяем веса (W = 1/dy)
        W = 1.0 / dy
        Aw = A * W[:, np.newaxis]
        Yw = y * W
        
        # Решаем задачу МНК
        coeffs, residuals, rank, s = np.linalg.lstsq(Aw, Yw, rcond=None)
        
        # Расчет ковариационной матрицы для ошибок
        # (Aw.T * Aw)^-1
        try:
            cov = np.linalg.inv(Aw.T @ Aw)
            errors = np.sqrt(np.diag(cov))
        except np.linalg.LinAlgError:
            errors = np.full(len(coeffs), np.nan)

        # Оценка качества (Chi-Square)
        y_fit = A @ coeffs
        chi_sq = np.sum(((y_fit - y) / dy)**2)
        dof = len(x) - len(actual_degs)
        chi_sq_red = chi_sq / dof if dof > 0 else np.nan
        
        return coeffs, errors, chi_sq_red, actual_degs

    if auto:
        # Пример логики auto: проверяем комбинации от простых к сложным
        potential_sets = [[1], [1, 2], [1, 2, 3], [-1, 1], [-2, -1, 1]]
        results = [solve_for_degrees(s) for s in potential_sets]
        # Выбираем тот набор, где chi_sq_red ближе всего к 1
        best = min(results, key=lambda r: abs(1 - r[2]) if not np.isnan(r[2]) else float('inf'))
        coeffs, errors, chi_sq_red, actual_degs = best
    else:
        coeffs, errors, chi_sq_red, actual_degs = solve_for_degrees(degrees)

    return {
        "formula": " + ".join([f"k_{d}*x^{d}" for d in actual_degs]),
        "coeffs": coeffs,
        "errors": errors,
        "chi_sq_red": chi_sq_red,
        "degrees": actual_degs
    }
