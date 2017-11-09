from .Slit import Slit
def makeSlits(Grating, slit_width, num_sources):

    # This function will create a set amount of slits based on the amount of slits a Grating class wants. Each slit is created with
    # 'num_sources' number of sources with a slit width of 'slit_width.' Depending on the amount of sources a grating wants, this
    # function sets up different diffraction scenarios, like single slit diffraction, double slit diffraction, and Grating 
    # diffraction

    if Grating.num_slits == 1:
        # Modeling Single Slit Diffraction
        
        # place a slit in the middle of the Grating.
        # Note: the y position of a slit is defined as its endpoint closest to the x axis
        
        center = Grating.length/2
        this_slit = Slit(Grating.x, center - slit_width/2, slit_width, num_sources, [])
        #make_sources(this_slit, )
        # we make the slit and add it to the slits array in this Grating, signifying that it is 'in' this Grating
        Grating.slits.append(this_slit)
        
    elif Grating.num_slits == 2:
        # Modeling Double Slit Diffraction
        
        # place two slits, with one 'slit_width' of distance between them
        
        center = Grating.length/2
        slit_1 = Slit(Grating.x, center - slit_width*1.5, slit_width, num_sources, [])
        slit_2 = Slit(Grating.x, center + slit_width*1.5, slit_width, num_sources, [])
        Grating.slits.append(slit_1)
        Grating.slits.append(slit_2)
        
    elif Grating.num_slits > 2:
        # Modeling a Grating with num_slits
        # this Grating is expected to have at least a slit_width of distance between each slit
        # num_slits is a variable input and each should start from the center and built outwards
        
        if Grating.num_slits%2 == 0:
            
            center = Grating.length/2
            
            i = 0
            
            while Grating.num_slits/2 > i:
                
                slit1_y = center + slit_width*0.5 + 2*i*slit_width
                slit2_y = center - slit_width*1.5 - 2*i*slit_width
                
                slit_1 = Slit(Grating.x, slit1_y, slit_width, num_sources, [])
                slit_2 = Slit(Grating.x, slit2_y, slit_width, num_sources, [])
                Grating.slits.append(slit_1)
                Grating.slits.append(slit_2)
                
                i+= 1
            
        else:
            
            center = Grating.length/2
            
            first_slit = Slit(Grating.x, center - slit_width/2, slit_width, num_sources, [])
            Grating.slits.append(first_slit)
            
            i = 0
            
            while (Grating.num_slits-1)/2 > i:
                
                slit1_y = center + slit_width*1.5 + 2*i*slit_width
                slit2_y = center - slit_width*2.5 - 2*i*slit_width
                
                slit_1 = Slit(Grating.x, slit1_y, slit_width, num_sources, [])
                slit_2 = Slit(Grating.x, slit2_y, slit_width, num_sources, [])
                Grating.slits.append(slit_1)
                Grating.slits.append(slit_2)
                
                i+= 1
            
            
            
            
    else:
        
        print("??")