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
	countryOffsetMinutesMap = $('#time-zone').data('countryOffsetMinutesMap')[e.val]
	timeZoneSelect.append $ '<option></option>'
	$.each countryOffsetMinutesMap, (key, value) ->
		timeZoneSelect.append $('<option></option>').val(value[0]).html(key)
		return
	resetTimeZone()
	return

