#!/usr/bin/env python
'''
backup.py recursively walks a file heirarchy searching for files that have been modified 
since the last backup (user-specified date). Those files are copied to a user-selected destination folder. 
'''
import os
import sys
import subprocess as sp
import filewalker as fw
import datetime
import psutil

def exit():
	print; print 'Exiting...';print;sys.exit()

def get_search_dirs():
	print 'Enter directories to copy (absolute paths, comma-separated) or type q to quit...'
	print '  (Default is current directory)...'
	search_dirs = raw_input('Directories: ')
	if search_dirs == 'q': 
		exit()
	elif search_dirs == '':
		search_dirs = [sp.Popen(['pwd'],stdout=sp.PIPE).communicate()[0].replace('\n','')]
	else:
		search_dirs = list(set([i for i in [x.strip() for x in search_dirs.split(',')] if i]))
	print
	return search_dirs

def is_valid_date(date):
	try:
		d = datetime.datetime(*date)
	except:
		return False
	return True

def get_mod_date():
	'''get user-selected mod date cutoff, check that date is valid, and convert to epoch time'''
	while 1:
		mod_date = raw_input('Enter mod cutoff date (e.g., 2004 4 25) or q: ')
		if mod_date == 'q': exit()
		else:
			try:
				mod_date = tuple([int(x) for x in mod_date.split(' ') if x != ''])
				if is_valid_date(mod_date):
					if mod_date[0] < 1970:
						print 'Date must be after 1970.'
						continue
					break
				else:
					print 'Try a date again.'
			except:
				print 'Your date is bad.'	
	print 'Using this date:',mod_date
	mod_date = int(datetime.datetime(*mod_date).strftime('%s'))	#converted to epoch
	print
	return mod_date

def get_dest_dir():
	while 1: 
		dest_dir = raw_input('Enter destination directory or type q to quit: ')
		if dest_dir == 'q': 
			exit()
		elif dest_dir == '':
			dest_dir = sp.Popen(['pwd'],stdout=sp.PIPE).communicate()[0].replace('\n','')
		else:
			dest_dir = dest_dir.replace('\n','')
		if os.path.exists(dest_dir):
			return dest_dir 
		else:
			print 'Cannot find destination directory';print

def do_transfer(files,dirs,root,dest_dir,mod_date):
	transfer_size = sum([os.path.getsize(f.abs) for f in files if os.path.getmtime(f.abs) > mod_date])
	print 'Total files from \''+root+'\' to transfer:' 
	print '   %i files in %i directories' %(len(files),len(dirs)+1)
	print '   %d bytes (%f Mb)' %(transfer_size,1.*transfer_size/10**6)
	disk_space_avail = psutil.disk_usage(dest_dir).free
	print 'Destination dir \'%s\' has available:' %dest_dir
	print '   %d bytes (%d Mb)'%(disk_space_avail,disk_space_avail/10**6)
	print
	
	resp=' '
	while resp not in 'ynq':
		resp=raw_input('Continue transfer? (y n q): ')
	if resp == 'q': exit()
	if resp == 'n': return False
	return True

def main():
	print
	print '#--------------------------------#'
	print '#--------backup.py v. 0.1--------#'
	print '#--------------------------------#'
	print 
	
	search_dirs = get_search_dirs()
	print 'Using search_dirs as',search_dirs
	print
		
	dest_dir = get_dest_dir()
	print 'Using dest_dir as',dest_dir
	print

	mod_date = get_mod_date()
	
	for root in search_dirs:
		files,dirs,ftree = fw.walk(root=root,print_all=False)
		
		old_dir_name = root.split('/')[-1]
		
		backup_dir = dest_dir+'/'+old_dir_name+'_backup_'+str(datetime.datetime.now()).split('.')[0].replace(' ','_')
		
		print '####################'
		print 'Copying from:'
		print ' ',root
		print
		print 'Saving to:'
		print ' ',backup_dir
		print
		
		if not do_transfer(files,dirs,root,dest_dir,mod_date):
			continue
		
		sp.Popen(['mkdir',backup_dir])
		path_to_dir_copy = backup_dir+'/'+old_dir_name
		sp.Popen(['mkdir',path_to_dir_copy])
		
		for dir in dirs:	#first create directory structure
			if not os.path.exists(path_to_dir_copy+'/'+dir.rel):
				sp.Popen(['mkdir',path_to_dir_copy+'/'+dir.rel])

		for file in files:	#then add file data
			with open(file.abs,'r') as f:
				doc = f.read()
			with open(path_to_dir_copy+'/'+file.rel,'w') as f:
				f.write(doc)
		print '...Transfer complete'; print
		


if __name__ == '__main__':
	main()