$('#time-format > select').select2 {
	width: '600px',
	placeholder: 'Choose a time format',
}

countrySelect = $('#country > select')
countrySelect.select2 {
	width: '600px',
	placeholder: 'Choose a country',
}

timeZoneSelect = $('#time-zone > select')
resetTimeZone = ->
	timeZoneSelect.select2 {
		width: '600px',
		placeholder: 'Choose a time zone',
	}
	return
resetTimeZone()

replaceDash = (s) ->
	return s.replace "-", "&ndash;"

countrySelect.on 'change', (e) ->
	countryOffsetMinutes = $('#time-zone').data('countryOffsetMinutesMap')[e.val]
	displayedOffsetMap = $('#time-zone').data 'displayedOffsetMap'

	timeZoneSelect.empty()
	timeZoneSelect.append $ '<option></option>'
	$.each countryOffsetMinutes, (index, element) ->
		name = element[0]
		value = element[1]
		offset = displayedOffsetMap[element[2]]
		
		text = '(' + replaceDash(offset[0]) + ') ' + replaceDash(name)
		timeZoneSelect.append $('<option></option>').val(value).html(text)
		return
	resetTimeZone()
	return

