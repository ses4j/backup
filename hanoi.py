""" Implementation of the tower-of-hanoi backup rotation pattern. """

import os

def hanoi(numDisks):
    numDisks = int(numDisks)
    lst = []
    for day in range(1,2**numDisks):
        #~ print day,
        for n in range(numDisks):
            # test nth bit of day number and bail if True
            if day & (2**n):
                lst.append(n+1)
                break
    return lst

def get_current_hanoi_slot(days_since_any_epoch, numDisks = 3):
    hanoi_list = hanoi(numDisks)

    hanoi_index = int(days_since_any_epoch) % (len(hanoi_list)-1)
    #~ print "idx=",hanoi_index,
    #~ print "day_id=",days_since_any_epoch,
    #~ print hanoi_list,

    return hanoi_list[hanoi_index]-1

def testandplay():
    numDisks = 8
    backups = [-1000000000000 for x in range(numDisks)]
    base_backup_target_path = r'C:\temp\backup'
    
    worst_max_age = 10000000
    for day in range(60000):
        slot_to_use = get_current_hanoi_slot(day, numDisks = numDisks)
        backups[slot_to_use] = day
        age_of_backups = [day-x for x in backups]
    
        worst_max_age = min([worst_max_age, max(age_of_backups)])
        print worst_max_age,
        print "%3d %3d %17s backup age: max=%3d avg=%.1f"%(day,slot_to_use,str(age_of_backups),max(age_of_backups),sum(age_of_backups)/len(age_of_backups))
    
    
    
