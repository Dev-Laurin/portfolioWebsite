#MySQL Query Functions 

def getPostTags(cursor, id):
	#get all tags associated with this post 
	cursor.callproc('getPostTags', [id])
	postTags = cursor.fetchall()

	pp = []
	for p in postTags: 
		pp.append(p[0])
	return pp 

