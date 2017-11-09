import math
def processInputForJobs(inputGrating,observingPositions,numJobs):
    
    # this code takes a Grating object, an array of observing positions, and the number of jobs and returns all the necessary
    # information for the parallelization of this code
    
    # each job requires their own chunk of observing positions to examine, and this breaks up obersving positions as such
    
    pointSourcePositions = [] # array that will be populated with the point source locations
    pointSourceAmplitudes = [] # array that will be populated with each source amplitude
    jobDataTotal = [[] for _ in range(numJobs)] # array of arrays that will hold the divided up observing positions
                                                # each array will be the chunk of observing positions for each job
    
    # grabs all information from the illuminated grating that we need; i.e., point source positions and amplitudes
    for ithSlit in inputGrating.slits:
        for jthSource in ithSlit.sources:
            pointSourcePositions.append(jthSource.y)
            pointSourceAmplitudes.append(jthSource.amplitude)
            
    # these loops divide up the number of observing positions to ensure that each job has about the same amount of work
    if len(observingPositions)%numJobs != 0:
        
        # current index keeps track of the actual index in the larger array of undivided observing positions
        # i is the ith array in jobDataTotal, which we must keep track of outside the loop. This loop round up
        # the number of observing positions divided by the number of jobs for the first n-1 jobs, and the final nth job
        # is given the remaining observing positions 
        
        currentIndex = 0
        i = 0
        
        # populate the first n-1 arrays in jobDataTotal with math.ceil(observingPositions/numJobs) number of jobs, parsing
        # through data with currentIndex
        for i in range(len(jobDataTotal)-1):
            for _ in range(int(math.ceil(len(observingPositions)/numJobs))):
                jobDataTotal[i].append(observingPositions[currentIndex])
                currentIndex += 1
                
        # populated the final array with the remaining data in observingPositions
        while currentIndex < len(observingPositions):
            jobDataTotal[i+1].append(observingPositions[currentIndex])
            currentIndex += 1
            
    else:
        # if observingPositions/numJobs is an even number, just populate each array with the same amount of observingPositions
        currentIndex = 0
        for jobData in jobDataTotal:
            for _ in range(int(len(observingPositions)/numJobs)):
                jobData.append(observingPositions[currentIndex])
                currentIndex += 1
        
    return jobDataTotal, pointSourcePositions, pointSourceAmplitudes