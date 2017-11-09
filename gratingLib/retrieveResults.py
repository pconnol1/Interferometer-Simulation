def retrieveResults(jobResults):
    # this function just loops through the results of a job submission and appends them to one single array
    results = []
    for job in jobResults:
        for result in job():
            results.append(result)
    return results