from server import DATABASE


_SERVER_ = DATABASE()

print(_SERVER_.get_all_index())

#print(_SERVER_.get_all_document('raonhanh365')['hits']['hits'])

print(_SERVER_.count_document('raonhanh'))
print("===================================")
print(_SERVER_.count_document('timviec365'))
print("===================================")
print(_SERVER_.count_document('raonhanh365'))