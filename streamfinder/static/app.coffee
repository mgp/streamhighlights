EMPTY = '/static/star-empty-light.png'
EMPTY_HOVER = '/static/star-empty-dark.png'
FULL = '/static/star-full-dark.png'
FULL_HOVER = '/static/star-full-light.png'

requestInProgress = false

adjustCount = (starImg, amount) ->
	# Change the number of stars.
	countSpan = starImg.siblings "span"
	count = parseInt countSpan.text()
	count += amount
	countSpan.text count
	# Toggle the text color.
	countsDiv = starImg.closest "div.counts"
	countsDiv.toggleClass "selected"
	return

toggleStarSucceeded = (data, textStatus, jqXHR) ->
	requestInProgress = false
	return

toggleStarFailed = (starImg) ->
	switch starImg.attr 'src'
		when EMPTY
			starImg.attr 'src', FULL
			adjustCount starImg, +1
		when FULL
			starImg.attr 'src', EMPTY
			adjustCount starImg, -1
	requestInProgress = false
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
	requestInProgress = true
	starImg = $(this)
	switch starImg.attr 'src'
		when EMPTY_HOVER, EMPTY
			toggleStar starImg, true
			starImg.attr 'src', FULL
			adjustCount starImg, +1
		when FULL_HOVER, FULL
			toggleStar starImg, false
			starImg.attr 'src', EMPTY
			adjustCount starImg, -1
	return

$.addStarRollover = (starImg) ->
	starImg
		.mouseenter(enterStar)
		.mouseleave(leaveStar)
		.click(clickStar)
	return

