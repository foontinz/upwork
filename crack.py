import random
import string
import timeit

password = {"akido": "suzzuya"}
allowed_chars = string.ascii_lowercase + " "


def check_pass(login, guess):
    return password[login] == guess


def gen_str(length):
    return ''.join(random.choices(allowed_chars, k=length))


def crack(login, max_length):
    list_time_of_check = []
    for length in range(max_length):
        i_time = timeit.repeat(stmt='check_pass(login,guess)',
                               setup=f'login={login!r}; guess=gen_str({length!r})',
                               globals=globals(),
                               repeat=10)
        list_time_of_check.append(min(i_time))
    print(max(list_time_of_check), list_time_of_check.index(max(list_time_of_check)) + 1)


crack("akido", 16)
