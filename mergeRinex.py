import ftplib 
import datetime
import string
import gzip
import os
import argparse 
import fnmatch
import subprocess

if __name__ == '__main__':    
    #For CLI
    p = argparse.ArgumentParser()
    p.add_argument('base',help='Enter in the base')
    p.add_argument('period1',help='Enter the intial time - format:%Y-%m-%dT%H:%M:%SZ')
    p.add_argument('period2',help='Enter the final time - format:%Y-%m-%dT%H:%M:%SZ')
    args = p.parse_args()
    
    
    print('\n')
    print("***Script started***")
    #Extracting input arguments
    base = args.base
    periods = [args.period1, args.period2]
    
    if len(base)!=4:
        raise ValueError ("The argument: base is wrong...Should be 4 characters")
        
    for i in range(2):
        if len(periods[i]) != 20:
           raise ValueError ("The argument: period{} is wrong...Check format:%Y-%m-%dT%H:%M:%SZ".format(str(i+1))) 
    
    print("Requested base: "+ base)

    #Arrays for storing time data
    year = []
    day = []
    hour = []
    tim_l = []
    
    #initialise file_list for merging using TEQC
    file_list1 = []
    file_list2 = []

    #Extracting dates and times from string
    for j in range(0,2):
        try:
            tim = datetime.datetime.strptime(periods[j],'%Y-%m-%dT%H:%M:%SZ')
            tim_l.append(tim)
            print("Requested period " + str(j+1)+ ": " + str(tim))
            struct = tim.timetuple()
        except ValueError:#Error handling for wrong input
            raise ValueError("Please input periods in the following format:%Y-%m-%dT%H:%M:%SZ")
        
        year.append(struct.tm_year)
        day.append(struct.tm_yday)
        hour.append( struct.tm_hour)
    
    #Check for period to be before the current time
    for i in range(2):
        if tim_l[i]>=datetime.datetime.now():
                    raise ValueError("Period: "+ str(i+1) + " is in the future!!!!")
    
    #Error handling for period1<period2
    if year[0]>year[1]:
        raise ValueError("Period 1 should be before Period2")
    elif year[0] == year[1] and day[0]>day[1]:
        raise ValueError("Period 1 should be before Period2")
    elif year[0] == year[1] and day[0] == day[1] and hour[0]>hour[1]:
        raise ValueError("Period 1 should be before Period2")
    
    #create arrays for looping(navigation in FTP)
    years = list(range(year[0],year[1]+1))
    days = list(range(day[0], day[1]+1))
    hours = [hour[0]]+ [0]*max((len(days)-2),0) + [hour[1]]
    
    #For the file indexing of files in ftp(time)
    d = dict(enumerate(string.ascii_lowercase, 0))
    
    #Creating a new folder to save downloaded files
    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, r'zip_downloads')
    if not os.path.exists(final_directory):
        os.makedirs(final_directory) 

    #Opening ftp directory
    ftp = ftplib.FTP('ftp.ngs.noaa.gov')
    ftp.login()
    ftp.set_pasv(True)
    ftp.cwd('cors/rinex/')
    parent_dir = ftp.pwd()# Setting FTP parent directory
    
    #Defining ranges for for loop(Navigating through FTP)
    end_years = len(years)
    end_days = len(days)
    
    # Navigation through FTP and downloading files to local directory
    for m in range(0, end_years):
        for i in range(0,end_days):  
            
            ftp.cwd(parent_dir)#returns to parent directory
            ftp.cwd(str(years[m])+'/'+str(days[i])+ '/'+base+'/')#moves to the file location
           
            #creating folder to save the zip file downloads
            current_directory = os.getcwd()
            final_directory = os.path.join(current_directory, r'zip_downloads/{0}-{1}'.format(years[m],days[i]))
            if not os.path.exists(final_directory):
                os.makedirs(final_directory) 
    
            #setting ranges for the file retrieval loop
            if i == end_days-1:
                n = -1
                step = -1
            else:
                n = 24
                step = 1
            
            if end_days == 1:#For the loop to get files between in case of same day
                n = hours[1]
                step = 1
            
            #Checking if hour files are in the directory
            if end_days != 1:
                k=0
                for hour in range(hours[i], n, step):
                    pattern= "*{0}.{1}o.gz".format(d[hour],str(years[m])[2:])#pattern for time files
                    dir_files = ftp.nlst()#Read directory files
                    for f in dir_files:
                        if fnmatch.fnmatch(f,pattern):
                            k += 1
                
                #For the case when requested period have not been uploaded yet
                if k != abs(n-(hours[i])) and k>0:
                   hours[i] = k-1
                   print("\n***Only " + str(k-1) + " hours have been uploaded***")
                   print("***Will be extracting and merging these files***\n")
            
            if end_days ==1:
                k = 0
                for hour in range(hours[0],hours[1]):
                    pattern= "*{0}.{1}o.gz".format(d[hour],str(years[m])[2:])#pattern for time files
                    dir_files = ftp.nlst()#Read directory files
                    for f in dir_files:
                        if fnmatch.fnmatch(f,pattern):
                            k += 1
                if k ==0:
                    raise ValueError("No files between the required period range has been uploaded")
                
                elif k != hours[1] - hours[0]:
                    n = hours[0] + k
                    print("\n***Only " + str(n) + " hour have been uploaded")
                    print("***Will be extracting and merging from " + str(hours[0]) + " hours to " + str(n)+" hours ***\n")
               
            #If the hour files remain in directory
            print("Retrieving and extracting files from site...")
            if k == abs(n-(hours[i])):
                for hour in range(hours[i], n, step):        
                    filename = base+str(days[i])+d[hour]+'.17o.gz'
                    fil_dir = 'zip_downloads/{0}-{1}/f-{2}.gz'.format(years[m],days[i],hour)
                    if not os.path.exists(fil_dir):
                        file  = open(fil_dir, 'wb')
                        ftp.retrbinary("RETR " + filename ,file.write)
                        file.close()
                
                    with gzip.open(fil_dir,'rb') as z: 
                        outF = open('f-{0}-{1}.{2}o'.format(days[i],hour,str(years[m])[2:]), 'wb')
                        outF.write( z.read())
                        if i == end_days-1 and end_days != 1:
                            file_list2.append('f-{0}-{1}.{2}o'.format(days[i],hour,str(years[m])[2:]))
                        else:
                            file_list1.append('f-{0}-{1}.{2}o'.format(days[i],hour,str(years[m])[2:]))
                        outF.close()
        
            #If the hour files have been replaced
            else:
                filename = base+str(days[i])+'0.17o.gz'
                fil_dir = 'zip_downloads/{0}-{1}/f-day.gz'.format(years[m],days[i])
                if not os.path.exists(fil_dir):
                    file  = open(fil_dir, 'wb')
                    ftp.retrbinary("RETR " + filename ,file.write)
                    file.close()
                
                with gzip.open(fil_dir,'rb') as z: 
                    outF = open('f-{0}-day.{1}o'.format(days[i],str(years[m])[2:]), 'wb')
                    outF.write(z.read())
                    file_list1.append('f-{0}-day.{1}o'.format(days[i],str(years[m])[2:]))
                    outF.close()
    
    ftp.quit()# Closing ftp connection   
    
    print("Files have been retrived and extracted")
    
    #Merging files using Teqc
    
    #Creating the command string for merging the file
    c1 = "teqc"
    c2 = ""
    
    #list of zpped files
    file_list = file_list1 + list(reversed(file_list2))
    
    for file in file_list:
        c2 = c2 + " " + file
    
    comm = c1 + c2 + " > " + base + ".obs"
    
    #Passing merge command to the CLI
    print("Merging files...")
    subprocess.call(comm, shell = True)
    
    #Delete and cleanup all the files
    for file in file_list:
        os.remove(file)
    print("Unzipped files removed")
    
    print("Merging finished")
    print("Find the merged file in the working directory")
    print("***Script ended***")