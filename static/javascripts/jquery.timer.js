function StartTimer(SecondsTrackedID, TimerStateID, TimerID) {
	timeTaken = document.getElementById(SecondsTrackedID).value;
	document.getElementById(TimerStateID).value = "start";
	Timer(SecondsTrackedID, TimerStateID, TimerID);
}

function StopTimer(TimerStateID) {
	document.getElementById(TimerStateID).value = "stop";
}

function ResetTimer(SecondsTrackedID, TimerStateID, TimerID) {
	document.getElementById(SecondsTrackedID).value = "0";
	timeTaken = document.getElementById(SecondsTrackedID).value;
	document.getElementById(TimerStateID).value = "reset";
	Timer(SecondsTrackedID, TimerStateID, TimerID);
}

function Timer(SecondsTrackedID, TimerStateID, TimerID) {
	var timeTaken = document.getElementById(SecondsTrackedID).value;
	timeTaken = (timeTaken == "") ? 0 : parseInt(timeTaken);
	minutes = (timeTaken > 60) ? parseInt(parseInt(timeTaken) / 60) : 0;
	seconds = (timeTaken > 60) ? (timeTaken % 60) : timeTaken;

	min_1 = (minutes > 9) ? parseInt(minutes / 10) : 0;
	min_2 = (minutes > 9) ? (minutes % 10) : minutes;
	sec_1 = (seconds > 9) ? parseInt(seconds / 10) : 0;
	sec_2 = (seconds > 9) ? (seconds % 10) : seconds;

	if (document.getElementById(TimerStateID).value == "start") {
		document.getElementById(TimerID).innerHTML = '<span class="DigitSprite'
				+ ' Digit_'
				+ min_1
				+ '" id="Min_1"></span><span class="DigitSprite'
				+ ' Digit_'
				+ min_2
				+ '" id="Min_2"></span><span class="DigitSprite" id="Separator" style="background-position: 0px -203px"></span><span class="DigitSprite'
				+ ' Digit_' + sec_1
				+ '" id="Sec_1"></span><span class="DigitSprite' + ' Digit_'
				+ sec_2 + '" id="Sec_2"></span>'
		setTimeout("Timer('" + SecondsTrackedID + "','" + TimerStateID + "', '"
				+ TimerID + "')", 1000);
		document.getElementById(SecondsTrackedID).value = timeTaken + 1;
	} else if (document.getElementById(TimerStateID).value == "reset") {
		document.getElementById(TimerID).innerHTML = '<span class="DigitSprite'
				+ ' Digit_'
				+ min_1
				+ '" id="Min_1"></span><span class="DigitSprite'
				+ ' Digit_'
				+ min_2
				+ '" id="Min_2"></span><span class="DigitSprite" id="Separator" style="background-position: 0px -203px"></span><span class="DigitSprite'
				+ ' Digit_' + sec_1
				+ '" id="Sec_1"></span><span class="DigitSprite' + ' Digit_'
				+ sec_2 + '" id="Sec_2"></span>'
	}

}

function TimeSpentTracker(SecondsSpentID) {
	var timeTaken = document.getElementById(SecondsSpentID).value;
	timeTaken = (timeTaken == "") ? 0 : parseInt(timeTaken);
	setTimeout("TimeSpentTracker('" + SecondsSpentID + "')", 1000);
	document.getElementById(SecondsSpentID).value = timeTaken + 1;
}