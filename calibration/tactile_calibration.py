import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize
import glob
import random

adc_max = 1024
adc_min = 20

def strain_to_force(strain, strain_0g, strain_weight, weight):
    d_strain_1g = (strain_weight - strain_0g) / weight
    weight_g = (strain - strain_0g) / d_strain_1g
    weight_kg = weight_g / 1000
    force = weight_kg * 9.81
    return force

def read_data(filename, strain_0g, strain_weight, weight, n):
    data = np.genfromtxt(filename)
    data = [[strain_to_force(row[0], strain_0g, strain_weight, weight), row[1]] for row in data]
    data = np.array(data)
    data[:,1] /= n
    return data
    
def model(row, parameters):
    surface_resistance = parameters[0] * 1000.0
    reference_resistance = row[3]
    force = row[0]
    internal_resistance = parameters[int(row[2] % 3 + 1)] * 1000.0
    sensor_resistance = surface_resistance / force * 2 + internal_resistance
    output_voltage = reference_resistance / sensor_resistance
    adc_reading = max(adc_min, adc_max * (1.0 - output_voltage))
    return adc_reading

def loss(parameters):
    v = 0.0
    for dat in data:
        for row in dat:
            d = model(row, parameters) - row[1]
            v += d * d / len(dat)
    for i in range(len(parameters)):
        if parameters[i] < 0.5:
            v += 10000000
    return v
    
data = [ ]
    
strain_0g = 1660130 
strain_weight = 1667333
weight = 20*8
samples = 5
data.append([[row[0], row[1], 0, 10000] for row in read_data("10k-nosil-cylindertip.1614926403.33.txt", strain_0g, strain_weight, weight, samples)])
data.append([[row[0], row[1], 1, 10000] for row in read_data("10k-thinsil-cylindertip.1614926690.65.txt", strain_0g, strain_weight, weight, samples)])
data.append([[row[0], row[1], 2, 10000] for row in read_data("10k-thicksil-cylindertip.1614927083.14.txt", strain_0g, strain_weight, weight, samples)])

strain_0g = 8322237 
strain_weight = 8341540
weight = 50
samples = 5
data.append([[row[0], row[1], 3, 1000] for row in read_data("none.1614726111.69.txt", strain_0g, strain_weight, weight, samples)])
data.append([[row[0], row[1], 4, 1000] for row in read_data("thin.1614725386.31.txt", strain_0g, strain_weight, weight, samples)])
data.append([[row[0], row[1], 5, 1000] for row in read_data("thick.1614725558.06.txt", strain_0g, strain_weight, weight, samples)])

data = [np.array(d) for d in data]

solution = np.array([
    1.0,
    1.0, 1.0, 1.0, 
    ])

def opt_callback(x, f, accepted):
    print(x, f, accepted)
    
def minimize_simple(f, s):
    cl = f(s)
    for i in range(30):
        for q in [0.0625, 0.125, 0.25, 0.5, 1.0]:
            t = s + np.random.normal(size=len(s)) * q
            c = f(t)
            if c < cl:
                s = t
                cl = c
    return s
    
plt.rcParams["figure.figsize"] = (10,5)

fig, plots = plt.subplots(2, 3)

iterations = 30

for iteration in range(iterations):

    for irow in range(2):
        for icol in range(3):
            i = irow * 3 + icol
            if i < len(data):
                print "i", irow, icol, i
                d = data[i]
                plot = plots[irow][icol]
                plot.cla()
                plot.set_ylim([0,1024])
                plot.scatter(d[:,0], d[:,1], c="g", marker=".")
                ds = np.sort(d, axis=0)
                plot.plot(ds[:,0], [model(row, solution) for row in ds], c="b", linewidth=3)

    plt.tight_layout()
    
    plt.draw()
    plt.pause(0.001)
    
    if iteration == (iterations - 1):
        print("save figure")
        plt.savefig("tactile_calibration_plots.png")

    print("solving")
    solution = minimize_simple(loss, solution)
    print(solution)
    print("ready")

f = open("README.md", "w")

f.write("# Tactile sensor calibration report\n")

f.write("## Command\n")
f.write("```python "+" ".join(sys.argv)+"```\n")

f.write("## Model fitting")
f.write("![](tactile_calibration_plots.png)\n")
f.write("\n")

f.write("## Estimated model parameters\n")
f.write("Parameter | Value\n")
f.write("--- | ---\n")
f.write("R<sub>S</sub> | " + "{0:.3f}".format(solution[0]) + " k&#937;N\n")
f.write("R<sub>0</sub> | " + "{0:.3f}".format(solution[1]) + " k&#937;\n")
f.write("R<sub>1</sub> | " + "{0:.3f}".format(solution[2]) + " k&#937;\n")
f.write("R<sub>2</sub> | " + "{0:.3f}".format(solution[3]) + " k&#937;\n")
f.write("\n")

f.write("## Resistor selection\n")
f.write("Feedback resistor | No Silicone | Thin Silicone | Tick Silicone \n")
f.write("--- | --- | --- | --- \n")
for resistor in [1, 2.2, 4.7, 10, 22, 47, 100]:
    f.write(str(resistor)+" k&#937;")
    for cover in range(3):
        def range_cost(force):
            if force < 0:
                return 10000000
            return model([force, 0, cover, resistor * 1000], solution) + force * 0.01
        force_range = scipy.optimize.minimize(range_cost, 1.0, method="Nelder-Mead")["x"][0]
        print resistor, cover, force_range
        f.write(" | "+"{0:.3f}".format(force_range)+" N")
    f.write("\n")
f.write("\n")

f.close()
