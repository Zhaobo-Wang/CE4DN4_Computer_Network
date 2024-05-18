#!/usr/bin/env python3

########################################################################
# Increment function for a variable.

def increment_counter(counter):
   for i in range(number_of_increments):
      counter += 1

########################################################################      

counter = 0
number_of_increments = 10000

correct_result = counter + number_of_increments

increment_counter(counter)

print("counter = ", counter, end='')
print(" (correct result is {})".format(correct_result))



