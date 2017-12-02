# Project Title: EECS 837 LEM1 programming project
# Date: 11/21/2017

import os.path
import numpy as np


def file_reader():
	while True:		# prompt the user to type in a input file
		read_file_name = raw_input("\nPlease type the name of the input file:\n")

		# check if the file exists in the current dir
		if(os.path.exists(read_file_name)):
			write_file_name = raw_input("\nPlease type the name of the output file:\n")
			return read_file_name, write_file_name
		else:
			print 'file not found, please try again!'


def parsing(file_name):
	# read in every line into an array
	dataset = np.array([])
	with open(file_name, 'r') as f:
		# delete the first row of the data set
		lines = f.readlines()[1:]
		# remove any special characters from the original data strings
		lines = map(lambda x: x.strip('<>[]\t\n\r'), lines)
		# replace any space with a single space from the data strings
		lines = map(lambda x: ' '.join(x.split()), lines)
		# iterate every line and insert them into a 2d array
		for line in lines:
			# skip empty lines
			if not line.strip():
				continue
			column_size = len(line.split())
			line = np.array(list(line.split()))
			# initialized the dataset array if it is empty
			if dataset.size is 0:
				dataset = line.reshape(1, column_size)
			# otherwise stack the rest of the lines with the dataset array
			else:
				dataset = np.vstack([dataset, line])

	print dataset
	# close the input file
	f.close()
	return dataset


def discretization(dataset):
	# ====================================
	# calculate the cutpoints
	# ====================================
	substitution_dic = {}
	discretized_dataset = dataset
	# exclude the last column
	for column in dataset[:, 0:-1].T:
		# remove all the duplicated values
		attribute_list = list(set(column[1:]))
		# check if the column is a list of numbers
		is_num = str(''.join(attribute_list)).replace(".", "").isdigit()

		if is_num:
			# sort them in ascending order
			attribute_list = sorted(map(float, attribute_list))

			# return a list of cut points in that column
			cutpoints = [(a + b) / 2 for a, b in zip(attribute_list[:-1], attribute_list[1:])]
			# list contains all attributes and its cutpoints
			temp_list = sorted(attribute_list + cutpoints)

			# loop through all numerical values to get the symbolic values
			for idx, val in enumerate(column[1:]):
				index = temp_list.index(float(val))
				if index+1 >= len(temp_list):
					upper_bound = temp_list[index-1]
					new_val = str(upper_bound) + ".." + str(val)
				else:
					upper_bound = temp_list[index+1]
					new_val = str(val) + ".." + str(upper_bound)

				# pair up the val and new_val for replacement out of this scope
				substitution_dic[val] = new_val
		# continue if the list is not numerics
		else:
			continue
	# iterate through all elements in discretized_dataset, and substitute the numerical values
	for index, x in np.ndenumerate(discretized_dataset[:,:-1]):
		# if the current element is a number
		if str(x).replace(".", "").isdigit():
			new_x = str(substitution_dic[str(x)])
			discretized_dataset[index] = new_x
		# else continue the iterate all elements
		else:
			continue

	# return the discretized dataset
	return discretized_dataset


def bound_calc(discretized_dataset):
	A = list()
	for row1 in discretized_dataset[1:,:-1]:
		index = 1
		selected_index = list()
		for row2 in discretized_dataset[1:,:-1]:
			if str(row1) == str(row2):
				selected_index.extend([index])
			index = index + 1
		A.append(selected_index)

	# remove the duplicates
	A = [x for n, x in enumerate(A) if x not in A[:n]]
	print 'A* = ',A

	d = list()
	for row1 in discretized_dataset[1:,-1]:
		index = 1
		selected_index = list()
		for row2 in discretized_dataset[1:,-1]:
			if str(row1) == str(row2):
				selected_index.extend([index])
			index = index + 1
		d.append(selected_index)

	# remove the duplicates
	d = [x for n, x in enumerate(d) if x not in d[:n]]
	print 'd* = ',d

	# check to see if the data is consistent
	non_consistency = 0
	consistency = False
	for item1 in A:
		issubset = False
		for item2 in d:
			if set(item1) <= set(item2):
				issubset = True
		if not issubset:
			print 'there'
			non_consistency += 1
	if non_consistency is not 0:
		print '\nthe dataset is not consistent\n'
	else:
		print '\nthe dataset is consistent\n'
		consistency = True

	# put attitude and corresponding row index into a dictionary
	attitude = {}
	for item in d:
		index = item[0] - 1
		attitude[discretized_dataset[1:,-1][index]] = {}
		attitude[discretized_dataset[1:,-1][index]]['attitude'] = item

	# finding the upper and lower approximatiBons
	for item in attitude:
		lower_bound = list()
		upper_bound = list()
		for keys in attitude[item]:
			rows = attitude[item][keys]
			for x in A:
				if set(x).issubset(rows):
					lower_bound.extend(x)
				if bool(set(x) & set(rows)):
					upper_bound.extend(x)
			attitude[item] = {}

			if non_consistency is not 0:
				attitude[item]['lower_bound'] = lower_bound
				attitude[item]['upper_bound'] = upper_bound
			else:
				attitude[item]['original'] = rows

	print "attitude: ",attitude
	return attitude, consistency


def lem1(discretized_dataset, attitude, consistency, write_file_name):
	A = discretized_dataset[1:,:-1]
	attributes = discretized_dataset[0, :-1]
	single_global_covering = {}
	all_rows = list(range(A.shape[0]))
	all_rows = [x+1 for x in all_rows]

	for key in attitude:
		print key
		single_global_covering[key] = {}


		for key1 in attitude[key]:
			conceptual_var = list()
			remaining = list()
			conceptual_var = attitude[key][key1]
			remaining = [x for x in all_rows if x not in conceptual_var]
			conceptual_var = [conceptual_var, remaining]
			print 'conceptual variable: ',conceptual_var

			index_remove = list()
			condition = list()
			for index in range(A.shape[1]):
				temp = np.delete(A, [index] + index_remove, 1)

				temp1 = list()
				for row1 in temp:
					index1 = 1
					selected_index = list()
					for row2 in temp:
						if str(row1) == str(row2):
							selected_index.extend([index1])
						index1 = index1 + 1
					temp1.append(selected_index)

				temp1 = [x for n, x in enumerate(temp1) if x not in temp1[:n]]
				print 'linear dropping condition: ',temp1

				if [] in conceptual_var:
					print 'conceptual variable is empty'
				else:
					non_consistency = 0
					for item1 in temp1:
						issubset = False
						for item2 in conceptual_var:
							if set(item1) <= set(item2):
								issubset = True
						if not issubset:
							non_consistency += 1
					if non_consistency is not 0:
						condition.append(attributes[index])
					else:
						index_remove.append(index)

			print 'condition: ',condition
			if key1 is 'original':
				single_global_covering[key] = condition
			else:
				single_global_covering[key][key1] = condition

	# now create rule sets for single global coverings
	print '\n',single_global_covering,'\n'
	matrix = list()

	if consistency:
		file = open(write_file_name+'.possible.txt', 'w')
		file.write('! possible rule set is not shown since it is identical with the certain rule set')
		file.close()

		file = open(write_file_name+'.certain.txt', 'w')

		for key in single_global_covering:
			indexes = list()
			for item in single_global_covering[key]:
				index = np.where(discretized_dataset[0,:] == item)[0]
				indexes.extend(index)

			matrix = discretized_dataset[np.where(discretized_dataset[:,-1] == key)]
			matrix = np.vstack((discretized_dataset[0,:], matrix))
			matrix = matrix[:,indexes]
			title = matrix[0]
			matrix = np.delete(matrix, 0, axis=0)
			unique_matrix = np.vstack({tuple(row) for row in matrix})


			index = len(title)
			for row in unique_matrix:
				for x in range(index):
					if x == index-1:
						print '( {0} {1} ) => ( Attitude {2} ) '.format(title[x], row[x], key)
						file.write('( {0} {1} ) => ( Attitude {2} ) \n'.format(title[x], row[x], key))
					else:
						print '( {0} {1} ) & '.format(title[x], row[x]),
						file.write('( {0} {1} ) & '.format(title[x], row[x]))
			file.write('\n')

		file.close()

	else:
		certain_rule = {}
		possible_rule = {}
		for key in single_global_covering:
			certain_rule[key] = single_global_covering[key]['lower_bound']
			possible_rule[key] = single_global_covering[key]['upper_bound']


		file = open(write_file_name+'.certain.txt', 'w')
		for key in certain_rule:
			indexes = list()
			for item in certain_rule[key]:
				index = np.where(discretized_dataset[0,:] == item)[0]
				indexes.extend(index)

			matrix = discretized_dataset[np.where(discretized_dataset[:,-1] == key)]
			matrix = np.vstack((discretized_dataset[0,:], matrix))
			matrix = matrix[:,indexes]
			title = matrix[0]
			matrix = np.delete(matrix, 0, axis=0)
			unique_matrix = np.vstack({tuple(row) for row in matrix})


			index = len(title)
			for row in unique_matrix:
				for x in range(index):
					if x == index-1:
						print '( {0} {1} ) => ( Attitude {2} ) '.format(title[x], row[x], key)
						file.write('( {0} {1} ) => ( Attitude {2} ) \n'.format(title[x], row[x], key))
					else:
						print '( {0} {1} ) & '.format(title[x], row[x]),
						file.write('( {0} {1} ) & '.format(title[x], row[x]))
			file.write('\n')

		file.close()

		file = open(write_file_name+'.possible.txt', 'w')
		for key in possible_rule:
			indexes = list()
			for item in possible_rule[key]:
				index = np.where(discretized_dataset[0,:] == item)[0]
				indexes.extend(index)

			matrix = discretized_dataset[np.where(discretized_dataset[:,-1] == key)]
			matrix = np.vstack((discretized_dataset[0,:], matrix))
			matrix = matrix[:,indexes]
			title = matrix[0]
			matrix = np.delete(matrix, 0, axis=0)
			unique_matrix = np.vstack({tuple(row) for row in matrix})


			index = len(title)
			for row in unique_matrix:
				for x in range(index):
					if x == index-1:
						print '( {0} {1} ) => ( Attitude {2} ) '.format(title[x], row[x], key)
						file.write('( {0} {1} ) => ( Attitude {2} ) \n'.format(title[x], row[x], key))
					else:
						print '( {0} {1} ) & '.format(title[x], row[x]),
						file.write('( {0} {1} ) & '.format(title[x], row[x]))
			file.write('\n')

		file.close()


def main():
	# read_file_name, write_file_name = file_reader()
	dataset = parsing('test2.txt')
	# check if the data set needs discretization or not
	if '..' in ''.join(dataset[1]):
		print '\nno need for discretization\n'
	else:
		print '\ndata needs discretization\n'
		dataset = discretization(dataset)

	# proceed to the LEM1 algorithm after preprocessing all the data
	attitude, consistency = bound_calc(dataset)
	lem1(dataset, attitude, consistency, 'hello')


if __name__ == "__main__":
	main()
