import numpy as np
import math

def linear_fit (values):
    '''values = [x, y, dy]'''
    data = np.array(values)
    x_data = data[:, 0]
    y_data = data[:, 1]
    y_errors = data[:, 2]
    a = 0
    for i in range(len(x_data)):
        a+=(x_data[i]*y_data[i])/y_errors[i] 
    c = 0
    for i in range(len(x_data)):
        c += (x_data[i])**2/y_errors[i]
    g = 0
    for i in range(len(x_data)):
        g += x_data[i]/y_errors[i]
    j = 0
    for i in range(len(x_data)): 
        j += 1/y_errors[i]
    l = 0
    for i in range(len(x_data)):
        l += y_data[i]/y_errors[i]
    k = (a*j - g*l)/(j*c - g**2)
    b = (l - k*g)/j 
    det = j*c - g**2
    r = 0
    for i in range (len(x_data)):
        r += ((k*x_data[i] + b - y_data[i])**2/y_errors[i]**2)
        
    r_av = math.sqrt(r/(len(x_data)-2))
    dk = r_av*(j/det)
    db = r_av*(c/det)
    #print(dk, db)
    return k, b, dk, db

def hyperbola_fit (values):
    '''values = [x, y, dy]'''
    data = np.array(values)
    x = data[:, 0]
    y = data[:, 1]
    dy = data[:, 2]
    
    a = sum([1/(x[i]*dy[i])**2 for i in range(len(x))])
    c = sum([1/(x[i]*(dy[i]**2)) for i in range(len(x))])
    d = sum([y[i]/(x[i]*(dy[i]**2)) for i in range(len(x))])
    g = sum([y[i]/(dy[i]**2) for i in range(len(x))])
    f = sum([1/dy[i]**2 for i in range(len(x))])

    k = (c*g-d*f)/(c**2-f*a)
    b = (d*c-g*a)/(c**2-f*a)

    r_av = math.sqrt(sum([(((k/x[i]) + b - y[i])**2)/(dy[i]**2) for i in range(len(x))])/(len(x) - 2))
    
    dk = r_av*(f/(f*a - c**2))
    db = r_av*(a/(f*a - c**2))
    
    return k, b, dk, db