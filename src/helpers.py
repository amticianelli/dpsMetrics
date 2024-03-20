import datetime

def timeis(func): 
    '''Decorator that reports the execution time.'''
  
    def wrap(*args, **kwargs): 
        start = datetime.datetime.now()
        result = func(*args, **kwargs) 
        end = datetime.datetime.now()
        duration = end - start
          
        print(f'''Started at: {start.strftime('%Y-%m-%d %H:%M:%S')}
Ended at:   {end.strftime('%Y-%m-%d %H:%M:%S')}
Duration: {(duration.seconds // 3600):0{2}}:{(duration.seconds % 3600 // 60):0{2}}:{(duration.seconds % 60):0{2}}''')
        return result 
    return wrap