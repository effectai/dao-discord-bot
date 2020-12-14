from modules.eos import calculate_dao_rank, signed_constitution

assert signed_constitution('terry.efx')
assert signed_constitution('4carpfishing')
assert not signed_constitution('terry.x')

assert calculate_dao_rank('11mrmarian11') == 0
assert calculate_dao_rank('4mont1me1111') == 1
assert calculate_dao_rank('1yuricordova') == 2
assert calculate_dao_rank('alansss11111') == 3
assert calculate_dao_rank('bjjgray12345') == 4
assert calculate_dao_rank('breekean2222') == 5
assert calculate_dao_rank('djstrikanova') == 6
assert calculate_dao_rank('huckleberry2') == 7
assert calculate_dao_rank('hakf355store') == 8

print('Tests cleared')
