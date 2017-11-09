from .Slit import Slit
from .PointSource import PointSource
from numpy import random
def makeSources(Slit, amplitude, spacing_type):
    
    if spacing_type.lower() == "uniform":
    
        if Slit.num_sources == 1:
        
            testSource = PointSource(Slit.x, Slit.y + Slit.width/2, amplitude)
            Slit.sources.append(testSource)
    
        elif Slit.num_sources == 2:
        
            spacing = Slit.width / (Slit.num_sources - 1)
            ts1 = PointSource(Slit.x, Slit.y, amplitude)
            ts2 = PointSource(Slit.x, Slit.y + Slit.width, amplitude)
            Slit.sources.append(ts1)
            Slit.sources.append(ts2)
        
        else:
        
            spacing = Slit.width / (Slit.num_sources - 1)
            ts_first = PointSource(Slit.x, Slit.y, amplitude)
            Slit.sources.append(ts_first)
        
            y_position = spacing
        
            for i in range(0, Slit.num_sources - 2):
                Slit.sources.append(PointSource(Slit.x, Slit.y + y_position, amplitude))
                y_position = y_position + spacing
        
            ts_last = PointSource(Slit.x, Slit.y + Slit.width, amplitude)
            Slit.sources.append(ts_last)
            
    elif spacing_type.lower() == "random":
        
        for point in range(0,Slit.num_sources):
            y_position = random.rand(1,1)[0][0] * Slit.width
            Slit.sources.append(PointSource(Slit.x, Slit.y + y_position, amplitude))
            