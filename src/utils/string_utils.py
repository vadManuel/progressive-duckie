# return ordinal number of a number
def ordinal_number(number):
	ordinal = __ordinal_number(number)
	return f'{number}{ordinal}'

def __ordinal_number(number):
	if number % 100 // 10 == 1:
		return 'th'
	else:
		if number % 10 == 1:
			return 'st'
		elif number % 10 == 2:
			return 'nd'
		elif number % 10 == 3:
			return 'rd'
		else:
			return 'th'
