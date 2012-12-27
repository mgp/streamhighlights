EMPTY = '/static/star-empty-light.png'
EMPTY_HOVER = '/static/star-empty-dark.png'
FULL = '/static/star-full-dark.png'
FULL_HOVER = '/static/star-full-light.png'

requestInProgress = false
starImage = $("TODO")

toggleStarSucceeded = (data, textStatus, jqXHR) ->
	requestInProgress = false
	return

toggleStarFailed = (jqXHR, textStatus, errorThrown) ->
	requestInProgress = false
	switch starImage.attr 'src'
		when EMPTY then starImage.attr 'src', FULL
		when FULL then starImage.attr 'src', EMPTY
	return

toggleStar = (url, starred) ->
	settings =
		type: 'POST'
		url: 'TODO'
		data:
			starred: starred
		success: toggleStarSucceeded
		error: toggleStarFailed
		dataType: 'json'
	$.ajax settings
	return

starImage
	.mouseenter ->
		switch starImage.attr 'src'
			when EMPTY then starImage.attr 'src', EMPTY_HOVER
			when FULL then starImage.attr 'src', FULL_HOVER 
		return
	.mouseleave ->
		switch starImage.attr 'src'
			when FULL_HOVER then starImage.attr 'src', FULL
			when EMPTY_HOVER then starImage.attr 'src', EMPTY
		return
	.click ->
		return if requestInProgress
		switch starImage.attr 'src'
			when EMPTY_HOVER
				toggleStar 'TODO', true
				starImage.attr 'src', FULL
			when FULL_HOVER
				toggleStar 'TODO', false
				starImage.attr 'src', EMPTY
		requestInProgress = true
		return

