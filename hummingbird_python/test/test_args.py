import sys, getopt

def hi():
  print('hi')

# This helps: https://docs.python.org/3/library/getopt.html
if __name__ == "__main__":
  arguments = sys.argv[1:]
  options = "ab:"
  long_options = ["empty", "non-empty=", "extra"]

  try:
    arguments, _ = getopt.getopt(arguments, options, long_options)
    
    for currentArgument, currentValue in arguments:
      if currentArgument in ("-a", "--empty"):
        print('empty')
      elif currentArgument in ("-b", "--non-empty"):
        print('non-empty', currentValue)
      elif currentArgument in ("--extra"):
        print('extra')
      else:
        print('hi')
              
  except getopt.error as err:
    print(str(err))