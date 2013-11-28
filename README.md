Timclock
========

Django Project for site tracking worker hours.

This project uses Django 1.5 and is a test case using 12th Avenue Iron's, of Seattle, pay schedule which
has pay periods as follows:

1)  There are 2 pay periods per month.

2)  First pay period is from the 1st of the month through the 15th of the month. The second period starts on
    the 16th of the month and runs through the last day of the month.
   
3)  The process of calculating overtime in this situation is complicated by Washington law that requires hours
    overtime to be calculated on a Sunday through Saturday basis. Hours for Sunday through Saturday are summed
    and anything over forty hours for that period is considered overtime. 
    
    A problem arises when a payperiod starts in the middle of the week. For example: If a payperiod starts on
    a Wednesday, hours from the previous Sunday through Tuesday have been paid in the last pay period, but the
    hours still need to be considered for overtime for the 'OT workweek' that won't end until the Saturday in
    the first week of the new payperiod.
    
    This project must address not only the hours of a current period, but also figure out overtime for any hours
    that need to be considered for overtime in from the last period, all the while making sure not to pay twice
    for the previous hours which, in most cases, were already paid as regular hours for in the previous paycheck.
