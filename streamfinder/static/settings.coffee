$('#time-format > select').select2 {
	width: '500px',
	placeholder: 'Choose a time format',
}

countrySelect = $('#country > select')
countrySelect.select2 {
	width: '500px',
	placeholder: 'Choose a country',
}

timeZoneSelect = $('#time-zone > select')
resetTimeZone = ->
	timeZoneSelect.select2 {
		width: '500px',
		placeholder: 'Choose a time zone',
	}
	return
resetTimeZone()

countrySelect.on 'change', (e) ->
	timeZoneSelect.empty()
	timeZoneMap = $('#time-zone').data('timeZoneMap')[e.val]
	timeZoneSelect.append $ '<option></option>'
	$.each timeZoneMap, (key, value) ->
		timeZoneSelect.append $('<option></option>').val(value).html(key)
		return
	resetTimeZone()
	return

