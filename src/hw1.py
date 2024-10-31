import random

class task_1:
  def task1():
    odd = 0
    odd_counter = 0
    even = 0
    even_counter = 0
    list_of_numbers = random.sample(range(0, 1001), 100)
    for j in range(len(list_of_numbers)-1):
       for i in range(len(list_of_numbers)-1):
         if list_of_numbers[i+1] < list_of_numbers[i]:
           list_of_numbers[i], list_of_numbers[i+1] = list_of_numbers[i+1], list_of_numbers[i]
    for num in (list_of_numbers):
      if num % 2 != 0:
        odd = odd + num
        odd_counter = odd_counter + 1
      else:
        even = even + num
        even_counter = even_counter + 1
    if odd_counter == 0 and even_counter != 0: 
        return f'avg even = {even/even_counter}, no odd numbers' 
    elif even_counter == 0 and odd_counter != 0: 
        return f'avg odd = {odd/odd_counter}, no even numbers'
    else: 
        return print(f'avg even = {even/even_counter}, avg odd = {odd/odd_counter}')

task = task_1.task1()
