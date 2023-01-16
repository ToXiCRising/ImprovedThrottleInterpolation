#%%
'''
Tries to implement an improved throttle interpolation scheme for use in sim racing games.
Discussion of the topic, by Niels Heusinkveld can be found here: https://youtu.be/0gW-cbSX3Uc
Goal: https://www.researchgate.net/figure/Predicted-Engine-output-torque-for-different-throttle-positions-and-engine-speeds_fig3_286637947
'''
import matplotlib.pyplot as plt
import ipywidgets

#%%

#------Basic math------
def map(x: float, A: float, B: float, C: float, D: float) -> float: 
    '''
    Maps a value x, contained in range A to B to range C to D
    '''
    return (x-A)/(B-A)*(D-C)+C

def reverse_smoothstep(x: float, lower_edge: float, higher_edge: float) -> float:
    '''
    Reverse smoothstep between 1 and 0 from lower edge to higher edge
    '''
    x = (x - lower_edge)/(higher_edge - lower_edge)
    if x < 0: return 1
    if x > 1: return 0
    else: return 3*(-x+1)**2 - 2*(-x+1)**3

#------Throttle interpolation------

def rpm_based_percentage(rpm: list[float], percent: float, min_rpm: int, max_rpm: int, low_rpm_cutoff: int = 40) -> float:
    '''
    Returns an RPM-based throttle percentage
    '''
    if percent == 100: return 100
    if percent == 0: return 0

    #Creates the boundaries for the smoothstep function
    mean_rpm = (max_rpm - min_rpm)/2
    #Linear scale for moving the lower edge; minus a slight offset, that causes a quicker release from the full throttle curve 
    lower_edge = min_rpm + percent/100 * max_rpm - 1/3*mean_rpm
    higher_edge = max_rpm

    #Scales the smoothstep for low throttle inputs, causes a fill for low rpm, low throttle torque values
    #To toggle the effect set low_rpm_cutoff to 0
    if percent > low_rpm_cutoff: low_rpm_modifier = 1
    else: low_rpm_modifier = (1-0.1)/low_rpm_cutoff * percent + 0.1

    return map(low_rpm_modifier*reverse_smoothstep(rpm, lower_edge, higher_edge), 0, 1, percent, 100)
    

def percent_throttle(percent: float, rpms: list[float], zero_throttle: list[float], full_throttle: list[float]) -> list[float]:
    '''
    Returns the interpolated throttle curve at given pedal position
    '''
    percent_throttle = [0]*len(rpms)
    for i in range(len(percent_throttle)):
        rpm_percent = rpm_based_percentage(rpms[i], percent, rpms[0], rpms[-1])
        percent_throttle[i] = map(rpm_percent, 0, 100, zero_throttle[i], full_throttle[i])
    return percent_throttle

#------Plotting------

def plot_fnc_nb(data: list[list[float]], percent: float = 50) -> None:
    plt.axhline(y = 0, color = "black", linestyle = "--")  
    
    #Calculates the throttle curves
    throttle = percent_throttle(percent, data[0], data[1], data[2])
    plt.plot(data[0], throttle, "--.", label = str(percent) + "%")
    plt.plot(data[0], data[2])
    plt.plot(data[0], data[1])

    plt.title("Improved Throttle Interpolation")
    plt.xlabel("RPM")
    plt.ylabel("Torque")
    plt.legend(title = "Throttle", loc = "center right", bbox_to_anchor=(1.2, 0.5))
    plt.show()

def plot_fnc_plt(data: list[list[float]]) -> None:
    
    plt.axhline(y = 0, color = "black", linestyle = "--")  
    
    #Calculates the throttle curves
    for i in range(10,100,10):
        throttle = percent_throttle(i, data[0], data[1], data[2])
        plt.plot(data[0], throttle, "--.", label = str(i) + "%")
    plt.plot(data[0], data[2])
    plt.plot(data[0], data[1])

    plt.title("Improved Throttle Interpolation")
    plt.xlabel("RPM")
    plt.ylabel("Torque")
    plt.legend(title = "Throttle", loc = "center right", bbox_to_anchor=(1.2, 0.5))
    plt.tight_layout()
    plt.show()

#------Housekeeping------

def is_notebook() -> bool:
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter


def main():
    #Rpm and full throttle data is ripped from power.lut of the RSS P91 Protech mod for Assetto Corsa
    rpms = [0, 600, 1200, 1800, 2400, 3000, 3600, 4200, 4800, 5400, 6000, 6600, 7200, 7800, 8400, 9000]
    full_throttle = [76.2201927039884, 
                     85.2201927039884, 
                     97.274668269767, 
                     105.332645084612,
                     117.189815680606,
                     131.892934724673,
                     143.735962118113,
                     155.676387883048,
                     167.99159344944,
                     179.579001269405,
                     189.137434603863,
                     194.121323315241,
                     191.553876739733,
                     184.036948579523,
                     169.492484637706,
                     148.561866760253]
    #Generates a simple linear engine inertia curve for zero throttle
    zero_throttle = []
    for i in rpms:
        zero_throttle.append((-40+10)/(rpms[-1]-rpms[0])*i - 10)

    data = [None]*3
    data[0] = rpms
    data[1] = zero_throttle
    data[2] = full_throttle
    
    if(is_notebook()):
        ipywidgets.interact(plot_fnc_nb, data = ipywidgets.fixed(data), percent = (0, 100, 1))
    else:
        plot_fnc_plt(data)


if __name__ == '__main__':
    main()

# %%
