
import distance as dist

def clusterNotions(setNotion, threshold=0.5):
    # Takes a set of notions and a threshold and returns a partition of
    # this set into lists of similar notions.
    # The greater the threshold, the finer the partition.
    processedNotions = dict() # assign to each notion an int-label such that
    # agreg[notion1] = agreg[notion2] iff notion1 and notion2 should be merged
    for notion in setNotion:
        similarNotions = [notion2 for notion2 in processedNotions if dist.distance(notion,notion2) >= threshold]
        if similarNotions != []:
            label = min([processedNotions[notion2] for notion2 in similarNotions])
            processedNotions[notion] = label
            for notion2 in similarNotions:
                processedNotions[notion2] = label
        else:
            i = 0
            while i in processedNotions.values():
                i += 1
            processedNotions[notion] = i
    # build a set of sets based on processedNotions
    agregatedNotions = []
    for i in set(processedNotions.values()):
        agregatedNotions.append([notion for notion in processedNotions if processedNotions[notion] == i])
    return agregatedNotions