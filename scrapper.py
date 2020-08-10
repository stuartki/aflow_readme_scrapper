import os
import re
from collections import defaultdict

class Flag_Dict:
  # data is a raw file readlines
  def __init__(self, data = []):
    self.data = {}
    self.count = 0
    self.add_data(data)


  def add_data(self, data, check = True):
    self.error_count = defaultdict(int)
    flag_dict = {}
    cur_key = ''
    for n in data:
      n = n.replace('\n', '')
      # split if string is "  aflow", indicates a command
        # check if there are "aflow" commands without format of first condition
      pot_command = n.split('aflow')
      if (
          # if it is in regular format, no need to check
          "  aflow" != n[:7] 
          # if there is an aflow call
          and len(pot_command) > 1 
          # if there is a following flag
          and pot_command[1] 
          # if there is a space after aflow
          and pot_command[1][0] == " "
          # check if it is just whitespace
          and not pot_command[0].replace(' ', '')
        ):
        if (n[:4] == '    '):
          self.error_count['aflow indent too large'] += 1
        else:
          if check:
            input("COMMAND FORMAT ANOMALY DETECTED: " + n)
          self.error_count['command format anomaly'] += 1
      
      # check for command format
      if ("  aflow" == n[:7]):
        flag_data = {}
        flags = n.split('  aflow ')


        index = len(flags[1])


        options = self.parse_nested(flags[1])
        # print(options)
        flag_found = False
        attribute_exists = False
        flag_data['optional_attributes'] = []
        flag_data['attributes'] = []
        flag_data['description'] = ''
        flag_data['additional_flags'] = {}
        flag_data['mandatory commands'] = {}
        flag_data['equivalent commands'] = []
        if type(options[-1]) == str and '<' in options[-1]:
          flag_data['inputs'] = options[-1].split('<')[1].split('|')


        for option in options:
          # handle attributes while valid
          if attribute_exists:
            # currently kicks out attributes when not valid
            if option == ' ':
              attribute_exists = False
              continue
            if type(option) == list:
              for o in option:
                # print(o)
                flag_data['optional_attributes'].append(o)
            elif type(option) == str:
              flag_data['attributes'] += option
            else:
              self.error_count['anomaly']+= 1

                     
          elif type(option) == str and not flag_found:
            flag = re.findall(r"--[\w\-_.]*", option)
            if option == ' ':
              continue
            if len(flag) == 0:
              if check:
                print("NO COMMAND")
                # input(option)
              self.error_count['no command'] += 1
            else:
              flag = flag[0]
              
              flag_end = re.split(r"--[\w\-_.]*", option)[1]
              # print(flag_end)
              if flag_end:
                if flag_end[0] not in [' ', '=']:
                  if check:
                    print(re.split(r"--\w\-_.*", option))
                    print(n)
                    print(flag)
                    input("INCOMPLETE COMMAND")
                  self.error_count['incomplete command'] += 1
                else:
                  if flag_end[0] == '=':
                    flag_data['attributes'] = flag_end.split('<')[0].replace('=', '')
                    attribute_exists = True
                  elif '=' in flag_end:
                    # if check:
                    #   input("ATTRIBUTES DETECTED")
                    self.error_count['attributes detected but not recorded'] += 1
                    # flag_data['attributes'] = None


                  if len(re.findall('[|]\s*-', option)) > 0:
                    flag_data['equivalent commands'].extend([n.replace(' ', '').replace('|','') for n in re.findall('[|][\s]*-*[\w\-_.]*', option)])
                    # print(n)
                    # input(flag_data['equivalent commands'])
                  add_flag = re.findall(r"--[\w\-_.]*", option)
                  if len(add_flag) > 0:
                    flag_data['mandatory commands'].update({f: {} for f in add_flag if (f not in flag_data['equivalent commands'] and f != flag)})
                 
                # flag_data['attributes'] = None
              flag_found = True
          else:
            if type(option) == str:
              if not (option == ' ' or '<' in option):
                self.error_count['str'] += 1
                # input(option)
            if type(option) == list:
              for o in option:
                if type(o) == str:
                  add_flag = re.findall(r"--[\w\-_.]*", o)
                  if len(add_flag) > 0:
                    add_commands = {flag: {} for flag in add_flag if flag != ''}
                    
                    flag_data['additional_flags'].update(add_commands)
                  add_flag = re.findall(r"-[\w\-_.]*", o)
                  if len(add_flag) > 0:
                    for f in add_flag:
                      if '-' + f not in flag_data['additional_flags'].keys():
                        flag_data['additional_flags'][f] = {}
                  

                  if o[0] == "=":
                    flag_data["optional_attributes"].append(o[1:])
                else:
                  self.error_count['anomaly']+= 1
            
              # flag_data['optional flags'] = option
            else: 
              self.error_count['anomaly'] += 1
          # if flag == "--bandgap":
          #   print(n)
          #   print(option)
          #   input(flag_data)
        # if check:
        # print(flag)
        # print(flag_data)
        # print(n)
        # input()

        if flag_data['attributes']:
          flag += '='
        
        if flag in flag_dict.keys():
          # print(flag)
          # print(flag_dict[flag])
          # input("ERROR")
          self.error_count['duplicate flags'] += 1
        
        cur_key = flag
        flag_dict[flag] = flag_data
        # print(flag)
        # print(flag_dict)
        # input()
      elif cur_key:
        flag_dict[cur_key]['description'] += n.lstrip() + '\n'
    self.data.update(flag_dict)
    return flag_dict

  def handle_options(self, text):
    if type(text) == str:
      return text.split('|')

  def self_check(self, data):
    count = 0
    cur_key = ''
    for n in data:
      temp_n = ""
      temp_n += n
      n_found = False
      n = n.replace('\n', '')
      
      # check for command format
      if ("  aflow" == n[:7]):
        if type(n) == str:
          flag = re.findall(r"--[\w\-_.]*", n)
          # if n == ' ':
          #   continue
          if len(flag) != 0:

            cur_key = flag[0]
            if re.split(r"--[\w\-_.]*", n)[1]:
              if re.split(r"--[\w\-_.]*", n)[1][0] == '=':
                cur_key = flag[0] + '='
        temp_n = temp_n.replace("  aflow ", '')
        if cur_key and cur_key in self.data.keys():
          temp_n = temp_n.replace(cur_key, '')
          cur_data = self.data[cur_key]
          for k, v in cur_data.items():
            
            if k == 'description':
              continue
            if k == "additional_flags" or k == "mandatory commands":
              for key, value in v.items():
                if key not in n:
                  print(key)
                  print(n)
                else:
                  temp_n = temp_n.replace(key, '')
            if type(v) == list:
              for att in v:
                if type(att) != str:
                  print("att not str")
                  continue
                if att not in n:
                  print("att not in")
                  print(k)
                  print(v)
                  print(att)
                  print(n)
                  # input()
                else:
                  temp_n = temp_n.replace(att, '')
            elif type(v) == str:
              if v not in n:
                print("v not in")
                print(k)
                print(v)
                print(n)
                # input()
              else:
                temp_n = temp_n.replace(v, '')
        elif cur_key and cur_key not in self.data.keys():
          print("not in data")
          print(cur_key)
          print(n)
          # input()
        temp_n = temp_n.replace('<', '').replace('|', '').replace('[]', '').lstrip()
        if temp_n and cur_key in self.data.keys():
          
          print(cur_key)
          print(n)
          print(self.data[cur_key])
          print()
          print("not all attributes in")
          print(temp_n)
          input()
          count+=1
    print(count)
    



    


  def parse_nested(self, text, left=r'[\[]', right=r'[\]]', sep=r','):
    """ Based on https://stackoverflow.com/a/17141899/190597 (falsetru) """
    pat = r'({}|{})'.format(left, right)
    tokens = re.split(pat, text)    
    stack = [[]]
    for x in tokens:
        if not x: continue
        if re.match(left, x):
            stack[-1].append([])
            # NOT a new array object, a reference to stack[-1][-1] -> works to direct at "else" point
            stack.append(stack[-1][-1])
        elif re.match(right, x):
            stack.pop()
            if not stack:
                raise ValueError('error: opening bracket is missing')
        else:
            stack[-1].append(x)
    if len(stack) > 1:
        raise ValueError('error: closing bracket is missing')
    return stack.pop()
  def pprint(self):
    for k, v in self.data.items():
      print(k + ": ")
      print(v)
      print()
  def find(self, text):
    for k,v in self.data.items():
      if text == k:
        return v
      if text in k['equivalent commands']:
        return v
    return "key does not exist"
  
if __name__ == "__main__":
  readmes = [n for n in os.listdir(os.getcwd()) if "README_AFLOW_ACONVASP" in n]
  count = 0
  total_dict = Flag_Dict()
  for readme in readmes:
    with open(readme, 'r') as file:
      data = file.readlines()
    # for n in data:
    #   print(repr(n))
    #   raw_input("")
    total_dict.add_data(data, check = False)
  # print(len(total_dict.data))
  # print(total_dict.error_count)
  total_dict.self_check(data)
  # total_dict.pprint()]

  #write
  import json
  print(json.dumps(total_dict.data))
  with open('readme_aflow_aconvasp.json', 'w') as file:
    file.write(json.dumps(total_dict.data))


