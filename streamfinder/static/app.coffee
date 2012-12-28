EMPTY = '/static/star-empty-light.png'
EMPTY_HOVER = '/static/star-empty-dark.png'
FULL = '/static/star-full-dark.png'
FULL_HOVER = '/static/star-full-light.png'

requestInProgress = false

toggleStarSucceeded = (data, textStatus, jqXHR) ->
	requestInProgress = false
	return

toggleStarFailed = (starImg) ->
	requestInProgress = false
	switch starImg.attr 'src'
		when EMPTY then starImg.attr 'src', FULL
		when FULL then starImg.attr 'src', EMPTY
	return

toggleStar = (starImg, starred) ->
	# Strip the query string, see http://stackoverflow.com/a/5817566/400717
	url = [location.protocol, '//', location.host, location.pathname].join('')
	settings =
		type: 'POST'
		url: url
		data:
			starred: starred
		success: toggleStarSucceeded
		error: (jqXHR, textStatus, errorThrown) ->
			toggleStarFailed(starImg)
		dataType: 'json'
	$.ajax settings
	return

enterStar = ->
	starImg = $(this)
	switch starImg.attr 'src'
		when EMPTY then starImg.attr 'src', EMPTY_HOVER
		when FULL then starImg.attr 'src', FULL_HOVER 
	return

leaveStar = ->
	starImg = $(this)
	switch starImg.attr 'src'
		when FULL_HOVER then starImg.attr 'src', FULL
		when EMPTY_HOVER then starImg.attr 'src', EMPTY
	return

clickStar = ->
	return if requestInProgress
	starImg = $(this)
	switch starImg.attr 'src'
		when EMPTY_HOVER
			toggleStar starImg, true
			starImg.attr 'src', FULL
		when FULL_HOVER
			toggleStar starImg, false
			starImg.attr 'src', EMPTY
	requestInProgress = true
	return

$.addStarRollover = (starImg) ->
	starImg
		.mouseenter(enterStar)
		.mouseleave(leaveStar)
		.click(clickStar)
	return

