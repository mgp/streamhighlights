# Initialize the time format selector with Select2.
timeFormatSelect = $('#time-format > select')
timeFormatSelect.select2 {
	width: '600px',
	placeholder: 'Choose a time format',
}

# Called when the time format is changed, toggles the visibility of the 12-hour
# and 24-hour times appropriately.
timeFormatSelect.change ->
	selectedFormat = $('option:selected', this).val()
	times12Hour = $('#time-compare div.format-12-hour')
	times24Hour = $('#time-compare div.format-24-hour')
	if selectedFormat == '12_hour'
		times12Hour.show()
		times24Hour.hide()
	else
		times12Hour.hide()
		times24Hour.show()
	return

# Initialize the country selector with Select2.
countrySelect = $('#country > select')
countrySelect.select2 {
	width: '600px',
	placeholder: 'Choose a country',
}

# The containing div for the client's 12-hour and 24-hour times.
clientTime = $('#client-time')
clientTime12Hour = $('div.format-12-hour', clientTime)
clientTime24Hour = $('div.format-24-hour', clientTime)

timeZoneSelect = $('#time-zone > select')
# Initializes the time zone selector with Select2. Must also be called after a
# new country is chosen, or else Select2 will not display the updated list of
# time zones.
resetTimeZone = ->
	timeZoneSelect.select2 {
		width: '600px',
		placeholder: 'Choose a time zone',
	}
	return
resetTimeZone()

# Replaces the dash with a longer dash more visible with LeagueGothic.
replaceDash = (s) ->
	return s.replace "-", "&ndash;"

# Called when a different country is selected, and the list of time zone options
# must be updated.
countrySelect.on 'change', (e) ->
	countryOffsetMinutes = $('#time-zone').data('countryOffsetMinutesMap')[e.val]
	displayedOffsetMap = $('#time-zone').data 'displayedOffsetMap'

	# Remove all previous time zone options.
	timeZoneSelect.empty()
	# Add the placeholder option again.
	timeZoneSelect.append $ '<option></option>'
	$.each countryOffsetMinutes, (index, element) ->
		# Get the name and value for this time zone.
		name = element[0]
		value = element[1]
		# Get the offset tuple; the first element is the offset format for display.
		offset = displayedOffsetMap[element[2]]
		
		# Create and append the option for this time zone.
		text = '(' + replaceDash(offset[0]) + ') ' + replaceDash(name)
		option = $('<option></option>').data('offset', offset).val(value).html(text)
		timeZoneSelect.append option
		return
	
	resetTimeZone()
	# A new country was chosen, so no time zone is chosen yet.
	clientTime.hide()
	clientTime12Hour.empty()
	clientTime24Hour.empty()
	return

# Called when a time zone is selected.
timeZoneSelect.change ->
	# Display the 12-hour and 24-hour times for this offset.
	offset = $('option:selected', this).data 'offset'
	clientTime12Hour.text(offset[1])
	clientTime24Hour.text(offset[2])
	# This may be the first time zone chosen after choosing a new country.
	clientTime.show()
	return

