#!/usr/bin/env python3

########################################################################
# Increment funcion for a variable in a list.

def increment_counter(counter):
   for i in range(number_of_increments):
      counter[0] += 1

########################################################################      

counter = [0] # List containing my counter.
number_of_increments = 10000

correct_result = counter[0] + number_of_increments

increment_counter(counter)

print("counter[0] = ", counter[0], end='')
print(" (correct result is {})".format(correct_result))



