#!/usr/bin/env python3

########################################################################
# Increment funcion for a variable in a dictionary.

def increment_counter(counter):
   for i in range(number_of_increments):
      counter["value"] += 1

########################################################################            

counter = { "value" : 0 } # Dictionary containing my counter.
number_of_increments = 10000

correct_result = counter["value"] + number_of_increments

increment_counter(counter)

print("counter[\"value\"] = ", counter["value"], end='')
print(" (correct result is {})".format(correct_result))



